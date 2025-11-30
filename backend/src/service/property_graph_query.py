from neo4j import GraphDatabase
import json

uri = "bolt://localhost:7687"
user = "neo4j"
password = "mogm1234"

driver = GraphDatabase.driver(uri, auth=(user, password))


def fetch_graph(tx, limit=10):
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    LIMIT $limit
    """
    result = tx.run(query, limit=limit)

    nodes = {}
    relationships = []

    for record in result:
        n = record["n"]
        r = record["r"]
        m = record["m"]

        # Use node id as unique key
        nodes[n.id] = {
            "id": n.id,
            "labels": list(n.labels),
            "properties": dict(n.items())
        }
        nodes[m.id] = {
            "id": m.id,
            "labels": list(m.labels),
            "properties": dict(m.items())
        }
        relationships.append({
            "id": r.id,
            "type": r.type,
            "startNode": r.start_node.id,
            "endNode": r.end_node.id,
            "properties": dict(r.items())
        })

    return {
        "nodes": list(nodes.values()),
        "relationships": relationships
    }


def get_graph_data(limit=10):
    with driver.session() as session:
        data = session.execute_read(fetch_graph, limit)
        return data

def print_all_nodes(tx, limit=100):
    query = """
    MATCH (n)
    RETURN labels(n) AS labels, n AS properties
    LIMIT $limit
    """
    result = tx.run(query, limit=limit)
    for record in result:
        print(f"Labels: {record['labels']}, Properties: {dict(record['properties'])}")

if __name__ == "__main__":
    with driver.session() as session:
        session.execute_read(print_all_nodes)


    data = get_graph_data()
    print(json.dumps(data, indent=2))
    driver.close()

