import csv
import os
from typing import List
from rdflib import Graph, URIRef, Literal

from pathlib import Path
from fastapi import FastAPI, HTTPException, Form
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
import json
from flask import Flask, request, jsonify

from fastapi import UploadFile, File, Depends

from service.graph_pipeline import GraphPipeline
from service.property_graph_query import PropertyGraphQuery
from src.endpoint.dependencies import get_dataset_service, get_neo4j
from src.service.dataset_service import DatasetService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Neo4j driver once
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "mogm1234"))

# Create a Redis connection
redis_client = Redis(host="localhost", port=6379, decode_responses=True)

class QueryRequest(BaseModel):
    query: str

# Dependency to provide PropertyGraphQuery service instance
def get_property_graph_query():
    service = PropertyGraphQuery(driver, redis_client)
    try:
        yield service
    finally:
        pass  # Could do cleanup here if needed

# TODO: Change it to a GET-request, where the "MATCH ..." request is param, not in the JSON body
@app.post("/cypher")
def run_cypher(
    request: QueryRequest,
    service: PropertyGraphQuery = Depends(get_property_graph_query)
):
    return {
        "results": service.run_cypher_query(request.query),
        "queries": service.get_query_list(request.query)
    }

@app.get("/queries")
def get_queries(limit: int = 50):
    raw = redis_client.lrange("query_history", 0, limit - 1)
    parsed = [json.loads(e) for e in raw]
    return {"queries": parsed}

@app.delete("/queries")
def clear_queries():
    redis_client.delete("query_history")
    return {"status": "cleared"}

@app.on_event("shutdown")
def shutdown_event():
    driver.close()


@app.post("/schema_datasets")
async def upload_dataset(
    files: List[UploadFile] = File(...),
    schema: str = Form(...),
    mongodb_service: DatasetService = Depends(get_dataset_service),
    dataset_service=Depends(get_dataset_service),
    neo4j = Depends(get_neo4j),
):
    schema_dict = json.loads(schema)

    print("Schema:", schema_dict)
    print("Files:", [f.filename for f in files])

    dataset = await mongodb_service.create_dataset_with_schema(
        dataset_name=schema_dict["datasetName"],
        files=files,
        schema=schema_dict
    )

    dataset_id = str(dataset["_id"])  # Assuming dataset has an "id" field after creation

    dataset = dataset_service.get_dataset(dataset_id)

    schema_for_build = {
        "nodeTypes": dataset.get("nodeTypes", []),
        "edgeTypes": dataset.get("edgeTypes", [])
    }
    csv_files = dataset.get("csvFiles", [])
    if not csv_files:
        raise HTTPException(status_code=400, detail="No CSV files found")

    csv_path_map = {
        f["filename"]: str(Path(f["stored_path"]).resolve())
        for f in csv_files
    }

    pipeline = GraphPipeline(neo4j)

    pipeline.build_graph(csv_path_map, schema_for_build)
    mongodb_service.mark_graph_built(dataset_id)

    return {
        "message": "Dataset uploaded and graph creation started successfully",
        "files": [f.filename for f in files],
        "schema": schema_dict
    }

@app.get("/schema_datasets/by-name")
def get_dataset_by_name(
    name: str,
    dataset_service: DatasetService = Depends(get_dataset_service)
):
    print(f"Searching for dataset by name: {name}")
    dataset = dataset_service.get_dataset_by_name(name)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@app.get("/schema_datasets/{dataset_id}")
def get_dataset(
    dataset_id: str,
    dataset_service = Depends(get_dataset_service)
):
    dataset = dataset_service.get_dataset(dataset_id)

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return dataset

@app.get("/schema_datasets")
def get_all_datasets(
    dataset_service = Depends(get_dataset_service)
):
    return dataset_service.get_all_datasets()

@app.get("/schema_datasets/name/{name}")
def get_dataset_by_name(
    name: str,
    dataset_service = Depends(get_dataset_service)
):
    return dataset_service.get_dataset_by_name(name)


@app.delete("/admin/datasets")
def delete_all_datasets(
    dataset_service: DatasetService = Depends(get_dataset_service)
):
    result = dataset_service.delete_all_datasets()
    return result

#######################
# RDF
#######################

# -------------------------------
# Load RDF data
# -------------------------------
BASE_DIR = os.path.dirname(__file__)
RDF_FILE = os.path.join(BASE_DIR, "output", "zurich.ttl")
RESULT_FILE = os.path.join(BASE_DIR, "output", "result.json")  # file to save query results

if not os.path.exists(RDF_FILE):
    raise FileNotFoundError("zurich.ttl not found. Please make sure it exists in output/")

g = Graph()
g.parse(RDF_FILE, format="ttl")
print(f"Loaded RDF graph with {len(g)} triples")

# -------------------------------
# POST /query
# Accepts SPARQL query in JSON { "query": "..." }
# Returns nodes and edges for vis-network and saves to a file
# -------------------------------
@app.route("/query", methods=["POST"])
def run_sparql():
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 415

    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        results = g.query(query)

        # Collect nodes and edges
        nodes_dict = {}
        edges = []

        for row in results:
            # Add each value as a node
            for val in row:
                if isinstance(val, (URIRef, Literal)):
                    val_str = str(val)
                    if val_str not in nodes_dict:
                        label = val_str.split('/')[-1] if isinstance(val, URIRef) else str(val)
                        nodes_dict[val_str] = {"id": val_str, "label": label}

            # If at least 2 columns, create edge from first -> second
            if len(row) >= 2:
                source = str(row[0])
                target = str(row[1])
                label = str(row[1]).split('/')[-1] if isinstance(row[1], URIRef) else str(row[1])
                edges.append({"source": source, "target": target, "label": label})

        # Prepare final data
        output_data = {"nodes": list(nodes_dict.values()), "edges": edges}

        # Save to file
        os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        print(f"Query result saved to {RESULT_FILE}")

        return jsonify(output_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# -------------------------------
# Optional: GET full graph
# -------------------------------
@app.route("/graph", methods=["GET"])
def get_full_graph():
    nodes_dict = {}
    edges = []

    for s, p, o in g:
        for val in (s, o):
            val_str = str(val)
            if val_str not in nodes_dict:
                label = val_str.split('/')[-1] if isinstance(val, URIRef) else str(val)
                nodes_dict[val_str] = {"id": val_str, "label": label}

        edges.append({"source": str(s), "target": str(o), "label": str(p).split('/')[-1]})

    return jsonify({"nodes": list(nodes_dict.values()), "edges": edges})
