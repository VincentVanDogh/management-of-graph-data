from fastapi import FastAPI, Depends
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
import time
import json

from src.service.property_graph_query import PropertyGraphQuery

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
    service = PropertyGraphQuery(driver)
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
    # Store query in Redis (as JSON with timestamp)
    entry = {
        "query": request.query,
        "timestamp": time.time()
    }
    redis_client.lpush("query_history", json.dumps(entry))

    # Get query result
    data = service.run_cypher_query(request.query)

    # Get redis queries
    raw_queries = redis_client.lrange("query_history", 0, 10)
    queries = [json.loads(e) for e in raw_queries]

    return {
        "results": data,
        "queries": queries
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
