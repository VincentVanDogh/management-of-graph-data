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