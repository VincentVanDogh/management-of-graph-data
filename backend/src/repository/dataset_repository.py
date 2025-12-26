from sqlalchemy.orm import Session
from models.dataset import Dataset

class DatasetRepository:
    def create(self, db: Session, dataset: Dataset):
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    def find_all(self, db: Session):
        return db.query(Dataset).all()

    def find_by_id(self, db: Session, dataset_id: int):
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()

    def delete(self, db: Session, dataset: Dataset):
        db.delete(dataset)
        db.commit()