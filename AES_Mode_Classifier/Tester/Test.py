import pandas as pd
import pickle
import os
import subprocess

def main():
    # Step 1: Take ciphertext file input from user
    ciphertext_file = input("Enter the path to the ciphertext file: ")

    # Step 2: Read the ciphertext from the file
    with open(ciphertext_file, "r") as file:
        ciphertext = file.read()

    # Step 3: Write the ciphertext to a temporary file
    temp_filename = "temp_input.txt"
    with open(temp_filename, "w") as temp_file:
        temp_file.write(ciphertext)
    
    # Step 4: Run the o1_Extract.py script
    feature_filename = "feature.csv"
    subprocess.run(["python", "o1_Extract.py", temp_filename, feature_filename], check=True)
    
    # Step 5: Read the feature.csv file
    features = pd.read_csv(feature_filename)
    print(features.columns)
    
    # Step 6: Load the RandomForest model
    model_filename = "random_forest_model.pkl"
    with open(model_filename, "rb") as model_file:
        model = pickle.load(model_file)
    
    # Step 7: Filter the features to match those used during training
    model_features = model.feature_names_in_
    print(model_features)
    features = features[model_features]
    
    # Step 8: Check for missing features
    missing_features = [feature for feature in model_features if feature not in features.columns]
    print("Missing features:", missing_features)
    
    # Step 9: Make a prediction
    prediction = model.predict(features)
    
    # Step 10: Output the result
    if prediction[0] == 1:
        print("The ciphertext is classified as: CBC")
    else:
        print("The ciphertext is classified as: ECB")
    
    # Cleanup: Remove the temporary file
    os.remove(temp_filename)

if __name__ == "__main__":
    main()