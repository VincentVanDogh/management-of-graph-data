from fastapi import FastAPI, Depends
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

class QueryRequest(BaseModel):
    query: str

# Dependency to provide PropertyGraphQuery service instance
def get_property_graph_query():
    service = PropertyGraphQuery(driver)
    try:
        yield service
    finally:
        pass  # Could do cleanup here if needed

@app.get("/zurich-transport")
def zurich_transport(service: PropertyGraphQuery = Depends(get_property_graph_query)):
    data = service.get_zurich_public_transport()
    return {"results": data}

# TODO: Change it to a GET-request, where the "MATCH ..." request is paramt, not in the JSON body
@app.post("/cypher")
def run_cypher(
    request: QueryRequest,
    service: PropertyGraphQuery = Depends(get_property_graph_query)
):
    data = service.run_cypher_query(request.query)
    return {"results": data}

@app.post("/cypher_shortest_path")
def run_cypher(
    request: QueryRequest,
    service: PropertyGraphQuery = Depends(get_property_graph_query)
):
    data = service.run_shortest_path()
    return {"results": data}

@app.on_event("shutdown")
def shutdown_event():
    driver.close()
