import pandas as pd
import pickle
import subprocess
import os
import sys

def classify_ciphertext(ciphertext_file):
    # Get the absolute path of the script's current directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Read the ciphertext from the file
    with open(ciphertext_file, "r") as file:
        ciphertext = file.read()
    
    # Step 2: Remove all spaces from the ciphertext
    ciphertext = ciphertext.replace(" ", "")
    # print(f"Ciphertext length (after removing spaces): {len(ciphertext)}")

    # Step 3: Ensure the ciphertext is a valid hexadecimal string
    if all(c in '0123456789abcdefABCDEF' for c in ciphertext):
        # Step 4: Ensure the ciphertext has an even number of characters
        if len(ciphertext) % 2 != 0:
            ciphertext = '0' + ciphertext
        
        # Step 5: Write the ciphertext to a temporary file
        temp_filename = os.path.join(script_dir, "temp_input.txt")
        with open(temp_filename, "w") as temp_file:
            temp_file.write(ciphertext)
        
        # Step 6: Run the FeatureExtract.py script
        feature_filename = os.path.join(script_dir, "feature.csv")
        feature_extract_path = os.path.join(script_dir, "FeatureExtract.py")

        try:
            result = subprocess.run(
                ["python", feature_extract_path, temp_filename, feature_filename],
                check=True, capture_output=True, text=True
            )
            # print("Feature extraction completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error running FeatureExtract.py: {e.stderr}")
            sys.exit(1)
        
        # Step 7: Read the feature.csv file
        try:
            features = pd.read_csv(feature_filename)
        except FileNotFoundError:
            print("Error: feature.csv file not found.")
            sys.exit(1)

        # Step 8: Load the RandomForest model
        model_filename = os.path.join(script_dir, "random_forest_model.pkl")
        try:
            with open(model_filename, "rb") as model_file:
                model = pickle.load(model_file)
        except FileNotFoundError:
            print(f"Error: {model_filename} not found.")
            sys.exit(1)
        
        # Step 9: Filter the features to match those used during training
        model_features = model.feature_names_in_
        features = features[model_features]
        
        # Step 10: Make a prediction
        prediction = model.predict(features)
        
        # Step 11: Output the result
        # print(f"Predicted value: {prediction[0]}")  # Debug log
        if prediction[0] == 1:
            print("Symmetric")
        else:
            print("Asymmetric")

    else:
        print("The provided ciphertext is not a valid hexadecimal string.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python Test.py <ciphertext_file>")
        sys.exit(1)

    ciphertext_file = sys.argv[1]
    classify_ciphertext(ciphertext_file)
