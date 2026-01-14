class SchemaRepository:
    def __init__(self, db):
        self.node_types = db["node_types"]
        self.edge_types = db["edge_types"]

    def save_node_types(self, dataset_id, node_types):
        for n in node_types:
            self.node_types.insert_one({
                "dataset_id": dataset_id,
                "label": n["label"],
                "id_column": n["idColumn"],
                "properties": n["properties"]
            })

    def save_edge_types(self, dataset_id, edge_types):
        for e in edge_types:
            self.edge_types.insert_one({
                "dataset_id": dataset_id,
                "label": e["label"],
                "start_id_column": e["startIdColumn"],
                "end_id_column": e["endIdColumn"],
                "properties": e["properties"]
            })

    def find_node_types(self, dataset_id: str):
        return list(self.node_types.find({
            "dataset_id": dataset_id
        }))

    def find_edge_types(self, dataset_id: str):
        return list(self.edge_types.find({
            "dataset_id": dataset_id
        }))