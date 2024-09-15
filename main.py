import os
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to load edges from file and create the graph
def create_graph(node_id):
    G = nx.DiGraph()
    file_name = f'twitter/{node_id}.edges'
    
    if not os.path.exists(file_name):
        print(f"File {file_name} not found!")
        return None, node_id

    # Load edges
    with open(file_name, 'r') as f:
        for line in f:
            a, b = map(int, line.strip().split())
            G.add_edge(a, b)
    
    # Add the 'ego' node edges
    ego_node = node_id
    all_nodes = list(G.nodes)
    for node in all_nodes:
        G.add_edge(ego_node, node)

    return G, node_id

# Function to draw the graph on the embedded canvas
def plot_graph_on_canvas(G, node_id, canvas, figure):
    if G is None:
        return
    
    figure.clear()
    ax = figure.add_subplot(111)
    pos = nx.spring_layout(G)  # Position nodes
    nx.draw(G, pos, with_labels=True, node_size=50, node_color="skyblue", arrowsize=10, font_size=8, ax=ax)
    ax.set_title(f'Ego Network {node_id}')
    
    # Redraw the canvas
    canvas.draw()

# Function to load graphs concurrently
def load_graphs(node_ids):
    graphs = []
    with ThreadPoolExecutor() as executor:
        future_to_node_id = {executor.submit(create_graph, node_id): node_id for node_id in node_ids}
        for future in as_completed(future_to_node_id):
            G, node_id = future.result()
            graphs.append((G, node_id))
    return graphs

# Function to handle dropdown selection
def on_select(event, graphs, canvas, figure):
    selected_node_id = int(event.widget.get())
    
    # Find the selected graph
    for G, node_id in graphs:
        if node_id == selected_node_id:
            plot_graph_on_canvas(G, node_id, canvas, figure)

# Main function to create the GUI and handle graph selection
def create_gui(graphs, node_ids):
    root = tk.Tk()
    root.title("Network Selector")

    # Dropdown menu for selecting node IDs
    label = ttk.Label(root, text="Select Ego Network:")
    label.pack(pady=10)

    selected_node_id = tk.StringVar()
    dropdown = ttk.Combobox(root, textvariable=selected_node_id, state='readonly')
    dropdown['values'] = node_ids
    dropdown.pack(pady=10)

    # Create a matplotlib figure and canvas to embed in Tkinter
    figure = plt.Figure(figsize=(5, 5), dpi=100)
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Bind the dropdown to the selection handler
    dropdown.bind("<<ComboboxSelected>>", lambda event: on_select(event, graphs, canvas, figure))

    root.mainloop()

# List of node_ids (assuming files are named like 12831.edges, 12832.edges, etc.)
node_ids = [12831, 78813, 356963, 428333, 612473, 613313, 623623]  # Extend this list to cover your range of networks

# Load all graphs concurrently
graphs = load_graphs(node_ids)

# Create the GUI to select and display graphs
create_gui(graphs, node_ids)
