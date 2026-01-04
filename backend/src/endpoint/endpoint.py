from typing import List

from fastapi import FastAPI, Depends, UploadFile, HTTPException, Form
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
import time
import json

from service.property_graph_query import PropertyGraphQuery
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from endpoint.dependencies import get_db, get_dataset_service
from service.dataset_service import DatasetService

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
    schema: str = Form(...)
):
    schema_dict = json.loads(schema)

    # Inspect incoming data
    print("Schema:", schema_dict)
    print("Files:", [f.filename for f in files])

    # TODO:
    # - store files
    # - store schema in MongoDB
    # - link CSV filenames to schema entries
    # - upload schema on Neo4j

    return {
        "message": "Dataset uploaded successfully",
        "files": [f.filename for f in files],
        "schema": schema_dict
    }