# endpoint/dependencies.py
from database.database import SessionLocal
from repository.dataset_repository import DatasetRepository
from service.dataset_service import DatasetService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_dataset_service():
    repo = DatasetRepository()
    return DatasetService(repo)