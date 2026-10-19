"""Run within-country retweet and reply network analysis."""

from config import COUNTRY, INPUT_FOLDER, MASTER_PICKLE, OUTPUT_FOLDER
from data_loader import load_tweets
from network_analysis import analyze_interaction_network


def main() -> None:
    tweets = load_tweets(
        master_pickle=MASTER_PICKLE,
        input_folder=INPUT_FOLDER,
    )

    print(f"Country/project label: {COUNTRY}")
    print(f"Rows loaded: {len(tweets):,}")
    print(f"Outputs will be written to: {OUTPUT_FOLDER.resolve()}")

    summaries = []
    for column, label in (
        ("retweetid", "Retweet"),
        ("replyid", "Reply"),
    ):
        summaries.append(
            analyze_interaction_network(
                data=tweets,
                interaction_column=column,
                interaction_name=label,
                output_prefix=COUNTRY,
                output_folder=OUTPUT_FOLDER,
            )
        )

    print("\nAnalysis complete.")
    for summary in summaries:
        print(summary)


if __name__ == "__main__":
    main()
