import json
import csv
from collections import defaultdict

INPUT_FILE = "datasets/community_infrastructure.json"
COMMUNITIES_CSV = "communities.csv"
SUBJECTS_CSV = "subjects.csv"
REL_CSV = "community_subject.csv"


def load_ndjson(path):
    """Load JSONL/NDJSON into a list of dicts."""
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    data = load_ndjson(INPUT_FILE)

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

    # --- Write communities.csv ---
    with open(COMMUNITIES_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["communityId:ID", "acronym", "name", "description", "type", ":LABEL"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(community_rows)
    print(f"Wrote {COMMUNITIES_CSV}")

    # --- Write subjects.csv ---
    with open(SUBJECTS_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["subjectName:ID", ":LABEL"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for subj in sorted(subject_set):
            writer.writerow({
                "subjectName:ID": subj,
                ":LABEL": "Subject"
            })
    print(f"Wrote {SUBJECTS_CSV}")

    # --- Write relationships ---
    with open(REL_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = [":START_ID", ":END_ID", ":TYPE"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rels)
    print(f"Wrote {REL_CSV}")

    print("\nConversion complete! Ready for Neo4j import.")
    print("Files generated:")
    print(f" - {COMMUNITIES_CSV}")
    print(f" - {SUBJECTS_CSV}")
    print(f" - {REL_CSV}")


if __name__ == "__main__":
    main()
