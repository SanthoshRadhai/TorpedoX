import pandas as pd
import pickle
import os
import subprocess

def main():
    # Step 1: Get the file path of the ciphertext from the user
    file_path = input("Enter the file path of the ciphertext: ")
    
    # Step 2: Read the ciphertext from the file
    with open(file_path, "r") as file:
        ciphertext = file.read()
    
    # Remove all spaces from the ciphertext
    ciphertext = ciphertext.replace(" ", "")

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
    
    # Debugging: Print features DataFrame and its data types
    print(features)
    print(features.dtypes)
    
    # Convert data types to numeric
    features = features.apply(pd.to_numeric, errors='coerce')
    
    # Handle missing values
    print(features.isnull().sum())
    features = features.fillna(0)
    
    # Step 9: Make predictions
    prediction = model.predict(features)

    if prediction == 0:
        print("Prediction: ChaCha20")
    else:
        print("Prediction: Salsa20")

if __name__ == "__main__":
    main()