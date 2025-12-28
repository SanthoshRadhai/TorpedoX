import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib

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

# Load data from directories
def load_data(directory, label):
    data = []
    text_files = [filename for filename in os.listdir(directory) if filename.endswith(".txt")]
    for filename in tqdm(text_files, desc=f"Loading data from {directory}"):
        with open(os.path.join(directory, filename), 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            features = extract_features(content)
            features.append(label)
            data.append(features)
    return data

# Load classic and modern cipher data
classic_data = load_data('classic', 0)
modern_data = load_data('modern', 1)

# Combine and create a DataFrame
all_data = classic_data + modern_data
columns = ['ascii_ratio', 'non_ascii_ratio', 'text_entropy', 'text_length', 'compression_ratio', 'label']
df = pd.DataFrame(all_data, columns=columns)

# Split the data
X = df.drop('label', axis=1)
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Create a pipeline with scaling and Random Forest
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(random_state=42))
])

# Hyperparameter tuning using GridSearchCV
param_grid = {
    'classifier__n_estimators': [50, 100, 150],
    'classifier__max_depth': [None, 10, 20],
    'classifier__min_samples_split': [2, 5, 10],
    'classifier__min_samples_leaf': [1, 2, 4]
}
grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Best model
best_model = grid_search.best_estimator_

# Evaluate the model on the test set
y_pred = best_model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Save the model
joblib.dump(best_model, 'optimized_model.pkl')
print("Optimized model trained and saved successfully.")
