import os

from repository.dataset_repository import DatasetRepository
from models.dataset import Dataset

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DatasetService:
    def __init__(self, repository: DatasetRepository):
        self.repository = repository

    def upload(self, db, file):
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        dataset = Dataset(
            filename=file.filename,
            stored_path=file_path,
            content_type=file.content_type
        )
        return self.repository.create(db, dataset)

    def list_all(self, db):
        return self.repository.find_all(db)

    def delete(self, db, dataset_id: int):
        dataset = self.repository.find_by_id(db, dataset_id)
        if not dataset:
            return None

        if os.path.exists(dataset.stored_path):
            os.remove(dataset.stored_path)

        self.repository.delete(db, dataset)
        return dataset