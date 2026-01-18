ACTORS_AND_MOVIES_CONFIG = {
    "nodes": {
        "names.csv": {
            "id_col": "nconst",
            "label": "Person"
        },
        "titles.csv": {
            "id_col": "tconst",
            "label": "Movie"
        }
    },
    "edges": {
        # Create edges from actors to movies based on 'knownForTitles' list in names.csv
        "names.csv": {
            "source_col": "nconst",
            "target_col": "knownForTitles",
            "edge_label": "ACTED_IN"
        }
    }
}
