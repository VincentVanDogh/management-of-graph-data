import json

from config import COMMUNITY_INFRASTRUCTURE, COMMUNITIES_PROPERTY_GRAPH_JSON



def load_jsonl(path):
    """Loads a JSONL file and returns a list of parsed objects."""
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


def build_graph(data):
    nodes = []
    edges = []

    # To avoid duplicate subject nodes
    subject_set = set()

    for com in data:
        com_id = com["id"]

        # --- COMMUNITY NODE ---
        nodes.append({
            "id": com_id,
            "label": com.get("name"),
            "type": com.get("type", "Community"),
            "acronym": com.get("acronym"),
            "description": com.get("description"),
            "zenodoCommunity": com.get("zenodoCommunity")
        })

        # --- SUBJECT NODES + RELATIONSHIPS ---
        subjects = com.get("subjects", [])
        for subj in subjects:
            subj_id = f"subject__{subj}"

            # Create subject node ONCE
            if subj_id not in subject_set:
                subject_set.add(subj_id)
                nodes.append({
                    "id": subj_id,
                    "label": subj,
                    "type": "Subject"
                })

            # Create edge Community → Subject
            edges.append({
                "id": f"{com_id}__{subj_id}",
                "source": com_id,
                "target": subj_id,
                "type": "HAS_SUBJECT"
            })

    return {"nodes": nodes, "edges": edges}


def main():
    print("Loading JSONL...")
    data = load_jsonl(COMMUNITY_INFRASTRUCTURE)

    print(f"Loaded {len(data)} community records")

    print("Building graph...")
    graph = build_graph(data)

    print(f"Nodes: {len(graph['nodes'])}")
    print(f"Edges: {len(graph['edges'])}")

    print(f"Writing to {COMMUNITIES_PROPERTY_GRAPH_JSON}...")
    with open(COMMUNITIES_PROPERTY_GRAPH_JSON, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print("Done! Graph exported successfully.")


if __name__ == "__main__":
    main()
