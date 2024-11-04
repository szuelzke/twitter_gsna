import json
import numpy as np
from scipy import io

# Load the sparse user feature matrix from the .mat file
sparse_data = io.loadmat('user_feature_matrix.mat')  # Adjust the filename as needed
feature_matrix = sparse_data['user_feature_matrix']  # Adjust the key based on your .mat file structure

# Load user index mapping
with open('user_index_mapping.json', 'r') as f:
    user_index_mapping = json.load(f)

# Load feature index mapping
with open('feature_index_mapping.json', 'r') as f:
    feature_index_mapping = json.load(f)

# Initialize a dictionary to hold the mapping of user IDs to features
user_features = {}

# Create a mapping of feature indices to feature names
index_to_feature = {index: feature for feature, index in feature_index_mapping.items()}

# Create a mapping of user IDs to their features
for user_id, index in user_index_mapping.items():
    # Get the feature row for the current user
    feature_row = feature_matrix[index].toarray()[0]  # Convert to dense array for easier indexing
    # Get the indices of features that are present (value > 0)
    feature_indices = np.where(feature_row > 0)[0]
    
    # Map user ID to its features using the feature names
    user_features[user_id] = [index_to_feature.get(feature_index, f"#{feature_index}") for feature_index in feature_indices]

# Save user features to a JSON file
with open('user_features.json', 'w', encoding='utf-8') as f:
    json.dump(user_features, f, ensure_ascii=False, indent=4)  # Save with pretty formatting

print("User features saved to user_features.json")
