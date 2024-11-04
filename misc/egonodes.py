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
ego_id = []  # To hold all ego node IDs

# Loop through files in the Twitter directory to extract ego node IDs
for filename in os.listdir(DIR):
    if filename.endswith('.egofeat'):  # Adjust this condition based on your file naming convention
        # Extract the ego node ID from the filename (assuming format is '{id}.egofeat')
        ego_node_id = int(filename.split('.')[0])  # Extract the ID before the '.egofeat' extension
        ego_id.append(ego_node_id)  # Add it to the ego_id list

print(ego_id)