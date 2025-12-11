from neo4j import GraphDatabase

try:
    # neo4j driver provides these graph types
    from neo4j.graph import Node, Relationship, Path
except Exception:
    # fallback names if package layout differs
    Node = Relationship = Path = object

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
            # normalize every record into a flat list of {a,r,b,...} entries
            normalized = []
            for record in result:
                normalized.extend(self._normalize_record(record))
            return normalized

    def _normalize_record(self, record):
        """
        Accepts a Neo4j Record and returns a list of normalized dictionaries
        in form: { "a": {...}, "r": {...} or None, "b": {...} or None, "aName": str, "bName": str }
        """
        nodes = []    # list of driver Node objects or dict-like node props
        rels = []     # list of driver Relationship objects or dict-like rel props
        other = {}    # other scalar/map values to pass through if needed

        # Inspect each value in the record by type
        for key, val in record.items():
            # Path: expand to nodes + relationships
            if isinstance(val, Path):
                # val.nodes and val.relationships are sequences
                for n in val.nodes:
                    nodes.append(n)
                for r in val.relationships:
                    rels.append(r)
            # Node object
            elif isinstance(val, Node):
                nodes.append(val)
            # Relationship object
            elif isinstance(val, Relationship):
                rels.append(val)
            # If it's already a plain dict (e.g., you returned a map in Cypher)
            elif isinstance(val, dict):
                # Heuristic: if it has 'id' or 'halt_lang' treat as node-like
                if "id" in val or "halt_lang" in val or "halt_kurz" in val:
                    nodes.append(val)
                else:
                    other[key] = val
            else:
                # scalar values (strings, numbers) — keep for possible use
                other[key] = val

        normalized = []

        # Case A: we have relationships -> create (a)-[r]->(b) triples
        if rels:
            # if nodes length == len(rels) + 1 (typical for paths), pair them
            if len(nodes) >= len(rels) + 1:
                for i, rel in enumerate(rels):
                    a_node = nodes[i]
                    b_node = nodes[i + 1]
                    normalized.append(self._record_from_objs(a_node, rel, b_node))
            else:
                # fallback: pair first two nodes with first rel if available
                a_node = nodes[0] if nodes else None
                b_node = nodes[1] if len(nodes) > 1 else None
                for rel in rels:
                    normalized.append(self._record_from_objs(a_node, rel, b_node))
        # Case B: only nodes (no relationships)
        elif nodes:
            for n in nodes:
                normalized.append(self._record_from_objs(n, None, None))
        # Case C: nothing node/rel like — try to convert scalar/map into single record
        else:
            # return a single record containing the raw other fields
            normalized.append({
                "a": None,
                "r": None,
                "b": None,
                "aName": None,
                "bName": None,
                "raw": other
            })

        return normalized

    def _node_to_dict(self, node):
        """Convert driver Node or plain dict to serializable dict including id."""
        if node is None:
            return None
        # driver Node has .id and .items() or mapping behaviour
        try:
            # Attempt to read attributes typical for neo4j Node
            props = dict(node)
            # include id (numeric driver id or provided 'id' prop)
            nid = None
            if hasattr(node, "id"):
                nid = node.id
            elif "id" in props:
                nid = props.get("id")
            # ensure string id for frontend (consistent)
            if nid is not None:
                props["id"] = str(nid)
            return props
        except Exception:
            # If it's already a dict
            if isinstance(node, dict):
                node = dict(node)
                if "id" in node:
                    node["id"] = str(node["id"])
                return node
            # unknown type: try to stringify
            return {"id": str(node), "value": str(node)}

    def _rel_to_dict(self, rel):
        """Convert driver Relationship to serializable dict including type, start/end ids."""
        if rel is None:
            return None
        try:
            props = dict(rel)
        except Exception:
            props = {}
            if isinstance(rel, dict):
                props.update(rel)

        # Try to include relationship identity and endpoints if available
        try:
            if hasattr(rel, "id"):
                props["id"] = str(rel.id)
        except Exception:
            pass

        # relationship .start_node and .end_node or .start and .end depending on driver
        try:
            if hasattr(rel, "start_node") and hasattr(rel.start_node, "id"):
                props["startNode"] = str(rel.start_node.id)
            if hasattr(rel, "end_node") and hasattr(rel.end_node, "id"):
                props["endNode"] = str(rel.end_node.id)
        except Exception:
            # older versions may use .start and .end
            try:
                if hasattr(rel, "start") and hasattr(rel.start, "id"):
                    props["startNode"] = str(rel.start.id)
                if hasattr(rel, "end") and hasattr(rel.end, "id"):
                    props["endNode"] = str(rel.end.id)
            except Exception:
                pass

        # relationship type
        try:
            if hasattr(rel, "type"):
                props["type"] = rel.type
        except Exception:
            pass

        return props

    def _record_from_objs(self, a_obj, r_obj, b_obj):
        """
        Build the normalized dict for one (a)-[r]->(b) triple or node-only record.
        """
        a = self._node_to_dict(a_obj)
        b = self._node_to_dict(b_obj)
        r = self._rel_to_dict(r_obj)

        return {
            "a": a,
            "r": r,
            "b": b,
            "aName": (a.get("halt_lang") if a else None) if isinstance(a, dict) else None,
            "bName": (b.get("halt_lang") if b else None) if isinstance(b, dict) else None,
        }

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