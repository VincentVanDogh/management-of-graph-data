# rdf_exporter.py
from rdflib import Graph
import json

def export_rdf_to_json(rdf_path: str, out_path="output/graph.json"):
    g = Graph()
    g.parse(rdf_path, format="turtle")

    nodes = set()
    edges = []

    for s, p, o in g:
        s = str(s)
        o = str(o)
        p = str(p)

        nodes.add(s)
        nodes.add(o)

        edges.append({
            "source": s,
            "target": o,
            "label": p
        })

    data = {
        "nodes": [{"id": n} for n in nodes],
        "edges": edges
    }

    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Graph exported to {out_path}")
    return out_path
