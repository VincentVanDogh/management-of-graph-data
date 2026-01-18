class CsvRepository:
    def __init__(self, db):
        self.collection = db["csv_files"]

    def create(self, csv_meta: dict):
        self.collection.insert_one(csv_meta)

    def find_by_dataset(self, dataset_id: str):
        return list(self.collection.find({
            "dataset_id": dataset_id
        }))

    def delete_all(self):
        return self.collection.delete_many({})
