import json
from bokeh.plotting import figure, curdoc
from bokeh.models import Div, GraphRenderer, StaticLayoutProvider, Circle, Square, MultiLine, HoverTool, ColumnDataSource, TextInput, Button
from bokeh.layouts import column, row
import networkx as nx
import os
import sys

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
original_edge_colors = ["gray" for _ in G.edges]
original_ego_shapes = ["square"] * len(ego_nodes)
original_non_ego_shapes = ["circle"] * len(non_ego_nodes)

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
    # Reset plot ranges to original
    plot.x_range.start, plot.x_range.end = -15000, 15000
    plot.y_range.start, plot.y_range.end = -15000, 15000
    search_bar.value = ""
    cd_output.text = ""  # Clear the community detection output text

    # Restore original node shapes and colors
    ego_source.data.update(color=original_ego_colors)
    non_ego_source.data.update(color=original_non_ego_colors)
    non_ego_renderer.edge_renderer.data_source.data.update(line_color=original_edge_colors)

    # Reset to square for ego nodes and circle for non-ego nodes
    ego_renderer.node_renderer.glyph = Square(size="size", fill_color="color")  # Reset to square
    non_ego_renderer.node_renderer.glyph = Circle(size="size", fill_color="color")  # Reset to circle

# Create "Clear Search" button
clear_button = Button(label="Reset", button_type="warning")
clear_button.on_click(clear_search)

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

# Define Community Detection button and output text
def community_detection():
    # community detection in progress
    cd_output.text = "CD in progress (placeholder, not yet implemented)"

cd_button = Button(label="Community Detection", button_type="primary")
cd_button.on_click(community_detection)

cd_output = Div(text="")  # Output area for community detection status

# Layout search, clear, and plot
layout = column(row(search_bar, clear_button, zoom_in_button, zoom_out_button), cd_button, cd_output, plot)
curdoc().add_root(layout)

print("Plot with ego nodes as squares and non-ego nodes as circles.")
