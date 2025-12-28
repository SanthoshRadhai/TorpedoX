import sys
import re
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
import json

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
        hash_value = hash_value.replace(" ", "")
        if not re.match(self.hash_patterns[algorithm], hash_value):
            return 0
        if len(hash_value) != self.hash_lengths[algorithm]:
            return 0
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

def predict_hash_algorithm(hash_value):
    # Load the pre-trained model
    model_file = r"D:\TorpedoX\TorpedoXApp\backend\hasher\hash\hash_model.h5"
    model = joblib.load(model_file)

    # Initialize the feature extractor
    features = Features()

    # Extract features
    algorithms = ["MD5", "SHA-1", "SHA-256", "SHA-384", "SHA-512", "BLAKE2b", "BLAKE2s", "RIPEMD-160", "HMAC-SHA256"]
    feature_vector = [getattr(features, algo.replace("-", ""))(hash_value) for algo in algorithms]

    # Predict the probabilities for each algorithm
    probabilities = model.predict_proba([feature_vector])[0]

    # Create a DataFrame for better visualization
    prob_df = pd.DataFrame({"Algorithm": model.classes_, "Probability": probabilities})
    prob_df = prob_df.sort_values(by="Probability", ascending=False)

    # Extract the most and least probable algorithms
    most_probable = prob_df.head(3)
    least_probable = prob_df.tail(3)

    result = {
        "most_probable": most_probable.to_dict(orient="records"),
        "least_probable": least_probable.to_dict(orient="records")
    }

    return result

if __name__ == "__main__":
    # Get the hash value from the command-line argument (passed from the server)
    hash_value = sys.argv[1].strip()
    result = predict_hash_algorithm(hash_value)

    # Return the result in the same format the server expects
    print(json.dumps(result))
