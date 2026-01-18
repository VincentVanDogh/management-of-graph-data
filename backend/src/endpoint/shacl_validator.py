# shacl_validator.py
import os
from rdflib import Graph
from pyshacl import validate

BASE_DIR = os.path.dirname(__file__)
DATA_GRAPH = os.path.join(BASE_DIR, "output", "zurich.ttl")
SHACL_FILE = os.path.join(BASE_DIR, "shacl_shapes.ttl")
REPORT_FILE = os.path.join(BASE_DIR, "output", "shacl_report.txt")

def validate_rdf():
    data_graph = Graph()
    shacl_graph = Graph()

    data_graph.parse(DATA_GRAPH, format="ttl")
    shacl_graph.parse(SHACL_FILE, format="ttl")

    conforms, report_graph, report_text = validate(
        data_graph=data_graph,
        shacl_graph=shacl_graph,
        inference="rdfs",
        abort_on_first=False,
        meta_shacl=False,
        debug=False
    )

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_text)

    print("SHACL Validation completed.")
    print(f"Conforms: {conforms}")
    print(f"Report saved to: {REPORT_FILE}")

    return conforms

if __name__ == "__main__":
    validate_rdf()
