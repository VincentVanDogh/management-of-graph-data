from service.node_generator import NodeGenerator
from service.edge_generator import EdgeGenerator
from service.neo4j_writer import Neo4jWriter

class GraphPipeline:

    def __init__(self, neo4j):
        self.node_generator = NodeGenerator()
        self.edge_generator = EdgeGenerator()
        self.neo4j_writer = Neo4jWriter(neo4j)

    def build_graph(self, csv_path_map: dict, schema: dict):

        # Nodes
        for node_schema in schema["nodeTypes"]:
            csv_name = node_schema["csvFileName"]
            csv_path = csv_path_map.get(csv_name)

            if not csv_path:
                raise ValueError(f"CSV not found for node type: {csv_name}")

            print("Loading nodes from:", csv_path)

            nodes = self.node_generator.generate(csv_path, node_schema)
            if nodes:
                self.neo4j_writer.create_nodes(nodes)

        # Edges
        for edge_schema in schema["edgeTypes"]:
            csv_name = edge_schema["csvFileName"]
            csv_path = csv_path_map.get(csv_name)

            if not csv_path:
                raise ValueError(f"CSV not found for edge type: {csv_name}")

            print("Loading edges from:", csv_path)

            edges = self.edge_generator.generate(csv_path, edge_schema)
            if edges:
                self.neo4j_writer.create_edges(edges)