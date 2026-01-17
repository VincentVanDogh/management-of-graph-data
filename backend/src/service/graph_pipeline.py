from service.node_generator import NodeGenerator
from service.edge_generator import EdgeGenerator
from service.neo4j_writer import Neo4jWriter

class GraphPipeline:

    def __init__(self, neo4j):
        self.node_generator = NodeGenerator()
        self.edge_generator = EdgeGenerator()
        self.neo4j_writer = Neo4jWriter(neo4j)

    def build_graph(self, dataset_dir: str, schema: dict):

        # Nodes
        for node_schema in schema["nodeTypes"]:
            csv_path = f"{dataset_dir}/{node_schema['csvFileName']}"
            nodes = self.node_generator.generate(csv_path, node_schema)
            self.neo4j_writer.create_nodes(nodes)

        # Edges
        for edge_schema in schema["edgeTypes"]:
            csv_path = f"{dataset_dir}/{edge_schema['csvFileName']}"
            edges = self.edge_generator.generate(csv_path, edge_schema)
            self.neo4j_writer.create_edges(edges)
