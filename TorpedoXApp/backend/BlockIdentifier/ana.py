import pickle

# Load the trained model
with open("random_forest_model.pkl", "rb") as file:
    model = pickle.load(file)

# Print model type
print("Model Type:", type(model))

# Print model parameters if available
if hasattr(model, "get_params"):
    print("\nModel Parameters:\n", model.get_params())

# Print feature importance (if applicable)
if hasattr(model, "feature_importances_"):
    print("\nFeature Importance:\n", model.feature_importances_)

# Print model coefficients (for linear models)
if hasattr(model, "coef_"):
    print("\nModel Coefficients:\n", model.coef_)

# List available methods in the model
print("\nAvailable Methods in the Model:")
print(dir(model))