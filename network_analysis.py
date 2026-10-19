"""Retweet/reply statistics and country-collection network exports."""

from pathlib import Path

import pandas as pd

from exports import ensure_output_folder, export_interaction_network


def _percent(part: int, total: int) -> float:
    """Percentage with safe handling for empty groups."""
    return round(part / total * 100, 2) if total else 0.0


def analyze_interaction_network(
    data: pd.DataFrame,
    interaction_column: str,
    interaction_name: str,
    output_prefix: str,
    output_folder: Path,
) -> dict:
    """Analyze retweets or replies and export interactions inside/outside the collection."""
    required = {"userid", interaction_column, "tweetDate", "text"}
    missing = required.difference(data.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    # Work on a copy so the caller's DataFrame is not mutated.
    clean = data.drop_duplicates().copy()
    clean["userid"] = clean["userid"].fillna("").astype(str).str.strip()
    clean[interaction_column] = clean[interaction_column].fillna("").astype(str).str.strip()

    original_rows = len(data)
    deduplicated_rows = len(clean)
    unique_ids = clean.loc[clean["userid"].ne(""), "userid"].drop_duplicates()
    known_ids = set(unique_ids)

    interactions = clean.loc[clean[interaction_column].ne("")].copy()
    self_interactions = interactions.loc[
        interactions["userid"].eq(interactions[interaction_column])
    ]
    other_interactions = interactions.loc[
        interactions["userid"].ne(interactions[interaction_column])
    ]

    # The target is considered "within" if it appears as a userid anywhere in this collection.
    within = other_interactions.loc[
        other_interactions[interaction_column].isin(known_ids)
    ]
    outside = other_interactions.loc[
        ~other_interactions[interaction_column].isin(known_ids)
    ]

    output_folder = ensure_output_folder(output_folder)
    unique_ids.to_csv(
        output_folder / f"{output_prefix}_uni_uids_{len(unique_ids)}",
        index=False,
        header=False,
    )

    # Match the original short labels in output filenames.
    label = "RT" if interaction_column == "retweetid" else "Rply"
    exports = export_interaction_network(
        interactions=clean,
        interaction_column=interaction_column,
        output_folder=output_folder,
        prefix=output_prefix,
        interaction_label=label,
    )

    self_counts = self_interactions["userid"].value_counts()
    print(f"\n{'-' * 14} {interaction_name} statistics {'-' * 14}")
    print(f"Original rows: {original_rows:,}")
    print(f"Deduplicated rows: {deduplicated_rows:,} ({_percent(deduplicated_rows, original_rows)}% of original)")
    print(f"Unique user IDs: {len(unique_ids):,}")
    print(f"Total {interaction_name.lower()} interactions: {len(interactions):,} "
          f"({_percent(len(interactions), deduplicated_rows)}% of deduplicated tweets)")
    print(f"Interactions with other users: {len(other_interactions):,}")
    print(f"Self-interactions: {len(self_interactions):,} "
          f"({_percent(len(self_interactions), len(interactions))}% of interactions)")
    print(f"Within collection: {len(within):,} "
          f"({_percent(len(within), len(other_interactions))}% of interactions with others)")
    print(f"Outside collection: {len(outside):,} "
          f"({_percent(len(outside), len(other_interactions))}% of interactions with others)")
    print(f"Unique within-collection pairs: {len(exports['within_pairs']):,}")
    print(f"Unique outside-collection pairs: {len(exports['outside_pairs']):,}")

    if not self_counts.empty:
        print("\nTop 15 users by self-interactions:")
        print(self_counts.head(15))

    return {
        "interaction": interaction_name,
        "original_rows": original_rows,
        "deduplicated_rows": deduplicated_rows,
        "unique_user_ids": len(unique_ids),
        "total_interactions": len(interactions),
        "self_interactions": len(self_interactions),
        "interactions_with_others": len(other_interactions),
        "within_collection": len(within),
        "outside_collection": len(outside),
        "unique_within_pairs": len(exports["within_pairs"]),
        "unique_outside_pairs": len(exports["outside_pairs"]),
    }
