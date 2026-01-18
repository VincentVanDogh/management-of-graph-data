# rdf_builder.py
import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF
import os

EX = Namespace("http://example.org/zurich/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

def build_rdf(df: pd.DataFrame, out_path="output/zurich.ttl") -> str:
    g = Graph()
    g.bind("ex", EX)
    g.bind("geo", GEO)

    for _, row in df.iterrows():
        station_uri = EX[f"station/{row['halt_id']}"]

        g.add((station_uri, RDF.type, EX.Station))
        g.add((station_uri, EX.hasName, Literal(row["halt_lang"])))

        if "linien" in df.columns and pd.notna(row["linien"]):
            for line in str(row["linien"]).split(","):
                line_uri = EX[f"line/{line.strip()}"]
                g.add((station_uri, EX.servedByLine, line_uri))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    g.serialize(out_path, format="turtle")
    print(f"RDF saved to {out_path}")
    return out_path
