import os
import binascii
import pandas as pd
import sys
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='feature_extraction.log'
)
logger = logging.getLogger(__name__)

def initialize_worker():
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def hex_to_binary(hex_data):
    try:
        if hex_data is None or not isinstance(hex_data, str):
            logger.warning(f"Invalid hex data: {hex_data}")
            return None
            
        # Remove any whitespace or special characters
        hex_data = ''.join(c for c in hex_data if c.isalnum())
        
        if len(hex_data) % 2 != 0:
            hex_data = '0' + hex_data  # Pad with leading zero if odd length
            
        binary_data = bin(int(binascii.unhexlify(hex_data).hex(), 16))[2:]
        return binary_data.zfill(len(hex_data) * 4)
    except Exception as e:
        logger.error(f"Error converting hex to binary: {str(e)}")
        return None

def extract_features_batch(binary_data_list):
    # Add validation
    if not binary_data_list or all(x is None for x in binary_data_list):
        logger.error("No valid binary data in batch")
        return []

    import torch
    from o1_Acc_Feature_Extract import FeatureExtract

    # Set device for the current process
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    # Log batch information
    logger.debug(f"Processing batch with {len(binary_data_list)} items")

    features_list = [{} for _ in binary_data_list]

    # Extract all values from approximate_entropy_test
    print("Extracting approximate_entropy_test features...")
    approximate_entropy_results = FeatureExtract.approximate_entropy_test_batch(binary_data_list)
    for i, result in enumerate(approximate_entropy_results):
        if result is not None:
            features = {
                f"approximate_entropy_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result.items()
            }
            features_list[i].update(features)
        else:
            features_list[i]['approximate_entropy_error'] = 'Failed to compute approximate entropy.'

    # Extract all values from binary_matrix_rank_test_16 and binary_matrix_rank_test_32
    print("Extracting binary_matrix_rank_test_16 and binary_matrix_rank_test_32 features...")

    binary_matrix_rank_results_16 = FeatureExtract.binary_matrix_rank_test_batch_16(binary_data_list)
    binary_matrix_rank_results_32 = FeatureExtract.binary_matrix_rank_test_batch_32(binary_data_list)

    for i, (result_16, result_32) in enumerate(zip(binary_matrix_rank_results_16, binary_matrix_rank_results_32)):
        if result_16 is not None:
            features_list[i].update({
                f"binary_matrix_rank_16_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result_16.items()
            })
        else:
            features_list[i]['binary_matrix_rank_16_error'] = 'Failed to compute binary matrix rank.'

        if result_32 is not None:
            features_list[i].update({
                f"binary_matrix_rank_32_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result_32.items()
            })
        else:
            features_list[i]['binary_matrix_rank_32_error'] = 'Failed to compute binary matrix rank.'

    # Extract all values from cumulative_sums_test
    print("Extracting cumulative_sums_test features...")
    cumulative_sums_results = FeatureExtract.cumulative_sums_test_batch(binary_data_list)
    for i, result in enumerate(cumulative_sums_results):
        if result is not None:
            features_list[i].update({
                f"cumulative_sums_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result.items()
            })
        else:
            features_list[i]['cumulative_sums_error'] = 'Failed to compute cumulative sums.'

    # Extract all values from serial_test_and_extract_features
    print("Extracting serial_test_and_extract_features features...")
    serial_test_results = FeatureExtract.serial_test_and_extract_features_batch(binary_data_list)
    for i, result in enumerate(serial_test_results):
        if result is not None:
            features_list[i].update({
                f"serial_test_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result.items()
            })
        else:
            features_list[i]['serial_test_error'] = 'Failed to compute serial test.'

    # Extract all values from spectral_test
    print("Extracting spectral_test features...")
    spectral_test_results = FeatureExtract.spectral_test_batch(binary_data_list)
    for i, result in enumerate(spectral_test_results):
        if result is not None:
            features_list[i].update({
                f"spectral_test_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result.items()
            })
        else:
            features_list[i]['spectral_test_error'] = 'Failed to compute spectral test.'

    print("Extracting linear_complexity_test features...")
    linear_complexity_results = FeatureExtract.linear_complexity_test_batch(
        serial_binary_data_list=binary_data_list,
        block_size=128
    )
    for i, result in enumerate(linear_complexity_results):
        if i % 100 == 0 and i > 0:
            logging.debug(f"Processed {i} / {len(linear_complexity_results)} linear complexity tests.")
        
        if result is not None and 'error' not in result:
            features_list[i].update({
                f"linear_complexity_{key}": value
                for key, value in result.items()
            })
        else:
            features_list[i]['linear_complexity_error'] = 'Failed to compute linear complexity.'

    # Extract all values from longest_one_block_test
    print("Extracting longest_one_block_test features...")
    longest_one_block_results = FeatureExtract.longest_one_block_test_batch(binary_data_list)
    for i, result in enumerate(longest_one_block_results):
        if result is not None:
            features_list[i].update({
                f"longest_one_block_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result.items()
            })
        else:
            features_list[i]['longest_one_block_error'] = 'Failed to compute longest one block.'

    # Extract all values from block_frequency_multiple_sizes
    print("Extracting block_frequency_multiple_sizes features...")
    block_freq_results = FeatureExtract.block_frequency_multiple_sizes_batch(binary_data_list)
    for i, result_list in enumerate(block_freq_results):
        if result_list is not None:
            for result in result_list:
                features_list[i].update({
                    key: value.tolist() if isinstance(value, torch.Tensor) else value 
                    for key, value in result.items()
                })
        else:
            features_list[i]['block_frequency_multiple_sizes_error'] = 'Failed to compute block frequency multiple sizes.'

    # Extract all values from statistical_test
    print("Extracting statistical_test features...")
    statistical_test_results = FeatureExtract.statistical_test_batch(binary_data_list)
    for i, result in enumerate(statistical_test_results):
        if result is not None:
            features_list[i].update({
                f"statistical_test_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result.items()
            })
        else:
            features_list[i]['statistical_test_error'] = 'Failed to compute statistical test.'

    # Extract all values from extract_run_test_features
    print("Extracting extract_run_test_features features...")
    try:
        run_test_results = FeatureExtract.extract_run_test_features_batch(binary_data_list, verbose=False)
        for i, result in enumerate(run_test_results):
            if result is not None:
                features_list[i].update({
                    f"run_test_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                    for key, value in result.items()
                })
            else:
                features_list[i]['run_test_error'] = 'Failed to compute run test.'
    except Exception as e:
        print(f"Error processing batch: {e}")

    # Extract all values from monobit_test
    print("Extracting monobit_test features...")
    monobit_results = FeatureExtract.monobit_test_batch(binary_data_list)
    for i, result in enumerate(monobit_results):
        if result is not None:
            features_list[i].update({
                f"monobit_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result.items()
            })
        else:
            features_list[i]['monobit_error'] = 'Failed to compute monobit test.'

    # Extract all values from spectral_test_on_blocks
    print("Extracting spectral_test_on_blocks features...")
    spectral_test_blocks_results = FeatureExtract.spectral_test_on_blocks_batch(binary_data_list, block_size=128)
    for i, result in enumerate(spectral_test_blocks_results):
        if result is not None:
            features_list[i].update({
                f"spectral_test_blocks_{key}": value.tolist() if isinstance(value, torch.Tensor) else value 
                for key, value in result.items()
            })
        else:
            features_list[i]['spectral_test_blocks_error'] = 'Failed to compute spectral test on blocks.'

    return features_list


def process_files_batch(file_paths, labels):
    import torch
    
    # Initialize torch in this process
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    binary_data_list = []
    hex_data_list = []
    
    logger.debug(f"Processing {len(file_paths)} files")
    
    for idx, file_path in enumerate(file_paths):
        try:
            with open(file_path, 'r') as file:
                hex_data = file.read().strip()
                if hex_data is not None:
                    logger.debug(f"File {file_path}: Hex data length = {len(hex_data)}")
                else:
                    logger.warning(f"File {file_path}: Hex data is None")
                    hex_data_list.append(None)
                    binary_data_list.append(None)
                    continue
                    
                binary_data = hex_to_binary(hex_data)
                
                if binary_data:
                    logger.debug(f"File {file_path}: Binary data length = {len(binary_data)}")
                    binary_data_list.append(binary_data)
                else:
                    logger.warning(f"File {file_path}: Failed to convert hex to binary")
                    binary_data_list.append(None)
                hex_data_list.append(hex_data)
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            hex_data_list.append(None)
            binary_data_list.append(None)

    # Validate batch before processing
    if all(x is None for x in binary_data_list):
        logger.error("All files in batch failed to process")
        return []

    print(f"Processing batch of {len(file_paths)} files...")
    features_list = extract_features_batch(binary_data_list)
    for i, features in enumerate(features_list):
        if binary_data_list[i]:
            features['label'] = labels[i]
            features['file_name'] = os.path.basename(file_paths[i])  # Add file name
            features['cipherText'] = hex_data_list[i]  # Add hex data
        else:
            features['label'] = 'error'
            features['file_error'] = 'Failed to read or convert file.'
            features['file_name'] = os.path.basename(file_paths[i])  # Add file name
            features['cipherText'] = hex_data_list[i]  # Add hex data

    return features_list

def terminate_processes():
    for p in multiprocessing.active_children():
        p.terminate()

def load_data(dataset_folder, batch_size=32, max_workers=None, output_file="intermediate_results.csv"):
    data = []
    file_paths = []
    labels = []

    # Add error handling for dataset folder
    if not os.path.exists(dataset_folder):
        logger.error(f"Dataset folder not found: {dataset_folder}")
        raise FileNotFoundError(f"Dataset folder not found: {dataset_folder}")

    folder_list = os.listdir(dataset_folder)
    for label in tqdm(folder_list, desc="Processing folders"):
        folder_path = os.path.join(dataset_folder, label)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                file_paths.append(file_path)
                labels.append(label)

    batches = [
        (file_paths[i:i + batch_size], labels[i:i + batch_size])
        for i in range(0, len(file_paths), batch_size)
    ]

    if not max_workers:
        total_cores = multiprocessing.cpu_count()
        max_workers = max(1, int(total_cores * 0.80))  # Use 80% of available cores
        print("max number of workers: ", max_workers)

    executor = None
    try:
        executor = ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=initialize_worker
        )
        futures = {
            executor.submit(process_files_batch, batch_fp, batch_lbl): (batch_fp, batch_lbl)
            for batch_fp, batch_lbl in batches
        }

        # Initialize counters and flags
        files_processed = 0
        save_interval = 200  # Save every 100 files
        is_first_write = not os.path.exists(output_file)

        # Buffer to hold intermediate data
        buffer_data = []

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing batches"):
            try:
                batch_data = future.result()
                if batch_data is not None:
                    buffer_data.extend(batch_data)
                    files_processed += len(batch_data)
                else:
                    logger.warning("Received None batch_data from future")
                    continue

                # Check if it's time to save
                if files_processed >= save_interval:
                    if buffer_data:  # Add check for empty buffer
                        df = pd.DataFrame(buffer_data)

                        # Determine the write mode and whether to write headers
                        if is_first_write:
                            df.to_csv(output_file, mode='w', index=False, header=True)
                            is_first_write = False
                            print(f"Saved intermediate results to {output_file} after processing {files_processed} files.")
                        else:
                            df.to_csv(output_file, mode='a', index=False, header=False)
                            print(f"Appended intermediate results to {output_file} after processing {files_processed} files.")

                        # Reset the buffer and counter
                        buffer_data = []
                        files_processed = 0

            except Exception as e:
                print(f"Error processing batch: {e}")
                executor.shutdown(wait=False, cancel_futures=True)
                terminate_processes()
                raise

        # After all batches are processed, save any remaining data
        if buffer_data:
            df = pd.DataFrame(buffer_data)
            if is_first_write:
                df.to_csv(output_file, mode='w', index=False, header=True)
                print(f"Saved remaining data to {output_file}.")
            else:
                df.to_csv(output_file, mode='a', index=False, header=False)
                print(f"Appended remaining data to {output_file}.")

    except (KeyboardInterrupt, SystemExit):
        print("Interrupt detected, shutting down executor...")
        if executor:
            executor.shutdown(wait=False, cancel_futures=True)
        terminate_processes()
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if executor:
            executor.shutdown(wait=False, cancel_futures=True)
        terminate_processes()
        load_data(dataset_folder, batch_size=4, max_workers=2, output_file=output_file)
        raise
    finally:
        if executor:
            executor.shutdown(wait=False, cancel_futures=True)
        terminate_processes()

    return pd.DataFrame(buffer_data)  # Return any remaining data

def save_to_csv(df, output_file):
    df.to_csv(output_file, index=False)

def main(input_file, output_file):
    with open(input_file, 'r') as file:
        hex_data = file.read().strip()
    
    binary_data = hex_to_binary(hex_data)
    if binary_data is None:
        print("Failed to convert hex to binary.")
        return
    
    features_list = extract_features_batch([binary_data])
    df = pd.DataFrame(features_list)
    df.to_csv(output_file, index=False)
    print(f"Features extracted and saved to {output_file}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python o1_Extract.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    main(input_file, output_file)