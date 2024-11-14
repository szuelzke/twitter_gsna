import networkx as nx
import json
import community as community_louvain  # Louvain community detection package

# Load your graph
G = nx.read_edgelist('twitter_combined.txt', nodetype=int)

# Perform community detection using the Louvain method
partition = community_louvain.best_partition(G)

# Save community assignments to JSON
community_detection_data = {str(node): comm_id for node, comm_id in partition.items()}
with open("community_detection.json", "w", encoding="utf-8") as f:
    json.dump(community_detection_data, f, indent=4)

print(f"Community detection saved to community_detection.json with {max(partition.values()) + 1} communities.")
