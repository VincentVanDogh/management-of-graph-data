import json
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

# Load JSON
with open("../datasets/inputs/community/community_infrastructure.json") as f:
    # data = json.load(f)
    data = [json.loads(line) for line in f if line.strip()]

# Namespaces
EX = Namespace("http://example.org/community/")
EXS = Namespace("http://example.org/schema/")

g = Graph()
g.bind("ex", EX)
g.bind("exs", EXS)

# Convert each record
for item in data:
    node = EX[str(item["id"])]
    g.add((node, RDF.type, EXS.Community))

    if item.get("name"):
        g.add((node, EXS.name, Literal(item["name"])))

    if item.get("acronym"):
        g.add((node, EXS.acronym, Literal(item["acronym"])))

    if item.get("description"):
        g.add((node, EXS.description, Literal(item["description"])))

    if item.get("type"):
        g.add((node, EXS.type, Literal(item["type"])))

    if item.get("subjects"):
        for s in item["subjects"]:
            g.add((node, EXS.subject, Literal(s)))

    if item.get("zenodoCommunity"):
        g.add((node, EXS.zenodoCommunity, Literal(item["zenodoCommunity"])))

# Save to RDF
g.serialize("community.ttl", format="turtle")