import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.io import loadmat
from mapping import user_index_mapping, feature_index_mapping

# Load the .mat file
mat_contents = loadmat('user_feature_matrix.mat')
#print(mat_contents.keys())

user_feature_matrix = mat_contents['user_feature_matrix']

# 'user_index_mapping' is imported
index_user_mapping = {index: user for user, index in user_index_mapping.items()} # Reverse mapping (index to user id)


# number clusters
num_clusters = 5 #int(input("Enter the number of clusters: "))

# KMeans clustering
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(user_feature_matrix)

# Get the cluster labels for each user
community_labels = kmeans.labels_

# Evaluate cluster strength
inertia = kmeans.inertia_  # Sum of squared distances to closest cluster center
silhouette_avg = silhouette_score(user_feature_matrix, community_labels)

print(f"Number of clusters: {num_clusters}")
print(f"Inertia (Lower is better): {inertia}")
print(f"Silhouette Score (Range -1 to 1, Higher is better): {silhouette_avg}")
