# rdf_visualizer.py
from rdflib import Graph
import networkx as nx
import matplotlib.pyplot as plt
import os

def visualize_rdf_graph(rdf_path: str, out_img="output/graph.png"):
    """
    Visualize RDF graph (stations and lines) and save as PNG.
    """
    g = Graph()
    g.parse(rdf_path, format="turtle")

    G = nx.DiGraph()

    for s, p, o in g:
        G.add_node(str(s))
        G.add_node(str(o))
        G.add_edge(str(s), str(o), label=str(p))

    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_img), exist_ok=True)

    plt.figure(figsize=(25, 15))
    pos = nx.spring_layout(G, k=0.35)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=150, node_color="skyblue")
    # Draw edges
    nx.draw_networkx_edges(G, pos, arrows=True)
    # Labels
    nx.draw_networkx_labels(G, pos, font_size=6)

    plt.axis("off")
    plt.title("RDF Graph Visualization (Stations & Lines)")
    plt.savefig(out_img, dpi=300)
    print(f"Graph saved to {out_img}")
