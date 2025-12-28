import pandas as pd
import pickle
import os
import subprocess

def main():
    # Step 1: Get the ciphertext file path from the user
    ciphertext_file = input("Enter the path to the ciphertext file: ")

    # Step 2: Read the ciphertext from the file
    with open(ciphertext_file, "r") as file:
        ciphertext = file.read()
    
    # Step 3: Remove all spaces from the ciphertext
    ciphertext = ciphertext.replace(" ", "")
    print(len(ciphertext))
    
    # Step 4: Ensure the ciphertext is a valid hexadecimal string
    if all(c in '0123456789abcdefABCDEF' for c in ciphertext):
        # Step 5: Ensure the ciphertext has an even number of characters
        if len(ciphertext) % 2 != 0:
            ciphertext = '0' + ciphertext
        
        # Step 6: Write the ciphertext to a temporary file
        temp_filename = "temp_input.txt"
        with open(temp_filename, "w") as temp_file:
            temp_file.write(ciphertext)
        
        # Step 7: Run the FeatureExtract.py script
        feature_filename = "feature.csv"
        subprocess.run(["python", "FeatureExtract.py", temp_filename, feature_filename], check=True)
        
        # Step 8: Read the feature.csv file
        features = pd.read_csv(feature_filename)
        
        # Step 9: Load the RandomForest model
        model_filename = "random_forest_model.pkl"
        with open(model_filename, "rb") as model_file:
            model = pickle.load(model_file)
        
        # Step 10: Filter the features to match those used during training
        model_features = model.feature_names_in_
        features = features[model_features]
        
        # Step 11: Make a prediction
        prediction = model.predict(features)
        
        # Step 12: Output the result
        if prediction[0] == 1:
            print("The ciphertext is classified as: Symmetric")
        else:
            print("The ciphertext is classified as: Asymmetric")
    else:
        print("The provided ciphertext is not a valid hexadecimal string.")

if __name__ == "__main__":
    main()