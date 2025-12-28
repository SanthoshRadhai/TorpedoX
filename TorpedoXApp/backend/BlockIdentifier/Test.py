import pandas as pd
import pickle
import os
import subprocess
import sys
import numpy as np

def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Step 1: Get the file path of the ciphertext from the command line argument
    if len(sys.argv) != 2:
        # print("Usage: python Test.py <ciphertext_file_path>")

        return
    
    file_path = sys.argv[1]

    # Step 2: Ensure the file exists
    if not os.path.exists(file_path):
        print(f"Error: The specified file {file_path} does not exist.")
        return

    # Step 3: Read the ciphertext from the file
    try:
        with open(file_path, "r") as file:
            ciphertext = file.read()
    except Exception as e:
        print(f"Error reading the ciphertext file: {e}")
        return
    
    # Remove all spaces from the ciphertext
    ciphertext = ciphertext.replace(" ", "")

    # Step 4: Write the ciphertext to a temporary file in the same directory as the script
    temp_filename = os.path.join(script_dir, "temp_input.txt")
    try:
        with open(temp_filename, "w") as temp_file:
            temp_file.write(ciphertext)
    except Exception as e:
        print(f"Error writing to temporary file: {e}")
        return

    # Step 5: Run the feature extraction script (o1_Extract.py)
    feature_filename = os.path.join(script_dir, "feature.csv")
    log_filename = os.path.join(script_dir, "feature_extraction.log")

    # Ensure the script runs in the directory where Test.py exists
    os.chdir(script_dir)

    try:
        with open(log_filename, 'w') as log_file:
            subprocess.run(
                ["python", "o1_Extract.py", temp_filename, feature_filename],
                check=True,
                stdout=log_file,  # Redirect stdout to log file
                stderr=subprocess.STDOUT  # Redirect stderr to stdout
            )
        print("Feature extraction completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing feature extraction: {e.stderr}")
        return
    except Exception as e:
        print(f"Error executing feature extraction: {e}")
        return

    # Step 6: Read the feature.csv file
    try:
        features = pd.read_csv(feature_filename)
        # print("Features extracted:")
        # print(features.columns)
    except FileNotFoundError:
        print(f"Error: {feature_filename} not found.")
        return
    except Exception as e:
        print(f"Error reading the feature file: {e}")
        return

    # Step 7: Load the RandomForest model
    model_filename = "random_forest_model.pkl"
    try:
        with open(model_filename, "rb") as model_file:
            model = pickle.load(model_file)
        print("Model loaded successfully.")
    except FileNotFoundError:
        print(f"Error: {model_filename} not found.")
        return
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Step 8: Load the Label Encoder
    label_encoder_filename = "label_encoder.pkl"
    try:
        with open(label_encoder_filename, "rb") as le_file:
            label_encoder = pickle.load(le_file)
        print("Label Encoder loaded successfully.")
    except FileNotFoundError:
        print(f"Error: {label_encoder_filename} not found.")
        return
    except Exception as e:
        print(f"Error loading Label Encoder: {e}")
        return

    # Step 9: Filter the features to match those used during training
    model_features = model.feature_names_in_
    # print(f"Model expected features: {model_features}")

    # Check if the features match the model's required features
    missing_features = [feature for feature in model_features if feature not in features.columns]
    if missing_features:
        print(f"Error: Missing features - {missing_features}")
        return
    features = features[model_features]

    # Debugging: Print features DataFrame and its data types
    # print("Features DataFrame:")
    # print(features)
    # print(features.dtypes)

    # Step 10: Convert data types to numeric
    features = features.apply(pd.to_numeric, errors='coerce')

    # Step 11: Handle missing values by filling with zeroes
    # print("Missing values per feature:")
    # print(features.isnull().sum())
    features = features.fillna(0)

    # Step 12: Make predictions
    try:
        prediction = model.predict(features)
        if isinstance(prediction, np.ndarray):
            prediction = prediction[0]  # If it's an array, take the first value.
        prediction_label = label_encoder.inverse_transform([prediction])  # Ensure proper format
        print(f"Prediction: {prediction_label[0]}")
    except Exception as e:
        print(f"Error making prediction: {e}")

if __name__ == "__main__":
    main()
