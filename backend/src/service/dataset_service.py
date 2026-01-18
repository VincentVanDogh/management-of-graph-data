import shutil
from typing import List
from pathlib import Path
from datetime import datetime
import csv
import uuid

from bson import ObjectId
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
        dataset_dir = f"./data/{dataset_name}"

        dataset = self.dataset_repo.create({
            "name": dataset_name,
            "created_at": datetime.utcnow(),
            "status": "UPLOADED",
            "storage_path": dataset_dir,
            "has_graph": False
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

        try:
            dataset_obj_id = ObjectId(dataset_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid dataset id")

        dataset = self.dataset_repo.find_by_id(dataset_obj_id)
        if not dataset:
            return None

        node_types = self.schema_repo.find_node_types(dataset_obj_id)
        edge_types = self.schema_repo.find_edge_types(dataset_obj_id)
        csv_files = self.csv_repo.find_by_dataset(dataset_obj_id)

        # Normalize dataset itself
        dataset["id"] = str(dataset["_id"])
        del dataset["_id"]

        return {
            **dataset,
            "nodeTypes": self.normalize(node_types),
            "edgeTypes": self.normalize(edge_types),
            "csvFiles": self.normalize(csv_files)
        }

    def normalize(self, docs):
        def convert_obj_ids(obj):
            if isinstance(obj, list):
                return [convert_obj_ids(i) for i in obj]
            elif isinstance(obj, dict):
                new_obj = {}
                for k, v in obj.items():
                    if isinstance(v, ObjectId):
                        new_obj[k] = str(v)
                    else:
                        new_obj[k] = convert_obj_ids(v)
                return new_obj
            elif isinstance(obj, ObjectId):
                return str(obj)
            else:
                return obj

        normalized_docs = []
        for d in docs:
            # Convert top-level _id to id string
            if "_id" in d:
                d["id"] = str(d["_id"])
                del d["_id"]
            normalized_docs.append(convert_obj_ids(d))
        return normalized_docs

    def get_all_datasets(self):
        datasets = self.dataset_repo.find_all()

        result = []
        for d in datasets:
            dataset_id = d["_id"]
            node_types = self.schema_repo.find_node_types(dataset_id)
            edge_types = self.schema_repo.find_edge_types(dataset_id)
            csv_files = self.csv_repo.find_by_dataset(dataset_id)

            result.append({
                "id": str(dataset_id),
                "name": d["name"],
                "status": d.get("status"),
                "created_at": d.get("created_at"),
                "has_graph": d.get("has_graph", False),
                "nodeTypes": self.normalize(node_types),
                "edgeTypes": self.normalize(edge_types),
                "csvFiles": self.normalize(csv_files)
            })
        return result

    def get_dataset_by_name(self, name: str):
        dataset = self.dataset_repo.find_by_name(name)

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        dataset_id = dataset["_id"]

        node_types = self.schema_repo.find_node_types(dataset_id)
        edge_types = self.schema_repo.find_edge_types(dataset_id)
        csv_files = self.csv_repo.find_by_dataset(dataset_id)

        return {
            "id": str(dataset_id),
            "name": dataset["name"],
            "status": dataset.get("status"),
            "created_at": dataset.get("created_at"),
            "has_graph": dataset.get("has_graph", False),
            "nodeTypes": self.normalize(node_types),
            "edgeTypes": self.normalize(edge_types),
            "csvFiles": self.normalize(csv_files)
        }

    def mark_graph_built(self, dataset_id: str):
        self.dataset_repo.set_has_graph(dataset_id, True)

    def delete_all_datasets(self):
        # Delete MongoDB collections
        self.csv_repo.delete_all()
        self.schema_repo.delete_all_node_types()
        self.schema_repo.delete_all_edge_types()
        self.dataset_repo.delete_all()

        # Optional: delete stored CSV files on disk
        data_dir = Path("./data")
        if data_dir.exists():
            shutil.rmtree(data_dir)
            data_dir.mkdir(exist_ok=True)

        return {"status": "All datasets deleted"}
