import numpy as np
import joblib
import tensorflow as tf
import string
import math
from collections import Counter
import collections
import os

# Feature extraction functions
def character_frequency(ciphertext):
    return Counter(ciphertext)

def bigram_frequency(ciphertext):
    return Counter([ciphertext[i:i+2] for i in range(len(ciphertext) - 1)])

def trigram_frequency(ciphertext):
    return Counter([ciphertext[i:i+3] for i in range(len(ciphertext) - 2)])

def index_of_coincidence(ciphertext):
    freq = character_frequency(ciphertext)
    N = len(ciphertext)
    return sum(f * (f - 1) for f in freq.values()) / (N * (N - 1))

def entropy(ciphertext):
    freq = character_frequency(ciphertext)
    N = len(ciphertext)
    return -sum(f/N * math.log2(f/N) for f in freq.values() if f > 0)

def repeated_substrings(ciphertext):
    return [ciphertext[i:i+3] for i in range(len(ciphertext) - 3) if ciphertext.count(ciphertext[i:i+3]) > 1]

def ciphertext_length(ciphertext):
    return len(ciphertext)

def hamming_distance(s1, s2):
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def kasiski_examination(ciphertext):
    repeated_patterns = repeated_substrings(ciphertext)
    distances = [ciphertext.find(pat, i+1) - i for i, pat in enumerate(repeated_patterns)]
    return math.gcd(*distances) if distances else None

def friedman_test(ciphertext):
    ic = index_of_coincidence(ciphertext)
    return 1 / (1 - ic) if ic != 1 else float('inf')

def digraph_frequency_analysis(ciphertext):
    digraphs = [ciphertext[i:i+2] for i in range(len(ciphertext) - 1)]
    digraph_freq = Counter(digraphs)
    total_digraphs = sum(digraph_freq.values())
    if total_digraphs == 0:
        return 0
    return max(digraph_freq.values()) / total_digraphs  

def is_triple_polygraphic_substitution(ciphertext):
    ciphertext = ''.join(filter(str.isalpha, ciphertext)).upper()
    digraph_counts = collections.Counter(ciphertext[i:i+2] for i in range(len(ciphertext) - 1))
    unique_digraphs = len(digraph_counts)
    total_digraphs = sum(digraph_counts.values())
    average_digraph_frequency = total_digraphs / unique_digraphs if unique_digraphs > 0 else 0
    threshold = 1  # Adjust threshold based on your dataset characteristics
    return 1 if average_digraph_frequency > threshold else 0
    
def has_letter_j(text):
    return int('J' in text.upper()) 

def extract_features(ciphertext):
    bigram_counts = bigram_frequency(ciphertext)
    trigram_counts = trigram_frequency(ciphertext)
    
    all_bigrams = [a+b for a in string.ascii_uppercase for b in string.ascii_uppercase]
    all_trigrams = [a+b+c for a in string.ascii_uppercase for b in string.ascii_uppercase for c in string.ascii_uppercase]
    
    bigram_features = [bigram_counts.get(bigram, 0) for bigram in all_bigrams]
    trigram_features = [trigram_counts.get(trigram, 0) for trigram in all_trigrams]

    binary_features = [
        has_letter_j(ciphertext)
    ]
    
    return [
        ciphertext_length(ciphertext),
        entropy(ciphertext),
        index_of_coincidence(ciphertext),
        len(repeated_substrings(ciphertext)),
        friedman_test(ciphertext),
        digraph_frequency_analysis(ciphertext),
        is_triple_polygraphic_substitution(ciphertext),
        *bigram_features,
        *trigram_features,
        *binary_features
    ]

# Load the model and encoders
def load_model_and_encoders(model_filename, scaler_filename, encoder_filename):
    # Check if files exist
    if not os.path.exists(model_filename):
        print(f"Error: {model_filename} not found!")
        return None, None, None
    if not os.path.exists(scaler_filename):
        print(f"Error: {scaler_filename} not found!")
        return None, None, None
    if not os.path.exists(encoder_filename):
        print(f"Error: {encoder_filename} not found!")
        return None, None, None
    
    # Load the trained model
    model = tf.keras.models.load_model(model_filename)
    print(f"Model loaded from {model_filename}")

    # Load the scaler
    scaler = joblib.load(scaler_filename)
    print(f"Scaler loaded from {scaler_filename}")

    # Load the label encoder
    label_encoder = joblib.load(encoder_filename)
    print(f"Label encoder loaded from {encoder_filename}")

    return model, scaler, label_encoder

# Predict function
def predict_algorithm(ciphertext, model, scaler, label_encoder):
    # Extract features from the ciphertext
    features = extract_features(ciphertext)
    
    # Normalize the features
    features = np.array(features).reshape(1, -1)
    features = scaler.transform(features)
    
    # Predict the algorithm and get probabilities
    predictions = model.predict(features)
    
    # Get all predictions and their probabilities
    predicted_classes = np.argsort(predictions, axis=1)[0][::-1]  # Sorted in descending order
    probabilities = np.sort(predictions, axis=1)[0][::-1]  # Sorted probabilities in descending order

    # Map predicted classes to algorithm names using the label encoder
    algorithm_probabilities = {
        label_encoder.inverse_transform([cls])[0]: prob
        for cls, prob in zip(predicted_classes, probabilities)
    }
    
    return algorithm_probabilities

# Main function for user input and evaluation
if __name__ == "__main__":
    # Load the model and encoders
    model, scaler, label_encoder = load_model_and_encoders(r'D:\cipher-analyzer\backend\ClassicalIdentifier\modelV1.2.h5', r'D:\cipher-analyzer\backend\ClassicalIdentifier\scaler1.2.pkl', r'D:\cipher-analyzer\backend\ClassicalIdentifier\label_encoder1.2.pkl')
    
    if model is None or scaler is None or label_encoder is None:
        print("Error loading necessary files. Exiting program.")
        exit(1)
    
    # Get user input for ciphertext
    user_ciphertext = input("Enter the ciphertext: ").upper()  # Ensure input is uppercase
    
    # Validate input ciphertext (make sure it's alphabetic)
    if not user_ciphertext.isalpha():
        print("Error: Ciphertext should only contain alphabetic characters.")
        exit(1)
    
    # Predict the algorithm used to generate the ciphertext
    algorithm_probabilities = predict_algorithm(user_ciphertext, model, scaler, label_encoder)
    
    # Print all predicted algorithms and their probability values
    print("Predicted algorithms and their probabilities:")
    for algorithm, probability in algorithm_probabilities.items():
        print(f"{algorithm}: {probability:.4f}")
