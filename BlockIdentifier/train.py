import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
import pickle

# Load the dataset
data = pd.read_csv("features.csv")

# Drop the 'file_name' column
data = data.drop(columns=["file_name"])

# Separate the label column before filtering numeric data
y = data["label"]  # Target column
X = data.drop(columns=["label"])  # Features (excluding the target 'label')

# Convert the label column to numeric if necessary (e.g., encoding categories)
if not pd.api.types.is_numeric_dtype(y):
    y = y.astype('category').cat.codes

# Select only numeric columns for features
X = X.select_dtypes(include=["number"])

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train the Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Evaluate the model
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Display the confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# Save the trained model and label encoder
with open("random_forest_model.pkl", "wb") as model_file:
    pickle.dump(rf_model, model_file)

with open("label_encoder.pkl", "wb") as le_file:
    pickle.dump(label_encoder, le_file)

print("Model saved as random_forest_model.pkl")
print("Label encoder saved as label_encoder.pkl")
