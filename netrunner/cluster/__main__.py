import argparse
from datetime import date
import functools
from multiprocessing import Pool
from netrunner.alwaysberunning.alwaysberunning import AlwaysBeRunning
import sys
from typing import Tuple

from netrunner.cluster.clustering import cluster_decklists
from netrunner.cluster.data_collection import all_events, decklists_from_event
from netrunner.cluster.most_common import most_common_cards


def main():
    output_file, start_date, end_date, tournament_format, top_percentage, eps, min_samples = args()
    abr = AlwaysBeRunning()

    print(f"[+] Getting completed {tournament_format} events from {start_date.isoformat()} to {end_date.isoformat()}")

    # Get all events that match our filters.
    events = list(
        filter(
            lambda event:
                (event.format or "") == tournament_format and
                (start_date <= (event.date or date(2000, 1, 1)) <= end_date),
            all_events(abr)
        )
    )

    print(f"[+] Getting decklists for {len(events)} tournaments")

    # Get all decklists from these events that match our filters, split out over
    # a multiprocessing pool to get it done quicker.
    decklist_getter = functools.partial(decklists_from_event, top_percentage)
    with Pool() as pool:
        decklists = [x for xs in pool.map(decklist_getter, events) for x in xs]

    # Split our decklist tuples into corp and runner sets.
    corp_decks = set([decklist[0] for decklist in decklists if decklist[0] is not None])
    runner_decks = set([decklist[1] for decklist in decklists if decklist[1] is not None])
    
    # Cluster the decklists.
    print(f"[+] Clustering {len(corp_decks)} corp decks")
    clustered_corp_decks = cluster_decklists(corp_decks, eps, min_samples)

    print(f"[+] Clustering {len(runner_decks)} runner decks")
    clustered_runner_decks = cluster_decklists(runner_decks, eps, min_samples)

    # Write the markdown.
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"## Corp\n")
        for label, decks in clustered_corp_decks.items():
            f.write(f"\n### {label}\n\n")
            for deck in decks:
                f.write(f"* [{deck.name}](https://netrunnerdb.com/en/decklist/{deck.uuid})\n")

            f.write(f"\n#### Most Common Cards\n\n")
            for card, quantity in most_common_cards(decks):
                f.write(f"* [{card.title}](https://netrunnerdb.com/en/card/{card.code}) ({quantity} copies)\n")

        f.write("\n")

        f.write(f"## Runner\n")
        for label, decks in clustered_runner_decks.items():
            f.write(f"\n### {label}\n\n")
            for deck in decks:
                f.write(f"* [{deck.name}](https://netrunnerdb.com/en/decklist/{deck.uuid})\n")

            f.write(f"\n#### Most Common Cards\n\n")
            for card, quantity in most_common_cards(decks):
                f.write(f"* [{card.title}](https://netrunnerdb.com/en/card/{card.code}) ({quantity} copies)\n")


def args() -> Tuple[str, date, date, str, float, float, int]:
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(
        prog="cluster",
        description="k-Means Clustering for Netrunner top decks"
    )

    parser.add_argument("--output", "-o", default=f"rwr_{date.today().isoformat()}.md", help="Output filename")
    parser.add_argument("--start-date", default="2024-03-18", help="Start date for completed events (inclusive)")
    parser.add_argument("--end-date", default=date.today().isoformat(), help="End date for completed events (inclusive)")
    parser.add_argument("--format", default="standard", choices=["standard", "startup"], help="The format to get completed decks for")
    parser.add_argument("--percentage", default=30, type=int, help="Percentage of decks to collect from tournaments (0-100)")
    parser.add_argument("--eps", default=7.5, type=float, help="EPS value for DBSSCAN algorithm")
    parser.add_argument("--min-samples", default=3, type=int, help="Minimum number of samples to form a cluster")

    args = parser.parse_args()

    if args.percentage < 0 or args.percentage > 100:
        sys.stderr.write("--percentage arg must be between 0 and 100\n")
        raise Exception

    return (
        args.output,
        date.fromisoformat(args.start_date),
        date.fromisoformat(args.end_date),
        args.format,
        args.percentage / 100,
        args.eps,
        args.min_samples
    )


if __name__ == "__main__":
    main()
