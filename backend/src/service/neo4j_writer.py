class Neo4jWriter:

    def __init__(self, neo4j):
        self.neo4j = neo4j

    def create_nodes(self, nodes):
        query = """
        UNWIND $nodes AS n
        MERGE (x:`%s` {id: n.properties.id})
        SET x += n.properties
        """ % nodes[0]["label"]

        self.neo4j.run_query(query, {"nodes": nodes})

    def create_edges(self, edges):
        query = """
        UNWIND $edges AS e
        MATCH (a {id: e.start_id})
        MATCH (b {id: e.end_id})
        MERGE (a)-[r:`%s`]->(b)
        SET r += e.properties
        """ % edges[0]["label"]

        self.neo4j.run_query(query, {"edges": edges})
