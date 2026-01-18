from utils.csv_reader import read_csv

class EdgeGenerator:
    def generate(self, csv_path: str, edge_schema: dict):
        rows = read_csv(csv_path)
        edges = []

        for row in rows:
            props = {}
            for p in edge_schema["properties"]:
                props[p] = row.get(p)

            edges.append({
                "label": edge_schema["label"],
                "start_id": row[edge_schema["start_id_column"]],
                "end_id": row[edge_schema["end_id_column"]],
                "properties": props
            })

        return edges
