import csv
from typing import List

from fastapi import FastAPI, HTTPException, Form
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
import json

from service.deprecated.property_graph_query import PropertyGraphQuery
from fastapi import UploadFile, File, Depends
from sqlalchemy.orm import Session

from service.graph_pipeline import GraphPipeline
from src.endpoint.dependencies import get_db, get_dataset_service, get_neo4j
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

# TODO: Change it to a GET-request, where the "MATCH ..." request is paramt, not in the JSON body
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

@app.post("/upload")
def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    service: DatasetService = Depends(get_dataset_service)
):
    return service.upload(db, file)

@app.get("/csv-list")
def list_datasets(
    db: Session = Depends(get_db),
    service: DatasetService = Depends(get_dataset_service)
):
    return service.list_all(db)

@app.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    service: DatasetService = Depends(get_dataset_service)
):
    deleted = service.delete(db, dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"deleted": dataset_id}

@app.get("/datasets/{dataset_id}/content")
def get_dataset_content(
    dataset_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    service: DatasetService = Depends(get_dataset_service)
):
    return service.get_csv_content(db, dataset_id, limit)

@app.post("/schema_datasets")
async def upload_dataset(
    files: List[UploadFile] = File(...),
    schema: str = Form(...),
    mongodb_service: DatasetService = Depends(get_dataset_service)
):
    schema_dict = json.loads(schema)

    # Inspect incoming data
    print("Schema:", schema_dict)
    print("Files:", [f.filename for f in files])

    dataset = await mongodb_service.create_dataset_with_schema(
        dataset_name=schema_dict["datasetName"],
        files=files,
        schema=schema_dict
    )

    return {
        "message": "Dataset uploaded successfully",
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


from pathlib import Path

@app.post("/datasets/{dataset_id}/build-graph")
def build_graph(
    dataset_id: str,
    dataset_service = Depends(get_dataset_service),
    neo4j = Depends(get_neo4j)
):
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    print(dataset)

    schema = {
        "nodeTypes": dataset.get("nodeTypes", []),
        "edgeTypes": dataset.get("edgeTypes", [])
    }

    csv_files = dataset.get("csvFiles", [])
    if not csv_files:
        raise HTTPException(status_code=400, detail="No CSV files found")

    # Build filename: absolute path map
    csv_path_map = {
        f["filename"]: str(Path(f["stored_path"]).resolve())
        for f in csv_files
    }

    print("CSV PATH MAP:", csv_path_map)

    pipeline = GraphPipeline(neo4j)
    pipeline.build_graph(csv_path_map, schema)

    dataset_service.mark_graph_built(dataset_id)

    return {"status": "Graph created successfully"}



@app.delete("/admin/datasets")
def delete_all_datasets(
    dataset_service: DatasetService = Depends(get_dataset_service)
):
    result = dataset_service.delete_all_datasets()
    return result
