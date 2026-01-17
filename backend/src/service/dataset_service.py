from typing import List
from pathlib import Path
from datetime import datetime
import csv
import uuid

from fastapi import UploadFile, HTTPException

from repository.dataset_repository import DatasetRepository
from repository.csv_repository import CsvRepository
from repository.schema_repository import SchemaRepository


class DatasetService:

    def __init__(
        self,
        dataset_repo: DatasetRepository,
        csv_repo: CsvRepository,
        schema_repo: SchemaRepository
    ):
        self.dataset_repo = dataset_repo
        self.csv_repo = csv_repo
        self.schema_repo = schema_repo

    async def create_dataset_with_schema(
        self,
        dataset_name: str,
        files: List[UploadFile],
        schema: dict
    ):
        dataset_id = str(uuid.uuid4())
        dataset_dir = f"./data/{dataset_id}"

        dataset = self.dataset_repo.create({
            "_id": dataset_id,  # optional – only if you want string IDs
            "name": dataset_name,
            "created_at": datetime.utcnow(),
            "status": "UPLOADED",
            "storage_path": dataset_dir
        })

        dataset_id = dataset["_id"]

        # 2. Persist node & edge schemas
        self.schema_repo.save_node_types(dataset_id, schema["nodeTypes"])
        self.schema_repo.save_edge_types(dataset_id, schema["edgeTypes"])

        # 3. Store CSV files + metadata
        for file in files:
            await self._store_csv_file(dataset_id, file)

        return dataset

    async def _store_csv_file(self, dataset_id, file: UploadFile):
        dataset_dir = Path(f"./data/{dataset_id}")
        dataset_dir.mkdir(parents=True, exist_ok=True)

        file_path = dataset_dir / file.filename

        # Save file to disk
        content = await file.read()
        file_path.write_bytes(content)

        # Detect delimiter + headers
        with open(file_path, encoding="utf-8", newline="") as f:
            sample = f.read(4096)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            reader = csv.reader(f, delimiter=dialect.delimiter)
            headers = next(reader)

        # Save CSV metadata
        self.csv_repo.create({
            "dataset_id": dataset_id,
            "filename": file.filename,
            "stored_path": str(file_path),
            "delimiter": dialect.delimiter,
            "headers": headers,
            "uploaded_at": datetime.utcnow()
        })

    def get_dataset(self, dataset_id: str):

        dataset = self.dataset_repo.find_by_id(dataset_id)
        if not dataset:
            return None

        node_types = self.schema_repo.find_node_types(dataset_id)
        edge_types = self.schema_repo.find_edge_types(dataset_id)
        csv_files = self.csv_repo.find_by_dataset(dataset_id)

        # Convert Mongo ObjectId → string
        dataset["id"] = str(dataset["_id"])
        del dataset["_id"]

        def normalize(docs):
            for d in docs:
                d["id"] = str(d["_id"])
                del d["_id"]
            return docs

        return {
            **dataset,
            "nodeTypes": normalize(node_types),
            "edgeTypes": normalize(edge_types),
            "csvFiles": normalize(csv_files)
        }

    def get_all_datasets(self):
        datasets = self.dataset_repo.find_all()

        return [
            {
                "id": str(d["_id"]),
                "name": d["name"],
                "status": d.get("status"),
                "created_at": d.get("created_at")
            }
            for d in datasets
        ]

    def get_dataset_by_name(self, name: str):
        dataset = self.dataset_repo.find_by_name(name)

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        return {
            "id": str(dataset["_id"]),
            "name": dataset["name"],
            "status": dataset.get("status"),
            "created_at": dataset.get("created_at")
        }