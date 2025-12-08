import csv
import pandas as pd
import json
from pathlib import Path

from config.zurich_public_transport_config import ZURICH_PUBLIC_TRANSPORT_CONFIG

DATA_DIR = Path("../datasets/inputs/zurich-public-transport/filtered")
OUT_DIR = Path("../datasets/outputs/zurich-public-transport/small")
OUT_DIR.mkdir(exist_ok=True)

MAX_EDGES = 14000

# -------------------------------------------
# helper
# -------------------------------------------
def row_to_props(row, exclude_cols):
    return {
        k: v
        for k, v in row.items()
        if k not in exclude_cols and pd.notna(v) and v != ""
    }


# -------------------------------------------
# Optionally define allowed lines here
# Set to None or empty set to disable filtering
# -------------------------------------------
# ALLOWED_LINES = {"2", "3", "4", "5", "6"}
ALLOWED_LINES = None  # Uncomment this line to disable filtering and get all lines

# -------------------------------------------
# Step 1 --- Load edges with optional filtering on lines
# -------------------------------------------
print(f"Loading up to {MAX_EDGES} edges" + (f" from lines {sorted(ALLOWED_LINES)}..." if ALLOWED_LINES else " from all lines..."))

edges = []
needed_node_ids = set()

for fname, edge_cfg in ZURICH_PUBLIC_TRANSPORT_CONFIG["edges"].items():
    path = DATA_DIR / fname
    print(f"Reading edges from {fname}")

    src_col = edge_cfg["source_col"]
    tgt_col = edge_cfg["target_col"]
    edge_label = edge_cfg["edge_label"]

    for chunk in pd.read_csv(path, dtype=str, chunksize=50_000):
        chunk = chunk.fillna("")

        # Determine the column with line info
        line_col = "linie"
        if line_col not in chunk.columns:
            raise ValueError(f"Column '{line_col}' not found in {fname}")

        # Filter edges by allowed lines if filtering is active
        if ALLOWED_LINES:
            filtered_chunk = chunk[chunk[line_col].isin(ALLOWED_LINES)]
        else:
            filtered_chunk = chunk

        for _, row in filtered_chunk.iterrows():
            if len(edges) >= MAX_EDGES:
                break

            src = row[src_col]
            tgt = row[tgt_col]
            if not src or not tgt:
                continue

            props = row_to_props(row, exclude_cols=[src_col, tgt_col])
            edges.append((src, tgt, edge_label, props))

            needed_node_ids.add(src)
            needed_node_ids.add(tgt)

        if len(edges) >= MAX_EDGES:
            break

print(f"Collected {len(edges)} edges involving {len(needed_node_ids)} nodes.")


# -------------------------------------------
# Step 2 — collect only required nodes
# -------------------------------------------
all_nodes = {}

print("Loading only required nodes...")

for fname, node_cfg in ZURICH_PUBLIC_TRANSPORT_CONFIG["nodes"].items():
    path = DATA_DIR / fname
    print(f"Scanning nodes from {fname}")

    id_col = node_cfg["id_col"]
    label = node_cfg["label"]

    for chunk in pd.read_csv(path, dtype=str, chunksize=50_000):
        chunk = chunk.fillna("")

        filtered = chunk[chunk[id_col].isin(needed_node_ids)]

        for _, row in filtered.iterrows():
            node_id = row[id_col]
            props = row_to_props(row, exclude_cols=[id_col])
            props["label"] = label

            if node_id not in all_nodes:
                all_nodes[node_id] = props
            else:
                all_nodes[node_id].update(props)

print(f"Loaded {len(all_nodes)} nodes.")


# -------------------------------------------
# Step 3 — export nodes
# -------------------------------------------
with open(OUT_DIR / "nodes.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id:ID", "properties:JSON", ":LABEL"])

    for nid, props in all_nodes.items():
        label = props.pop("label", "Entity")
        props_json = json.dumps(props, ensure_ascii=False)
        writer.writerow([nid, props_json, label])


# -------------------------------------------
# Step 4 — export edges
# -------------------------------------------
with open(OUT_DIR / "edges.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([":START_ID", ":END_ID", ":TYPE", "properties:JSON"])

    for src, tgt, label, props in edges:
        props_json = json.dumps(props, ensure_ascii=False)
        writer.writerow([src, tgt, label, props_json])

print("Done!")
print(f"Exported {len(all_nodes)} nodes and {len(edges)} edges.")
