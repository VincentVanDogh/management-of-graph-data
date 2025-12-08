from neo4j import GraphDatabase

class PropertyGraphQuery:
    def __init__(self, driver):
        self.driver = driver

    def get_zurich_public_transport(self):
        query = """
        MATCH (a)-[r:CONNECTED_BY]->(b)
        RETURN a, r, b,
               a.halt_lang AS aName,
               b.halt_lang AS bName
        LIMIT 500
        """

        def work(tx):
            result = tx.run(query)
            records = []
            for record in result:
                records.append({
                    "a": dict(record["a"]),
                    "r": dict(record["r"]),
                    "b": dict(record["b"]),
                    "aName": record["aName"],
                    "bName": record["bName"],
                })
            return records

        with self.driver.session() as session:
            return session.execute_read(work)

    def run_cypher_query(self, query: str):
        with self.driver.session() as session:
            result = session.run(query)
            return [
                {key: value for key, value in record.items()}
                for record in result
            ]

    def run_shortest_path(self):
        query = """
            MATCH p = shortestPath((start {halt_kurz: 'REHA'})-[*]-(end {halt_kurz: 'SIGN'}))
            RETURN p
        """
        with self.driver.session() as session:
            result = session.run(query)
            return self._normalize_path(result)

    def _normalize_path(self, result):
        output = []

        for record in result:
            path = record["p"]

            nodes = path.nodes
            rels = path.relationships

            # convert into (a)-[r]->(b) triples
            for i, rel in enumerate(rels):
                a = nodes[i]
                b = nodes[i + 1]

                output.append({
                    "a": dict(a),
                    "b": dict(b),
                    "r": dict(rel),
                    "aName": a.get("halt_lang"),
                    "bName": b.get("halt_lang"),
                })

        return output


"""
QUERIES:
    MATCH (a)-[r:CONNECTED_BY]->(b) RETURN a, r, b, a.halt_lang AS aName, b.halt_lang AS bName LIMIT 20;
    ------------------------------------------------------------------------------------------
    MATCH p = shortestPath((start {halt_kurz: $start})-[*]-(end {halt_kurz: $end})) RETURN p
"""