from bson import ObjectId


class DatasetRepository:
    def __init__(self, db):
        self.collection = db["datasets"]

    def create(self, dataset: dict):
        result = self.collection.insert_one(dataset)
        dataset["_id"] = result.inserted_id
        return dataset

    def find_by_id(self, dataset_id: str):
        return self.collection.find_one({
            "_id": ObjectId(dataset_id)
        })

    def find_all(self):
        return list(self.collection.find())

    def find_by_name(self, name: str):
        return self.collection.find_one({"name": name})
