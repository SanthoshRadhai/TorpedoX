import os
import csv
import re
import pandas as pd
from tqdm import tqdm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

class Features:
    def __init__(self):
        self.hash_patterns = {
            'MD5': r'^[a-fA-F0-9]{32}$',
            'SHA-1': r'^[a-fA-F0-9]{40}$',
            'SHA-256': r'^[a-fA-F0-9]{64}$',
            'SHA-384': r'^[a-fA-F0-9]{96}$',
            'SHA-512': r'^[a-fA-F0-9]{128}$',
            'BLAKE2b': r'^[a-fA-F0-9]{128}$',
            'BLAKE2s': r'^[a-fA-F0-9]{64}$',
            'RIPEMD-160': r'^[a-fA-F0-9]{40}$',
            'HMAC-SHA256': r'^[a-fA-F0-9]{64}$'
        }
        self.hash_lengths = {
            'MD5': 32,
            'SHA-1': 40,
            'SHA-256': 64,
            'SHA-384': 96,
            'SHA-512': 128,
            'BLAKE2b': 128,
            'BLAKE2s': 64,
            'RIPEMD-160': 40,
            'HMAC-SHA256': 64
        }

    def is_valid_hex(self, hash_value):
        try:
            int(hash_value, 16)
            return True
        except ValueError:
            return False

    def check_hash(self, hash_value, algorithm):
        # Remove spaces from the hash value
        hash_value = hash_value.replace(" ", "")
        
        # Check if the hash matches the regular expression
        if not re.match(self.hash_patterns[algorithm], hash_value):
            return 0
        
        # Check if the hash length is correct
        if len(hash_value) != self.hash_lengths[algorithm]:
            return 0
        
        # Check if the hash is a valid hex string
        if not self.is_valid_hex(hash_value):
            return 0
        
        return 1

    def MD5(self, hash_value):
        return self.check_hash(hash_value, 'MD5')

    def SHA1(self, hash_value):
        return self.check_hash(hash_value, 'SHA-1')

    def SHA256(self, hash_value):
        return self.check_hash(hash_value, 'SHA-256')

    def SHA384(self, hash_value):
        return self.check_hash(hash_value, 'SHA-384')

    def SHA512(self, hash_value):
        return self.check_hash(hash_value, 'SHA-512')

    def BLAKE2b(self, hash_value):
        return self.check_hash(hash_value, 'BLAKE2b')

    def BLAKE2s(self, hash_value):
        return self.check_hash(hash_value, 'BLAKE2s')

    def RIPEMD160(self, hash_value):
        return self.check_hash(hash_value, 'RIPEMD-160')

    def HMACSHA256(self, hash_value):
        return self.check_hash(hash_value, 'HMAC-SHA256')

def extract_features_from_dataset(dataset_folder, output_csv):
    features = Features()
    algorithms = ["MD5", "SHA-1", "SHA-256", "SHA-384", "SHA-512", "BLAKE2b", "BLAKE2s", "RIPEMD-160", "HMAC-SHA256"]
    
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['file_name', 'hash_data'] + algorithms
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for algorithm in algorithms:
            folder_path = os.path.join(dataset_folder, algorithm)
            files = os.listdir(folder_path)
            for filename in tqdm(files, desc=f"Processing {algorithm}", unit="file"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as file:
                    hash_value = file.read().strip()
                    row = {'file_name': filename, 'hash_data': hash_value}
                    for algo in algorithms:
                        row[algo] = getattr(features, algo.replace("-", ""))(hash_value)
                    writer.writerow(row)

def train_and_save_model(csv_file, model_file):
    # Load the dataset
    df = pd.read_csv(csv_file)
    
    # Prepare the data
    X = df.drop(columns=['file_name', 'hash_data'])
    y = df['file_name'].apply(lambda x: x.split('_')[0])  # Extract the algorithm name from the file name
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy * 100:.2f}%")
    
    # Save the model
    joblib.dump(model, model_file)
    print(f"Model saved to {model_file}")

# Example usage
dataset_folder = 'Hash_dataset'
output_csv = 'Hash.csv'
model_file = 'hash_model.h5'

# Extract features and save to CSV
extract_features_from_dataset(dataset_folder, output_csv)

# Train the model and save it
train_and_save_model(output_csv, model_file)