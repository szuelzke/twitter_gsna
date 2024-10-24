import json
from bokeh.plotting import figure, curdoc
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, MultiLine
from bokeh.io import show
import networkx as nx

# Load the precomputed layout from the JSON file
with open('graph_layout.json', 'r') as f:
    layout_data = json.load(f)

# Create an empty graph using networkx
G = nx.Graph()

# Add nodes and edges
for node in layout_data.keys():
    G.add_node(int(node))

# Load edges from file (replace with your actual edge file)
with open('twitter_combined.txt', 'r') as f:
    edges = f.readlines()

for edge in edges:
    u, v = map(int, edge.split())
    G.add_edge(u, v)

# Create the Bokeh plot
plot = figure(title="Social Network Graph", x_range=(-15000, 15000), y_range=(-15000, 15000), width=1000, height=1000)
plot.grid.grid_line_color = None
plot.axis.visible = False

# Create the GraphRenderer
graph_renderer = GraphRenderer()

# Extract node indices and assign the layout positions from the JSON file
node_indices = list(G.nodes)
graph_layout = {int(node): tuple(pos) for node, pos in layout_data.items()}

# Set node colors and sizes
graph_renderer.node_renderer.data_source.data = dict(index=node_indices)
graph_renderer.node_renderer.glyph = Circle(size=8, fill_color="blue")

# Set edge rendering
start_nodes = [edge[0] for edge in G.edges]
end_nodes = [edge[1] for edge in G.edges]
graph_renderer.edge_renderer.data_source.data = dict(start=start_nodes, end=end_nodes)
graph_renderer.edge_renderer.glyph = MultiLine(line_color="gray", line_alpha=0.6, line_width=1)

# Apply the precomputed layout
graph_renderer.layout_provider = StaticLayoutProvider(graph_layout=graph_layout)

# Add the GraphRenderer to the plot
plot.renderers.append(graph_renderer)

# Display the plot
curdoc().add_root(plot)
