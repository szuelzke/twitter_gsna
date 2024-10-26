import json
from bokeh.plotting import figure, curdoc
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, MultiLine, HoverTool, ColumnDataSource, TextInput, Button
from bokeh.layouts import column, row
import networkx as nx
import os
import sys

# Reconfigure the system stdout to use utf-8 encoding
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

# Prepare tooltip data with node IDs and features
tooltip_data = [(int(node), str(node), ', '.join(user_features.get(str(node), []))) for node in G.nodes]

# Create a ColumnDataSource for tooltips
tooltip_source = ColumnDataSource(data=dict(
    node_id=[t[0] for t in tooltip_data],
    tooltip=[f"Node ID: {t[1]}, Features: {t[2]}" for t in tooltip_data]
))

# Create the Bokeh plot
plot = figure(title="Social Network Graph", x_range=(-15000, 15000), y_range=(-15000, 15000), width=1000, height=1000)
plot.grid.grid_line_color = None
plot.axis.visible = False

# Create the GraphRenderer
graph_renderer = GraphRenderer()
node_indices = list(G.nodes)
graph_layout = {int(node): tuple(pos) for node, pos in layout_data.items()}
node_colors = ["green" if node in ego_id else "blue" for node in node_indices]
node_sizes = [8 for _ in node_indices]

graph_renderer.node_renderer.data_source.data = dict(index=node_indices, color=node_colors, size=node_sizes)
graph_renderer.node_renderer.glyph = Circle(size="size", fill_color="color")

start_nodes = [edge[0] for edge in G.edges]
end_nodes = [edge[1] for edge in G.edges]
graph_renderer.edge_renderer.data_source.data = dict(start=start_nodes, end=end_nodes)
graph_renderer.edge_renderer.glyph = MultiLine(line_color="gray", line_alpha=0.6, line_width=1)

graph_renderer.layout_provider = StaticLayoutProvider(graph_layout=graph_layout)

hover_tool = HoverTool(tooltips=[("Tooltip", "@tooltip")])
plot.add_tools(hover_tool)
graph_renderer.node_renderer.data_source.data.update(tooltip_source.data)
plot.renderers.append(graph_renderer)

# Create a search bar (TextInput widget) for searching nodes
search_bar = TextInput(title="Search for Node ID:", placeholder="Enter Node ID")

# Define callback for node search
def search_node(attr, old, new):
    try:
        node_id = int(new)
    except ValueError:
        return
    if node_id not in G.nodes:
        return

    new_colors = ["red" if node == node_id else "green" if node in ego_id else "blue" for node in node_indices]
    new_sizes = [12 if node == node_id else 8 for node in node_indices]
    graph_renderer.node_renderer.data_source.data.update(color=new_colors, size=new_sizes)

    if node_id in graph_layout:
        x, y = graph_layout[node_id]
        plot.x_range.start = x - 100
        plot.x_range.end = x + 100
        plot.y_range.start = y - 100
        plot.y_range.end = y + 100

search_bar.on_change("value", search_node)

# Define zoom in and zoom out button callbacks
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

# Layout the search bar, zoom buttons, and plot
layout = column(row(search_bar, zoom_in_button, zoom_out_button), plot)
curdoc().add_root(layout)

print("Plot with search and zoom functionality is ready to be displayed.")
