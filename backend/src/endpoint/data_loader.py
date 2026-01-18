# data_loader.py
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd

def load_zurich_dataset(file_path: str) -> pd.DataFrame:
    """
    Load the Zurich public transport dataset (haltestelle.csv) as a Pandas DataFrame.
    """
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "laa283/zurich-public-transport",
        file_path
    )
    return df
