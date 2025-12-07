import pandas as pd
from pathlib import Path

# Paths
DATA_DIR = Path("../datasets/inputs/zurich-public-transport")
INPUT_FILES = ["fahrzeitensollist1.csv", "fahrzeitensollist2.csv"]

OUTPUT_DIR = DATA_DIR / "filtered"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Includes timestamps
columns_to_keep = [
    "linie",
    "richtung",
    "kurs",
    "seq_von",
    "halt_diva_von",
    "halt_kurz_von1",
    "soll_an_von",
    "ist_an_von",
    "soll_ab_von",
    "ist_ab_von",
    "seq_nach",
    "halt_diva_nach",
    "halt_kurz_nach1",
    "soll_an_nach",
    "ist_an_nach1",
    "soll_ab_nach",
    "ist_ab_nach",
    "fahrt_id",
    "fahrweg_id",
    "fw_no",
    "fw_typ",
    "fw_kurz",
    "fw_lang",
    "halt_id_von",
    "halt_id_nach",
]

# No timestamps (reduces dataset by 50%, instead of ~1_400_000 rows, just ~700_000
columns_to_keep_no_timestamps = [
    "linie",
    "richtung",
    "kurs",
    "seq_von",
    "halt_diva_von",
    "halt_kurz_von1",
    "seq_nach",
    "halt_diva_nach",
    "halt_kurz_nach1",
    "fahrt_id",
    "fahrweg_id",
    "fw_no",
    "fw_typ",
    "fw_kurz",
    "fw_lang",
    "halt_id_von",
    "halt_id_nach",
]

columns_to_keep_no_timestamps_custom = [
    "linie",
    "richtung",
    "kurs",
    "seq_von",
    "seq_nach",
    "fahrweg_id",
    "fw_no",
    "fw_typ",
    "fw_lang",
    "halt_id_von",
    "halt_id_nach",
]


for filename in INPUT_FILES:
    input_path = DATA_DIR / filename
    output_path = OUTPUT_DIR / f"{filename.rstrip('.csv')}.csv"

    print(f"Processing {input_path}...")

    # Load CSV with only needed columns
    df = pd.read_csv(input_path, usecols=columns_to_keep_no_timestamps_custom, dtype=str)

    print(f"Original rows: {len(df)}")

    # Drop duplicates
    df = df.drop_duplicates()

    print(f"Rows after duplicates removed: {len(df)}")

    # Save filtered CSV
    df.to_csv(output_path, index=False)

    print(f"Saved filtered file to {output_path}\n")

print("All files processed.")
