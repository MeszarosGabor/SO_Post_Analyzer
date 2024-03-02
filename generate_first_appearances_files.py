import datetime
import itertools
import json

import click
import tqdm


def find_first_appearances(data_path: str):

    individual_dates = {}
    pair_dates = {}

    with open(data_path) as handle:
        for line in tqdm.tqdm(handle):
            data = json.loads(line)
            dt = datetime.datetime.strptime(
                data.get("date") ,"%Y-%m-%dT%H:%M:%S.%f").date()

            # create or update entry for individual timestamp
            for package in data.get("imports"):
                if (
                    package not in individual_dates or 
                    individual_dates[package] > dt
                ):
                    individual_dates[package] = dt

            # create or update entry for pair timestamp
            for p1, p2 in itertools.combinations(data.get("imports"), 2):
                canonical_pair_name = "|".join(sorted([p1, p2]))
                if (
                    canonical_pair_name not in pair_dates or 
                    pair_dates[canonical_pair_name] > dt
                ):
                    pair_dates[canonical_pair_name] = dt

    return individual_dates, pair_dates


@click.command()
@click.option("-i", "--input_path", type=str)
@click.option("-o", "--output_path", type=str)
def main(input_path, output_path):
    if output_path.endswith(".json"):
        output_path = output_path[:5]

    individual_dates, pair_dates = find_first_appearances(input_path)

    with open(f"{output_path}_indiv.jsonl", 'w') as handle:
        json.dump(individual_dates, handle, default=str)
    with open(f"{output_path}_pairs.jsonl", 'w') as handle:
        json.dump(pair_dates, handle, default=str)


if __name__ == "__main__":
    main()
