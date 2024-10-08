import networkx as nx
import numpy as np
import os
import sys
from scipy.sparse import lil_matrix
from scipy import io

# Reconfigure the system stdout to use utf-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Define the directory containing Twitter files
DIR = "twitter"

# Initialize feature table and user set
feature_table = {}
user_set = set()
ego_id = []  # To hold all ego node IDs

# Loop through files in the Twitter directory to extract ego node IDs
for filename in os.listdir(DIR):
    if filename.endswith('.egofeat'):  # Adjust this condition based on your file naming convention
        # Extract the ego node ID from the filename (assuming format is '{id}.egofeat')
        ego_node_id = int(filename.split('.')[0])  # Extract the ID before the '.egofeat' extension
        ego_id.append(ego_node_id)  # Add it to the ego_id list

        user_features = {}
        # Read the ego user
        with open(os.path.join(DIR, filename)) as egofeat:
            line = egofeat.readline().strip().split(' ')
            user_features[ego_node_id] = [int(x) for x in line]
            user_set.add(ego_node_id)

        # Read the ego user's friends
        feat_filename = os.path.join(DIR, f'{ego_node_id}.feat')
        if os.path.exists(feat_filename):
            with open(feat_filename) as feat:
                for line in feat:
                    user_id = int(line.strip().split(' ')[0])
                    user_set.add(user_id)
                    user_features[user_id] = [int(x) for x in line.strip().split(' ')[1:]]

        # Fill the dimension with corresponding feature ID
        featnames_filename = os.path.join(DIR, f'{ego_node_id}.featnames')
        if os.path.exists(featnames_filename):
            with open(featnames_filename, encoding='utf-8') as file:
                for line in file:
                    d = line.strip().split(' ')[0]
                    feature_id = line.strip().split(';')[-1].split(' ')[-1]
                    #print("test: ", ego_node_id, " - ", d, feature_id)

                    for user in user_features:
                        if feature_id not in feature_table:
                            feature_table[feature_id] = []
                        
                        if user_features[user][int(d)] == 1:
                            feature_table[feature_id].append(user)

# Use a sparse matrix to construct the user-feature matrix
num_users = len(user_set)
num_features = len(feature_table)
user_feature_matrix = lil_matrix((num_users, num_features), dtype=bool)

# Create mappings for users and features
user_index_mapping = {user: index for index, user in enumerate(user_set)}
feature_index_mapping = {feature_id: index for index, feature_id in enumerate(feature_table)}