from fastapi import FastAPI
from pathlib import Path
import json

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
GRAPH_DIR = BASE_DIR / "property_graphs"
JSON_PATH = GRAPH_DIR / "communities.json"


@app.get("/property-graph/communities")
async def get_property_graph():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)
    return graph
