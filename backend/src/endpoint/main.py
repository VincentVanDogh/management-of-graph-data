# main.py
from data_loader import load_zurich_dataset
from rdf_builder import build_rdf
from rdf_exporter import export_rdf_to_json
from shacl_validator import validate_rdf

def main():
    print("Loading Zurich dataset...")
    df = load_zurich_dataset("haltestelle.csv")
    print("Dataset loaded.")

    print("Building RDF graph...")
    rdf_path = build_rdf(df)

    print("Exporting RDF → JSON...")
    export_rdf_to_json(rdf_path)

    print("Validating RDF with SHACL (C3)...")
    validate_rdf()
    print("Done! Start Flask with: python api.py")

if __name__ == "__main__":
    main()
