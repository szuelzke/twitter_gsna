import networkx as nx
import numpy as np

# function to calculate various statistics on twitter graph
def calculate_graph_statistics(G):
    
    # number of nodes and edges
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    print(f"Number of nodes: {num_nodes}")
    print(f"Number of edges: {num_edges}")

    # degree-related statistics
    degrees = list(dict(G.degree()).values())
    average_degree = np.mean(degrees)
    max_degree = max(degrees)
    min_degree = min(degrees)

    # density
    density = nx.density(G)

    # average clustering coefficient
    avg_clustering_coefficient = nx.average_clustering(G)

    # diameter and average shortest path length
    try:
        diameter = nx.diameter(G)
    except nx.NetworkXError:
        diameter = float('inf')  # If the graph is not connected

    try:
        avg_shortest_path_length = nx.average_shortest_path_length(G)
    except nx.NetworkXError:
        avg_shortest_path_length = float('inf')  # If the graph is not connected

    # Print statistics
    print(f"Density: {density:.6f}")
    print(f"Average Degree: {average_degree:.2f}")
    print(f"Maximum Degree: {max_degree}")
    print(f"Minimum Degree: {min_degree}")
    print(f"Average Clustering Coefficient: {avg_clustering_coefficient:.6f}")
    print(f"Diameter: {diameter}")
    print(f"Average Shortest Path Length: {avg_shortest_path_length}")


# main
G = nx.read_adjlist("twitter_combined.txt", delimiter=' ')
calculate_graph_statistics(G)