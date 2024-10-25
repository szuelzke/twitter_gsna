import json
from bokeh.plotting import figure, curdoc
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, MultiLine, HoverTool, ColumnDataSource
import networkx as nx
from scipy import io
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
    if filename.endswith('.egofeat'):  # Adjust this condition based on your file naming convention
        # Extract the ego node ID from the filename (assuming format is '{id}.egofeat')
        ego_node_id = int(filename.split('.')[0])  # Extract the ID before the '.egofeat' extension
        ego_id.append(ego_node_id)  # Add it to the ego_id list

print(ego_id)

# Load the precomputed layout from the JSON file
with open('graph_layout.json', 'r', encoding='utf-8') as f:
    layout_data = json.load(f)

# Create an empty graph using networkx
G = nx.Graph()

# Add nodes from the layout data
for node in layout_data.keys():
    G.add_node(int(node))

print(f"Nodes added: {len(G.nodes)}")  # Debugging output

# Load edges from file
with open('twitter_combined.txt', 'r', encoding='utf-8', errors='ignore') as f:
    edges = f.readlines()

for edge in edges:
    u, v = map(int, edge.split())
    G.add_edge(u, v)

print(f"Edges added: {len(G.edges)}")  # Debugging output

# Load user index mapping
with open('user_index_mapping.json', 'r', encoding='utf-8') as f:
    user_index_mapping = json.load(f)

# Load user features from the JSON file
with open('user_features.json', 'r', encoding='utf-8') as f:
    user_features = json.load(f)

# Prepare tooltip data with node IDs and features
tooltip_data = []
for node in G.nodes:
    features = user_features.get(str(node), [])
    tooltip_data.append((int(node), str(node), ', '.join(features)))  # Joining features as a string

# Debugging output for tooltip data
print("Tooltip Data Generated:")
for t in tooltip_data:
    print(t)

# Create a ColumnDataSource for tooltips
if tooltip_data:
    tooltip_source = ColumnDataSource(data=dict(node_id=[t[0] for t in tooltip_data],
                                                 tooltip=[f"Node ID: {t[1]}, Features: {t[2]}" for t in tooltip_data]))
else:
    tooltip_source = ColumnDataSource(data=dict(node_id=[], tooltip=[]))  # Handle empty case

# Create the Bokeh plot
plot = figure(title="Social Network Graph", x_range=(-15000, 15000), y_range=(-15000, 15000), width=1000, height=1000)
plot.grid.grid_line_color = None
plot.axis.visible = False

# Create the GraphRenderer
graph_renderer = GraphRenderer()

# Extract node indices and assign the layout positions from the JSON file
node_indices = list(G.nodes)
graph_layout = {int(node): tuple(pos) for node, pos in layout_data.items()}

# Debugging output for layout positions
print("Graph layout keys:", layout_data.keys())
print("Graph layout positions:", graph_layout)

# Set node colors and sizes
node_colors = ["green" if node in ego_id else "blue" for node in node_indices]
graph_renderer.node_renderer.data_source.data = dict(index=node_indices, color=node_colors)

graph_renderer.node_renderer.glyph = Circle(size=8, fill_color="color")

# Set edge rendering
start_nodes = [edge[0] for edge in G.edges]
end_nodes = [edge[1] for edge in G.edges]
graph_renderer.edge_renderer.data_source.data = dict(start=start_nodes, end=end_nodes)
graph_renderer.edge_renderer.glyph = MultiLine(line_color="gray", line_alpha=0.6, line_width=1)

# Apply the precomputed layout
graph_renderer.layout_provider = StaticLayoutProvider(graph_layout=graph_layout)

# Add hover tool for tooltips (showing node ID and features)
hover_tool = HoverTool(tooltips=[("Tooltip", "@tooltip")])
plot.add_tools(hover_tool)

# Ensure the tooltip source data is added to the renderer
graph_renderer.node_renderer.data_source.data.update(tooltip_source.data)

# Add the GraphRenderer to the plot
plot.renderers.append(graph_renderer)

# Display the plot
curdoc().add_root(plot)

# Final check to see if the plot is ready
print("Plot is ready to be displayed.")
