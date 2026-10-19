"""Output helpers for the network analysis."""

from pathlib import Path

import pandas as pd


def ensure_output_folder(path: Path) -> Path:
    """Create the output folder if it does not already exist."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def export_interaction_network(
    interactions: pd.DataFrame,
    interaction_column: str,
    output_folder: Path,
    prefix: str,
    interaction_label: str,
) -> dict:
    """Export self, within-collection, and outside-collection network files."""
    output_folder = ensure_output_folder(output_folder)
    id_columns = ["userid", interaction_column]
    full_columns = ["userid", interaction_column, "tweetDate", "text"]

    nonempty = interactions.loc[
        interactions[interaction_column].ne("")
    ].copy()

    self_interactions = nonempty.loc[
        nonempty["userid"].eq(nonempty[interaction_column])
    ].copy()
    other_interactions = nonempty.loc[
        nonempty["userid"].ne(nonempty[interaction_column])
    ].copy()

    known_ids = set(interactions["userid"].dropna().astype(str))
    within = other_interactions.loc[
        other_interactions[interaction_column].isin(known_ids)
    ].copy()
    outside = other_interactions.loc[
        ~other_interactions[interaction_column].isin(known_ids)
    ].copy()

    # Preserve the original notebook's main output naming pattern.
    self_interactions.to_csv(
        output_folder / f"{prefix}_self{interaction_label}_{len(self_interactions)}.csv",
        index=False,
    )
    self_interactions["userid"].value_counts().to_csv(
        output_folder / f"{prefix}_self{interaction_label}.csv"
    )

    within_full = within[full_columns]
    outside_full = outside[full_columns]
    within_full.to_pickle(
        output_folder / f"{prefix}_withinCountry{interaction_label}_edges_Full_{len(within_full)}.pkl"
    )
    outside_full.to_pickle(
        output_folder / f"{prefix}_outsideCountry{interaction_label}_edges_Full_{len(outside_full)}.pkl"
    )

    within_pairs = (
        within[id_columns].groupby(id_columns, dropna=False).size().rename("count").reset_index()
    )
    outside_pairs = (
        outside[id_columns].groupby(id_columns, dropna=False).size().rename("count").reset_index()
    )
    within_pairs.to_csv(
        output_folder / f"{prefix}_withinCountry{interaction_label}_edges_Trimmed.csv",
        index=False,
    )
    outside_pairs.to_csv(
        output_folder / f"{prefix}_outsideCountry{interaction_label}_edges_Trimmed.csv",
        index=False,
    )

    outside[interaction_column].value_counts().to_csv(
        output_folder / f"{prefix}_outsideCountry{interaction_label}_CountsByID.csv"
    )
    outside_ids = outside[interaction_column].drop_duplicates()
    outside_ids.to_csv(
        output_folder / f"{prefix}_outsideCountry{interaction_label}_ids_{len(outside_ids)}",
        index=False,
        header=False,
    )

    return {
        "self": self_interactions,
        "other": other_interactions,
        "within": within,
        "outside": outside,
        "within_pairs": within_pairs,
        "outside_pairs": outside_pairs,
    }
