from database.neo4j import Neo4jService
from src.database.mongo import db

from src.database.database import SessionLocal
from src.repository.dataset_repository import DatasetRepository
from src.repository.csv_repository import CsvRepository
from src.repository.schema_repository import SchemaRepository
from src.service.dataset_service import DatasetService

def get_dataset_service() -> DatasetService:
    dataset_repo = DatasetRepository(db)
    csv_repo = CsvRepository(db)
    schema_repo = SchemaRepository(db)

    return DatasetService(
        dataset_repo=dataset_repo,
        csv_repo=csv_repo,
        schema_repo=schema_repo
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_neo4j():
    neo = Neo4jService(
        uri = "bolt://localhost:7687",
        user = "neo4j",
        password = "mogm1234"
    )
    try:
        yield neo
    finally:
        neo.close()