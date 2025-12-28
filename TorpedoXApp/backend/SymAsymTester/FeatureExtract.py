from tqdm import tqdm
import os
import pandas as pd
import binascii
from FeatureClassGPUv1 import FeatureExtract  # Assuming FeatureExtract contains the methods

def hex_to_binary(hex_data):
    hex_data = hex_data.replace(" ", "")  # Remove spaces
    binary_data = bin(int(binascii.unhexlify(hex_data).hex(), 16))[2:]
    return binary_data.zfill(len(hex_data) * 4)

def extract_features(binary_data):
    features = {}
    
    # Extract all values from approximate_entropy_test
    approximate_entropy_results = FeatureExtract.approximate_entropy_test(binary_data)
    features.update({f"approximate_entropy_{key}": value for key, value in approximate_entropy_results.items()})
    
    # Extract all values from binary_matrix_rank_test
    binary_matrix_rank_results = FeatureExtract.binary_matrix_rank_test(binary_data)
    features.update({f"binary_matrix_rank_{key}": value for key, value in binary_matrix_rank_results.items()})
    
    # Extract all values from cumulative_sums_test
    cumulative_sums_results = FeatureExtract.cumulative_sums_test(binary_data)
    features.update({f"cumulative_sums_{key}": value for key, value in cumulative_sums_results.items()})
    
    # Extract all values from serial_test_and_extract_features
    serial_test_results = FeatureExtract.serial_test_and_extract_features(binary_data)
    features.update({f"serial_test_{key}": value for key, value in serial_test_results.items()})
    
    # Extract all values from spectral_test
    spectral_test_results = FeatureExtract.spectral_test(binary_data)
    features.update({f"spectral_test_{key}": value for key, value in spectral_test_results.items()})
    
    # Extract all values from linear_complexity_test
    linear_complexity_results = FeatureExtract.linear_complexity_test(binary_data)
    features.update({f"linear_complexity_{key}": value for key, value in linear_complexity_results.items()})
    
    # Extract all values from longest_one_block_test
    longest_one_block_results = FeatureExtract.longest_one_block_test(binary_data)
    features.update({f"longest_one_block_{key}": value for key, value in longest_one_block_results.items()})
    
    # Extract all values from block_frequency_multiple_sizes
    block_freq_results = FeatureExtract.block_frequency_multiple_sizes(binary_data)
    features.update(block_freq_results)
    
    # Extract all values from statistical_test
    statistical_test_results = FeatureExtract.statistical_test(binary_data)
    features.update({f"statistical_test_{key}": value for key, value in statistical_test_results.items()})
    
    # Extract all values from extract_run_test_features
    run_test_results = FeatureExtract.extract_run_test_features(binary_data)
    features.update({f"run_test_{key}": value for key, value in run_test_results.items()})
    
    # Extract all values from monobit_test
    monobit_results = FeatureExtract.monobit_test(binary_data)
    features.update({f"monobit_{key}": value for key, value in monobit_results.items()})
    
    # Extract all values from spectral_test_on_blocks
    spectral_test_blocks_results = FeatureExtract.spectral_test_on_blocks(binary_data, block_size=128)
    features.update({f"spectral_test_blocks_{key}": value for key, value in spectral_test_blocks_results.items()})
    
    return features

def load_data(dataset_folder):
    data = []
    labels = []
    folder_list = os.listdir(dataset_folder)
    for label in tqdm(folder_list, desc="Processing folders"):
        folder_path = os.path.join(dataset_folder, label)
        if os.path.isdir(folder_path):
            file_list = os.listdir(folder_path)
            for filename in tqdm(file_list, desc=f"Processing files in {label}", leave=False):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as file:
                    hex_data = file.read().strip()
                    binary_data = hex_to_binary(hex_data)
                    features = extract_features(binary_data)
                    features['label'] = label
                    data.append(features)
    return pd.DataFrame(data)

def save_to_csv(df, output_file):
    df.to_csv(output_file, index=False)

def process_single_file(file_path):
    with open(file_path, 'r') as file:
        hex_data = file.read().strip()
        binary_data = hex_to_binary(hex_data)
        features = extract_features(binary_data)
    return features

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python FeatureExtract.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    features = process_single_file(input_file)
    df = pd.DataFrame([features])
    save_to_csv(df, output_file)