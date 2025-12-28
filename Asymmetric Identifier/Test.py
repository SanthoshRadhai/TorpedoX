import pandas as pd
import joblib
import os
import subprocess
from sklearn.preprocessing import LabelEncoder

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
    print(f"Loading model from: {model_filename}")
    
    model = joblib.load(model_filename)
    
    # Step 7: Filter and reorder the features to match those used during training
    try:
        model_features = model.feature_names_in_
    except AttributeError:
        # Manually specify the feature names if the model does not have 'feature_names_in_'
        model_features = features.columns.tolist()  # Assuming the features in the CSV match the training features
    
    features = features[model_features]
    
    # Convert data types to numeric
    features = features.apply(pd.to_numeric, errors='coerce')
    
    # Handle missing values
    print(features.isnull().sum())
    features = features.fillna(0)
    
    # Step 9: Make predictions
    prediction = model.predict(features)

    # Step 10: Load the label encoder and transform the prediction
    label_encoder_filename = "label_encoder.pkl"
    with open(label_encoder_filename, "rb") as le_file:
        label_encoder = joblib.load(le_file)
    
    prediction_label = label_encoder.inverse_transform(prediction)
    
    print(f"Prediction: {prediction_label[0]}")

if __name__ == "__main__":
    main()