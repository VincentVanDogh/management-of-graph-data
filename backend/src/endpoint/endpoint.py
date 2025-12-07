from fastapi import FastAPI, Depends
from neo4j import GraphDatabase

from src.service.property_graph_query import PropertyGraphQuery

app = FastAPI()

# Create Neo4j driver once
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "mogm1234"))

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

@app.on_event("shutdown")
def shutdown_event():
    driver.close()
