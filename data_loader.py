"""Read source tweet CSVs or load an existing master pickle."""

import csv
from pathlib import Path
from typing import Iterable

import pandas as pd

from config import SOURCE_COLUMNS, MIN_SOURCE_COLUMN_COUNT


def read_tweet_csv(path: Path) -> pd.DataFrame:
    """Read selected fields from a source CSV, skipping malformed/repeated headers."""
    records = []

    with path.open("r", encoding="utf-8-sig", newline="") as source:
        # Strip NUL characters because they can make csv.reader fail on some exports.
        cleaned_lines = (line.replace("\0", "") for line in source)
        reader = csv.reader(cleaned_lines)

        for line_number, row in enumerate(reader, start=1):
            if len(row) < MIN_SOURCE_COLUMN_COUNT:
                continue

            record = {
                field: row[index]
                for field, index in SOURCE_COLUMNS.items()
            }

            # Some source files contain a header row in the body.
            if record["userid"].strip().lower() == "userid":
                continue

            records.append(record)

    return pd.DataFrame.from_records(records, columns=SOURCE_COLUMNS.keys())


def build_master_dataframe(folder: Path) -> pd.DataFrame:
    """Load all CSV files in a folder and concatenate them into one DataFrame."""
    folder = Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"Input folder does not exist: {folder.resolve()}")

    csv_files = sorted(folder.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in: {folder.resolve()}")

    frames = []
    for path in csv_files:
        print(f"Reading {path.name}...")
        frames.append(read_tweet_csv(path))

    master = pd.concat(frames, ignore_index=True)
    print(f"Loaded {len(master):,} rows from {len(csv_files)} CSV file(s).")
    return master


def load_tweets(master_pickle: Path | None = None, input_folder: Path | None = None) -> pd.DataFrame:
    """Load a master pickle if provided; otherwise build the DataFrame from CSV files."""
    if master_pickle is not None:
        master_pickle = Path(master_pickle)
        if not master_pickle.exists():
            raise FileNotFoundError(f"Master pickle does not exist: {master_pickle.resolve()}")
        print(f"Loading master pickle: {master_pickle}")
        data = pd.read_pickle(master_pickle)
    else:
        if input_folder is None:
            raise ValueError("Provide input_folder when master_pickle is not set.")
        data = build_master_dataframe(Path(input_folder))

    required = {"userid", "replyid", "retweetid", "tweetDate", "text"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Input data is missing required columns: {sorted(missing)}")

    # Normalize interaction ID fields to strings and missing values to empty strings.
    for column in ("userid", "replyid", "retweetid"):
        data[column] = data[column].fillna("").astype(str).str.strip()

    # Remove repeated source header rows if they were present in a master pickle.
    data = data.loc[data["userid"].str.lower().ne("userid")].copy()
    return data
