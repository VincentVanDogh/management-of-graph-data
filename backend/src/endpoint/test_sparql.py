from rdflib import Graph

g = Graph()
g.parse("output/zurich.ttl", format="ttl")

q = """
PREFIX ex: <http://example.org/zurich/>

SELECT ?s ?p ?o WHERE {
  ?s a ex:Station .
  ?s ?p ?o .
}
LIMIT 50
"""

res = g.query(q)
for row in res:
    print(row)
