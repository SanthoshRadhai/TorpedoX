import sys
import joblib
from sklearn.preprocessing import StandardScaler

# Function to extract features from text
def extract_features(text):
    import string
    from collections import Counter
    from scipy.stats import entropy
    import zlib

    ascii_chars = [c for c in text if c in string.ascii_letters + string.digits + string.punctuation + ' ']
    non_ascii_chars = [c for c in text if c not in string.ascii_letters + string.digits + string.punctuation + ' ']
    ascii_ratio = len(ascii_chars) / len(text) if len(text) > 0 else 0
    non_ascii_ratio = len(non_ascii_chars) / len(text) if len(text) > 0 else 0

    char_counts = Counter(text)
    char_probs = [count / len(text) for count in char_counts.values()]
    text_entropy = entropy(char_probs, base=2) if char_probs else 0

    text_length = len(text)

    if len(text) > 0:
        compressed_data = zlib.compress(text.encode('utf-8'))
        compressed_text = len(compressed_data) / len(text.encode('utf-8'))
    else:
        compressed_text = 0

    return [ascii_ratio, non_ascii_ratio, text_entropy, text_length, compressed_text]

# Load the optimized model
model = joblib.load('backend/ClasMod/optimized_model.pkl')

# Function to classify a ciphertext
def classify_ciphertext(ciphertext):
    features = extract_features(ciphertext)
    prediction = model.predict([features])
    return "Classical Cipher" if prediction[0] == 0 else "Modern Cipher"

if __name__ == "__main__":
    ciphertext = sys.argv[1]
    classification = classify_ciphertext(ciphertext)
    print(classification)