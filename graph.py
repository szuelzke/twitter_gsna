import json
from bokeh.plotting import figure, curdoc
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, MultiLine, HoverTool, ColumnDataSource, TextInput, Button, Triangle
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

# Prepare tooltip data with node IDs, features, and ego node status
node_ids = list(G.nodes)
node_colors = ["green" if node in ego_id else "blue" for node in node_ids]
node_sizes = [12 if node in ego_id else 8 for node in node_ids]
node_tooltips = [
    f"Node ID: {node}, Features: {', '.join(user_features.get(str(node), []))}, Ego Node: {'Yes' if node in ego_id else 'No'}"
    for node in node_ids
]

# Create ColumnDataSource for the graph's tooltips
tooltip_source = ColumnDataSource(data=dict(
    index=node_ids,
    color=node_colors,
    size=node_sizes,
    tooltip=node_tooltips
))

# Create the Bokeh plot
plot = figure(title="Social Network Graph", x_range=(-15000, 15000), y_range=(-15000, 15000), width=1000, height=1000)
plot.grid.grid_line_color = None
plot.axis.visible = False

# Define layout provider
graph_layout = {int(node): tuple(pos) for node, pos in layout_data.items()}
layout_provider = StaticLayoutProvider(graph_layout=graph_layout)

# GraphRenderer for the entire graph's nodes and edges
graph_renderer = GraphRenderer()
graph_renderer.node_renderer.data_source = tooltip_source
graph_renderer.node_renderer.glyph = Circle(size="size", fill_color="color")
graph_renderer.edge_renderer.data_source.data = dict(
    start=[edge[0] for edge in G.edges],
    end=[edge[1] for edge in G.edges],
    line_color=["gray" for _ in G.edges]
)
graph_renderer.edge_renderer.glyph = MultiLine(line_color="line_color", line_alpha=0.3, line_width=0.5)
graph_renderer.layout_provider = layout_provider

# Add main graph renderer for edges and nodes to plot
plot.renderers.append(graph_renderer)

# GraphRenderer for highlighted edges (will be overlaid on regular edges)
highlighted_edge_renderer = GraphRenderer()
highlighted_edge_renderer.node_renderer.data_source = tooltip_source  # Use same node data
highlighted_edge_renderer.node_renderer.glyph = Circle(size="size", fill_color="color")
highlighted_edge_renderer.edge_renderer.glyph = MultiLine(line_color="black", line_alpha=1, line_width=1)
highlighted_edge_renderer.layout_provider = layout_provider

# Add hover tool for nodes
hover_tool = HoverTool(tooltips=[("Tooltip", "@tooltip")])
plot.add_tools(hover_tool)

# Add highlighted edges after regular edges, before nodes
plot.renderers.insert(1, highlighted_edge_renderer)

# Create search bar
search_bar = TextInput(title="Search for Node ID:", placeholder="Enter Node ID")

# Store original colors and edge attributes for reset
original_node_colors = list(node_colors)
original_edge_colors = ["gray" for _ in G.edges]

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

    # Highlight the searched node and its first-degree edges
    highlight_colors = ["red" if node == node_id else original_node_colors[i] for i, node in enumerate(node_ids)]
    edge_start, edge_end = list(graph_renderer.edge_renderer.data_source.data['start']), list(graph_renderer.edge_renderer.data_source.data['end'])
    highlight_edge_start = [edge_start[i] for i in range(len(edge_start)) if edge_start[i] == node_id or edge_end[i] == node_id]
    highlight_edge_end = [edge_end[i] for i in range(len(edge_end)) if edge_start[i] == node_id or edge_end[i] == node_id]
    
    # Update color data source with highlighted colors
    graph_renderer.node_renderer.data_source.data.update(color=highlight_colors)
    
    # Update highlighted edges renderer data
    highlighted_edge_renderer.edge_renderer.data_source.data.update(
        start=highlight_edge_start,
        end=highlight_edge_end
    )

search_bar.on_change("value", search_node)

# Define "Clear Search" button callback to reset graph
def clear_search():
    # Reset plot ranges to original
    plot.x_range.start, plot.x_range.end = -15000, 15000
    plot.y_range.start, plot.y_range.end = -15000, 15000
    search_bar.value = ""

    # Restore original node and edge colors
    graph_renderer.node_renderer.data_source.data.update(color=original_node_colors)
    highlighted_edge_renderer.edge_renderer.data_source.data.update(start=[], end=[])

# Create "Clear Search" button
clear_button = Button(label="Clear Search", button_type="warning")
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

# Layout search, clear, zoom buttons, and plot
layout = column(row(search_bar, clear_button, zoom_in_button, zoom_out_button), plot)
curdoc().add_root(layout)

print("Plot with search, clear, and zoom functionality is ready to be displayed.")
