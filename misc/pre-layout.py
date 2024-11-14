import networkx as nx
import json
import pickle
from concurrent.futures import ThreadPoolExecutor
from fa2 import ForceAtlas2

# Load your edges data using multithreading
def load_edges(file_path, num_threads=10):
    G = nx.Graph()
    
    with open(file_path, 'r') as f:
        edges = f.readlines()

    def process_chunk(chunk):
        """Processes a chunk of edges and adds them to the graph."""
        for line in chunk:
            u, v = map(int, line.split())
            G.add_edge(u, v)

    # Split edges into chunks for multithreading
    chunk_size = len(edges) // num_threads
    chunks = [edges[i:i + chunk_size] for i in range(0, len(edges), chunk_size)]

    # Multithreaded processing of edge chunks
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(process_chunk, chunks)

    return G

# Prepare the graph
file_path = "twitter_combined.txt"  # Replace with your actual file path
G = load_edges(file_path)

# Correct the ForceAtlas2 configuration
forceatlas2 = ForceAtlas2(
    outboundAttractionDistribution=True,  # Dissuade hubs
    linLogMode=False,
    adjustSizes=False,
    edgeWeightInfluence=1.0,
    jitterTolerance=1.0,
    barnesHutOptimize=True,  # Optimization for large graphs
    barnesHutTheta=1.2,
    multiThreaded=False,  # Set this to False due to limitations
    scalingRatio=2.0,
    strongGravityMode=False,
    gravity=1.0,
    verbose=True
)

# Compute layout in batches to avoid memory issues
def compute_chunked_layout(G, chunk_size=10000, num_threads=10):
    all_nodes = list(G.nodes)
    positions = {}

    def process_chunk(chunk):
        """Computes the layout for a chunk of nodes using ForceAtlas2."""
        subG = G.subgraph(chunk)  # Extract a subgraph for the chunk
        pos = forceatlas2.forceatlas2_networkx_layout(subG, iterations=2000)  # Perform the layout
        return pos

    # Split the node list into chunks
    node_chunks = [all_nodes[i:i + chunk_size] for i in range(0, len(all_nodes), chunk_size)]

    # Use multithreading to compute layout for each chunk in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        chunk_results = executor.map(process_chunk, node_chunks)

    # Merge all results into a single layout
    for chunk_layout in chunk_results:
        positions.update(chunk_layout)

    return positions

# Compute the layout for all nodes in chunks using multithreading
full_pos = compute_chunked_layout(G)

# Save the computed full_pos layout before processing to avoid recomputation
with open('full_pos.pkl', 'wb') as f:
    pickle.dump(full_pos, f)

print("Full layout saved to full_pos.pkl")

# Save layout to a JSON file
layout_data = {str(node): list(pos) for node, pos in full_pos.items()}  # Convert tuple to list
with open('graph_layout.json', 'w') as f:
    json.dump(layout_data, f)

print("Layout saved to graph_layout.json")
