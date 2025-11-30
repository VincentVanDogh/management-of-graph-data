import csv

import pandas as pd
import json
from pathlib import Path

DATA_DIR = Path("../datasets/inputs/zurich-public-transport")
OUT_DIR = Path("../datasets/outputs/zurich-public-transport")
OUT_DIR.mkdir(exist_ok=True)

# Define your config here
config = {
    "nodes": {
        "haltestelle.csv": {
            "id_col": "halt_id",
            "label": "Stop"
        },
        "haltepunkt.csv": {
            "id_col": "halt_punkt_id",
            "label": "StopPoint"
        }
    },
    "edges": {
        "fahrzeitensollist1.csv": {
            "source_col": "halt_id_von",
            "target_col": "halt_id_nach",
            "edge_label": "CONNECTED_BY"
        },
        "fahrzeitensollist2.csv": {
            "source_col": "halt_id_von",
            "target_col": "halt_id_nach",
            "edge_label": "CONNECTED_BY"
        }
    }
}

# Helper function to clean and convert row to dict excluding some columns
def row_to_props(row, exclude_cols):
    return {k: v for k, v in row.items() if k not in exclude_cols and pd.notna(v) and v != ""}

# Load nodes
all_nodes = {}  # id -> props dict, including label
for fname, node_cfg in config["nodes"].items():
    path = DATA_DIR / fname
    print(f"Loading nodes from {fname}")
    df = pd.read_csv(path, dtype=str).fillna("")
    id_col = node_cfg["id_col"]
    label = node_cfg["label"]

    for _, row in df.iterrows():
        node_id = row[id_col]
        props = row_to_props(row, exclude_cols=[id_col])
        props["label"] = label
        if node_id not in all_nodes:
            all_nodes[node_id] = props
        else:
            # merge properties, new keys overwrite old
            all_nodes[node_id].update(props)

# Load edges
edges = []
for fname, edge_cfg in config["edges"].items():
    path = DATA_DIR / fname
    print(f"Loading edges from {fname}")
    df = pd.read_csv(path, dtype=str).fillna("")
    src_col = edge_cfg["source_col"]
    tgt_col = edge_cfg["target_col"]
    edge_label = edge_cfg["edge_label"]

    for _, row in df.iterrows():
        src = row[src_col]
        tgt = row[tgt_col]
        if not src or not tgt:
            continue
        props = row_to_props(row, exclude_cols=[src_col, tgt_col])
        edges.append((src, tgt, edge_label, props))

# Export nodes
with open(OUT_DIR / "nodes.csv", "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["id:ID", "properties:JSON", ":LABEL"])
    for nid, props in all_nodes.items():
        label = props.pop("label", "Entity")
        props_json = json.dumps(props, ensure_ascii=False)
        writer.writerow([nid, props_json, label])

# Export edges
with open(OUT_DIR / "edges.csv", "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f)
    writer.writerow([":START_ID", ":END_ID", ":TYPE", "properties:JSON"])
    for src, tgt, label, props in edges:
        props_json = json.dumps(props, ensure_ascii=False)
        writer.writerow([src, tgt, label, props_json])

print(f"Exported {len(all_nodes)} nodes and {len(edges)} edges to '{OUT_DIR}'")
