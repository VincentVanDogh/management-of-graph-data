import json
import csv
import os

from config.config import COMMUNITIES_PROPERTY_GRAPH_CSV, SUBJECTS_PROPERTY_GRAPH_CSV, COMMUNITIES_SUBJECTS_PROPERTY_GRAPH_CSV, \
    COMMUNITY_INFRASTRUCTURE, PROPERTY_GRAPHS_OUTPUT


def load_ndjson(path):
    """Load JSONL/NDJSON into a list of dicts."""
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    data = load_ndjson(COMMUNITY_INFRASTRUCTURE)

    # Collect subjects for global deduplication
    subject_set = set()

    # Relationship edges
    rels = []

    # Prepare rows for the nodes
    community_rows = []

    for item in data:
        cid = item["id"]

        # --- Community node ---
        community_rows.append({
            "communityId:ID": cid,
            "acronym": item.get("acronym", ""),
            "name": item.get("name", ""),
            "description": item.get("description", ""),
            "type": item.get("type", ""),
            ":LABEL": "Community"
        })

        # --- Subjects ---
        subjects = item.get("subjects", [])
        for subj in subjects:
            subject_set.add(subj)
            rels.append({
                ":START_ID": cid,
                ":END_ID": subj,
                ":TYPE": "HAS_SUBJECT"
            })

    # Check that property_graph-dir exists, if not, create it
    if not os.path.exists(PROPERTY_GRAPHS_OUTPUT):
        os.makedirs(PROPERTY_GRAPHS_OUTPUT)

    # --- Write communities.csv ---
    with open(COMMUNITIES_PROPERTY_GRAPH_CSV, "w+", newline="", encoding="utf-8") as f:
        fieldnames = ["communityId:ID", "acronym", "name", "description", "type", ":LABEL"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(community_rows)
    print(f"Wrote {COMMUNITIES_PROPERTY_GRAPH_CSV}")

    # --- Write subjects.csv ---
    with open(SUBJECTS_PROPERTY_GRAPH_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["subjectName:ID", ":LABEL"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for subj in sorted(subject_set):
            writer.writerow({
                "subjectName:ID": subj,
                ":LABEL": "Subject"
            })
    print(f"Wrote {SUBJECTS_PROPERTY_GRAPH_CSV}")

    # --- Write relationships ---
    with open(COMMUNITIES_SUBJECTS_PROPERTY_GRAPH_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = [":START_ID", ":END_ID", ":TYPE"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rels)
    print(f"Wrote {COMMUNITIES_SUBJECTS_PROPERTY_GRAPH_CSV}")

    print("\nConversion complete! Ready for Neo4j import.")
    print("Files generated:")
    print(f" - {COMMUNITIES_PROPERTY_GRAPH_CSV}")
    print(f" - {SUBJECTS_PROPERTY_GRAPH_CSV}")
    print(f" - {COMMUNITIES_SUBJECTS_PROPERTY_GRAPH_CSV}")


if __name__ == "__main__":
    main()
