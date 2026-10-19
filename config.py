"""Project configuration for within-country tweet network analysis."""

from pathlib import Path

# Change this value for each country dataset.
COUNTRY = "iran"

# Folder containing the raw tweet CSV files, relative to the project root.
# Example: Path("data") / "ven2"
INPUT_FOLDER = Path("data") / "ven2"

# Folder used for generated files.
OUTPUT_FOLDER = Path("output")

# Optional existing master pickle file. Set to None to build from CSV files.
# Example: Path("data") / "iran_complete1.pkl"
MASTER_PICKLE = None

# The original notebook used these zero-based positions in the source CSV.
# Confirm that your source CSV schema has not changed before processing.
SOURCE_COLUMNS = {
    "userid": 1,
    "replyid": 16,
    "retweetid": 19,
    "mentions": 29,
    "tweetDate": 13,
    "accountDate": 9,
    "tweetClient": 14,
    "text": 12,
}

# Source CSV rows must contain at least this many columns to use all fields above.
MIN_SOURCE_COLUMN_COUNT = max(SOURCE_COLUMNS.values()) + 1
