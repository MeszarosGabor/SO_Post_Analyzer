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
    pair_count = collections.defaultdict(int)
    libs_dates = {}
    pair_dates = {}

    for row in tqdm.tqdm(data):
        dt = datetime.datetime.strptime(
            row.get("date"), "%Y-%m-%dT%H:%M:%S.%f").date()

        # create or update entry for individual timestamp
        for package in row.get("imports"):
            libs_count[package] += 1
            if (
                package not in libs_dates or
                libs_dates[package] > dt
            ):
                libs_dates[package] = dt

        # create or update entry for pair timestamp
        for p1, p2 in itertools.combinations(row.get("imports"), 2):
            canonical_pair_name = "|".join(sorted([p1, p2]))
            pair_count[canonical_pair_name] += 1
            if (
                canonical_pair_name not in pair_dates or
                pair_dates[canonical_pair_name] > dt
            ):
                pair_dates[canonical_pair_name] = dt

    return libs_count, pair_count, libs_dates, pair_dates


@click.command()
@click.option("-i", "--input_path", type=str)
@click.option("-o", "--output_path", type=str)
def main(input_path, output_path):
    logger.info("Load input JSON (this takes a while...)")
    with open(input_path) as handle:
        data = json.load(handle)
    logger.info("Input JSON loaded.")

    libs_count, pair_count, individual_dates, pair_dates =\
        find_first_appearances_and_count_appearances(data)

    logger.info("Generating output files...")
    with open(f"{output_path}_libs_count.json", 'w') as handle:
        json.dump(libs_count, handle, default=str)
    with open(f"{output_path}_pair_count.json", 'w') as handle:
        json.dump(pair_count, handle, default=str)
    with open(f"{output_path}_indiv.json", 'w') as handle:
        json.dump(individual_dates, handle, default=str)
    with open(f"{output_path}_pairs.json", 'w') as handle:
        json.dump(pair_dates, handle, default=str)


if __name__ == "__main__":
    main()
