from neo4j import GraphDatabase
import csv
import json

# --- Neo4j connection details ---
uri = "bolt://localhost:7687"
user = "neo4j"
password = "mogm1234"

# --- CSV files ---
# nodes_file = "../datasets/outputs/actors-and-movies-dataset/nodes_small.csv"
nodes_file = "../datasets/outputs/zurich-public-transport/small/nodes.csv"
# edges_file = "../datasets/outputs/actors-and-movies-dataset/edges_small.csv"
edges_file = "../datasets/outputs/zurich-public-transport/small/edges.csv"

driver = GraphDatabase.driver(uri, auth=(user, password))


def clean_json(json_str):
    """Clean JSON string for Neo4j (replace '\\N' with None and remove None props)."""
    if not json_str:
        return {}
    obj = json.loads(json_str)
    cleaned = {}
    for k, v in obj.items():
        if v is None or v == "\\N" or v == "":
            continue  # skip null or empty values
        cleaned[k] = v
    return cleaned


def load_nodes(tx, filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        i = 0
        for row in reader:
            if i % 100 == 0:
                print(i)

            node_id = row.get("id") or row.get(":ID") or row.get("id:ID")
            label = row.get(":LABEL")

            # Skip if no node id or label
            if not node_id or not label:
                print(f"Skipping node with missing id or label: id={node_id}, label={label}")
                continue

            properties_json = row.get("properties") or row.get("properties:JSON")
            properties = clean_json(properties_json)

            # Ensure id property exists and is not None/null
            properties["id"] = node_id

            query = (
                f"MERGE (n:{label} {{id: $id}}) "
                "SET n += $props"
            )
            tx.run(query, id=node_id, props=properties)
            i = i + 1



def load_edges(tx, filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        i = 0
        for row in reader:
            if i % 100 == 0:
                print(i)
            start_id = row.get(":START_ID")
            end_id = row.get(":END_ID")
            rel_type = row.get(":TYPE")

            # Skip if any critical info missing
            if not start_id or not end_id or not rel_type:
                print(f"Skipping edge with missing start/end/type: start={start_id}, end={end_id}, type={rel_type}")
                continue

            properties_json = row.get("properties:JSON")
            properties = clean_json(properties_json)

            query = (
                "MATCH (a {id: $start_id}), (b {id: $end_id}) "
                f"MERGE (a)-[r:{rel_type}]->(b) "
                "SET r += $props"
            )
            tx.run(query, start_id=start_id, end_id=end_id, props=properties)
            i = i + 1


def main():
    with driver.session() as session:
        print("Loading nodes...")
        session.execute_write(load_nodes, nodes_file)
        print("Nodes loaded.")

        print("Loading edges...")
        session.execute_write(load_edges, edges_file)
        print("Edges loaded.")


if __name__ == "__main__":
    main()
