import collections
import datetime
import itertools
import json
import logging
import typing

import click
import tqdm

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)


def find_first_appearances_and_count_appearances(
        data: typing.List[typing.Dict]
):
    libs_count = collections.defaultdict(int)
    pairs_count = collections.defaultdict(int)
    all_libs_dates = collections.defaultdict(list)
    all_pairs_dates = collections.defaultdict(list)
    libs_first_dates = {}
    pairs_first_dates = {}

    for row in tqdm.tqdm(data):
        dt = datetime.datetime.strptime(
            row.get("date"), "%Y-%m-%dT%H:%M:%S.%f").date()

        # create or update entry for individual timestamp
        for package in row.get("imports"):
            libs_count[package] += 1
            all_libs_dates[package].append(dt)
            if (
                package not in libs_first_dates or
                libs_first_dates[package]["date"] > dt
            ):
                libs_first_dates[package] = {
                    "id": row["id"],
                    "poster_id": row["poster_id"],
                    "date": dt,
                }

        # create or update entry for pair timestamp
        for p1, p2 in itertools.combinations(row.get("imports"), 2):
            canonical_pair_name = "|".join(sorted([p1, p2]))
            pairs_count[canonical_pair_name] += 1
            all_pairs_dates[canonical_pair_name].append(dt)
            if (
                canonical_pair_name not in pairs_first_dates or
                pairs_first_dates[canonical_pair_name]["date"] > dt
            ):
                pairs_first_dates[canonical_pair_name] = {
                    "id": row["id"],
                    "poster_id": row["poster_id"],
                    "date": dt,
                }
    return (
        libs_count, pairs_count,
        all_libs_dates, all_pairs_dates,
        libs_first_dates, pairs_first_dates,
    )


@click.command()
@click.option("-i", "--input_path", type=str)
@click.option("-o", "--output_path", type=str)
def main(input_path, output_path):
    logger.info("Load input JSON (this takes a while...)")
    with open(input_path) as handle:
        data = json.load(handle)
    logger.info("Input JSON loaded.")

    (
        libs_count, pairs_count,
        all_libs_dates, all_pairs_dates,
        libs_first_dates, pairs_first_dates
    ) =\
        find_first_appearances_and_count_appearances(data)

    logger.info("Generating output files...")
    with open(f"{output_path}_libs_count.json", 'w') as handle:
        json.dump(libs_count, handle, default=str)
    with open(f"{output_path}_pairs_count.json", 'w') as handle:
        json.dump(pairs_count, handle, default=str)
    with open(f"{output_path}_all_libs_dates.json", 'w') as handle:
        json.dump(all_libs_dates, handle, default=str)
    with open(f"{output_path}_all_pairs_dates.json", 'w') as handle:
        json.dump(all_pairs_dates, handle, default=str)
    with open(f"{output_path}_libs_first_dates.json", 'w') as handle:
        json.dump(libs_first_dates, handle, default=str)
    with open(f"{output_path}_pairs_first_dates.json", 'w') as handle:
        json.dump(pairs_first_dates, handle, default=str)


if __name__ == "__main__":
    main()
