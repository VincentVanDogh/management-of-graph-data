ZURICH_PUBLIC_TRANSPORT_CONFIG = {
    "nodes": {
        "haltestelle.csv": {
            "id_col": "halt_id",
            "label": "Stop"
        },
        "haltepunkt.csv": {
            "id_col": "halt_punkt_id",
            "label": "StopPoint"
        }
    },
    "edges": {
        "fahrzeitensollist1.csv": {
            "source_col": "halt_id_von",
            "target_col": "halt_id_nach",
            "edge_label": "CONNECTED_BY"
        },
        "fahrzeitensollist2.csv": {
            "source_col": "halt_id_von",
            "target_col": "halt_id_nach",
            "edge_label": "CONNECTED_BY"
        }
    }
}