import json
from bokeh.plotting import figure, curdoc
from bokeh.models import Div, GraphRenderer, StaticLayoutProvider, Circle, Square, MultiLine, HoverTool, ColumnDataSource, TextInput, Button
from bokeh.layouts import column, row
import networkx as nx
import os
import sys
import community  # Louvain community detection package
import random  # To generate random colors for each community

# Reconfigure system stdout to use utf-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Define the directory containing Twitter files
DIR = "twitter"

# Initialize feature table and user set
ego_id = []  # To hold all ego node IDs

# Loop through files in the Twitter directory to extract ego node IDs
for filename in os.listdir(DIR):
    if filename.endswith('.egofeat'):
        ego_node_id = int(filename.split('.')[0])
        ego_id.append(ego_node_id)

# Load the precomputed layout from the JSON file
with open('graph_layout.json', 'r', encoding='utf-8') as f:
    layout_data = json.load(f)

# Create an empty graph using networkx
G = nx.Graph()
for node in layout_data.keys():
    G.add_node(int(node))

# Load edges from file
with open('twitter_combined.txt', 'r', encoding='utf-8', errors='ignore') as f:
    edges = f.readlines()
for edge in edges:
    u, v = map(int, edge.split())
    G.add_edge(u, v)

# Load user features from the JSON file
with open('user_features.json', 'r', encoding='utf-8') as f:
    user_features = json.load(f)

# Separate node data for ego and non-ego nodes
ego_nodes = [node for node in G.nodes if node in ego_id]
non_ego_nodes = [node for node in G.nodes if node not in ego_id]
ego_colors = ["blue"] * len(ego_nodes)  # All nodes start as blue
non_ego_colors = ["blue"] * len(non_ego_nodes)
ego_sizes = [12] * len(ego_nodes)
non_ego_sizes = [8] * len(non_ego_nodes)

# Tooltips for nodes
ego_tooltips = [
    f"Node ID: {node}, Features: {', '.join(user_features.get(str(node), []))}, Ego Node: Yes"
    for node in ego_nodes
]
non_ego_tooltips = [
    f"Node ID: {node}, Features: {', '.join(user_features.get(str(node), []))}, Ego Node: No"
    for node in non_ego_nodes
]

# ColumnDataSource for ego and non-ego nodes
ego_source = ColumnDataSource(data=dict(
    index=ego_nodes,
    color=ego_colors,
    size=ego_sizes,
    tooltip=ego_tooltips
))

non_ego_source = ColumnDataSource(data=dict(
    index=non_ego_nodes,
    color=non_ego_colors,
    size=non_ego_sizes,
    tooltip=non_ego_tooltips
))

# Create the Bokeh plot
plot = figure(title="Social Network Graph", x_range=(-15000, 15000), y_range=(-15000, 15000), width=1000, height=1000)
plot.grid.grid_line_color = None
plot.axis.visible = False

# Define layout provider
graph_layout = {int(node): tuple(pos) for node, pos in layout_data.items()}
layout_provider = StaticLayoutProvider(graph_layout=graph_layout)

# GraphRenderer for non-ego nodes (circles)
non_ego_renderer = GraphRenderer()
non_ego_renderer.node_renderer.data_source = non_ego_source
non_ego_renderer.node_renderer.glyph = Circle(size="size", fill_color="color")
non_ego_renderer.edge_renderer.data_source.data = dict(
    start=[edge[0] for edge in G.edges],
    end=[edge[1] for edge in G.edges],
    line_color=["gray" for _ in G.edges]
)
non_ego_renderer.edge_renderer.glyph = MultiLine(line_color="line_color", line_alpha=0.3, line_width=0.5)
non_ego_renderer.layout_provider = layout_provider

# GraphRenderer for ego nodes (squares)
ego_renderer = GraphRenderer()
ego_renderer.node_renderer.data_source = ego_source
ego_renderer.node_renderer.glyph = Square(size="size", fill_color="color")
ego_renderer.layout_provider = layout_provider  # No edge renderer needed for ego renderer

# Add main graph renderer for edges and nodes to plot
plot.renderers.append(non_ego_renderer)
plot.renderers.append(ego_renderer)

# Add hover tool for nodes
hover_tool = HoverTool(tooltips=[("Tooltip", "@tooltip")])
plot.add_tools(hover_tool)

# Create search bar
search_bar = TextInput(title="Search for Node ID:", placeholder="Enter Node ID")

# Store original colors and edge attributes for reset
original_ego_colors = list(ego_colors)
original_non_ego_colors = list(non_ego_colors)

# Define callback for search
def search_node(attr, old, new):
    try:
        node_id = int(new)
    except ValueError:
        return

    if node_id not in G.nodes:
        return

    # Center plot on searched node
    if node_id in graph_layout:
        x, y = graph_layout[node_id]
        plot.x_range.start = x - 200
        plot.x_range.end = x + 200
        plot.y_range.start = y - 200
        plot.y_range.end = y + 200

    # Highlight the searched node
    ego_source.data.update(color=["red" if node == node_id else "blue" for node in ego_nodes])
    non_ego_source.data.update(color=["red" if node == node_id else "blue" for node in non_ego_nodes])

    # Highlight first-degree edges of the searched node
    first_degree_edges = [edge for edge in G.edges(node_id)]
    first_degree_edges_start = [edge[0] for edge in first_degree_edges]
    first_degree_edges_end = [edge[1] for edge in first_degree_edges]

    # Change color of first-degree edges to emphasize them
    non_ego_renderer.edge_renderer.data_source.data.update(
        start=[edge[0] for edge in G.edges],
        end=[edge[1] for edge in G.edges],
        line_color=["red" if (edge[0] == node_id or edge[1] == node_id) else "gray" for edge in G.edges]
    )

    # Update node shapes to stars for the searched node
    ego_renderer.node_renderer.glyph = Square(size="size", fill_color="color")  # Ensure we keep it a square for ego nodes
    non_ego_renderer.node_renderer.glyph = Circle(size="size", fill_color="color")  # Keep it as circle for non-ego nodes

search_bar.on_change("value", search_node)

# Define "Clear Search" button callback to reset graph
def clear_search():
    plot.x_range.start, plot.x_range.end = -15000, 15000
    plot.y_range.start, plot.y_range.end = -15000, 15000
    search_bar.value = ""
    cd_output.text = ""

    # Restore original node colors
    ego_source.data.update(color=original_ego_colors)
    non_ego_source.data.update(color=original_non_ego_colors)

# Define zoom buttons
def zoom_in():
    plot.x_range.start *= 0.8
    plot.x_range.end *= 0.8
    plot.y_range.start *= 0.8
    plot.y_range.end *= 0.8

def zoom_out():
    plot.x_range.start /= 0.8
    plot.x_range.end /= 0.8
    plot.y_range.start /= 0.8
    plot.y_range.end /= 0.8

# Create zoom buttons
zoom_in_button = Button(label="Zoom In", button_type="success")
zoom_in_button.on_click(zoom_in)

zoom_out_button = Button(label="Zoom Out", button_type="success")
zoom_out_button.on_click(zoom_out)

# Community detection function
def community_detection():
    # Load the saved community data from community_detection.json
    try:
        with open("community_detection.json", "r") as f:
            community_data = json.load(f)
    except FileNotFoundError:
        cd_output.text = "community_detection.json not found."
        return

    # Ensure all nodes in G have a community assignment
    default_community = max(community_data.values(), default=0) + 1  # New community ID for any missing nodes
    for node in G.nodes:
        if str(node) not in community_data:
            community_data[str(node)] = default_community  # Assign to default community

    # Convert community data back to int keys for modularity calculation
    partition = {int(node): comm_id for node, comm_id in community_data.items()}

    # Calculate modularity score with the updated partition
    modularity_score = community.modularity(partition, G)

    # Detect the number of communities
    num_communities = len(set(partition.values()))

    # Assign random colors to each community
    community_colors = {}
    distinct_colors = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(num_communities)]
    for comm_id in set(partition.values()):
        color = distinct_colors[comm_id]
        community_nodes = [node for node, comm in partition.items() if comm == comm_id]
        for node in community_nodes:
            community_colors[node] = color

    # Update node colors based on the community detection
    ego_source.data.update(color=[community_colors.get(node, "blue") for node in ego_nodes])
    non_ego_source.data.update(color=[community_colors.get(node, "blue") for node in non_ego_nodes])

    # Display the modularity score and number of communities on the screen
    cd_output.text = f"Detected {num_communities} communities.\nModularity Score: {modularity_score:.4f}"

# Community detection button
community_button = Button(label="Detect Communities", button_type="success")
community_button.on_click(community_detection)

# Clear button
clear_button = Button(label="Reset", button_type="danger")
clear_button.on_click(clear_search)

# Create the output div for community results
cd_output = Div(width=400, height=400)

layout = column(row(search_bar, clear_button, zoom_in_button, zoom_out_button), community_button, cd_output, plot)
curdoc().add_root(layout)
