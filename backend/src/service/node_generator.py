from utils.csv_reader import read_csv

class NodeGenerator:
    def generate(self, csv_path: str, node_schema: dict):
        rows = read_csv(csv_path)
        nodes = []

        for row in rows:
            node_id = row[node_schema["idColumn"]]

            props = {
                "id": node_id
            }

            for p in node_schema["properties"]:
                props[p] = row.get(p)

            nodes.append({
                "label": node_schema["label"],
                "properties": props
            })

        return nodes
