import collections
import itertools
import json
import logging
import typing

import click
import tqdm

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)


def collect_post_count_to_new_libs_data(data: typing.List[typing.Dict]):
    stats = collections.defaultdict(int)
    time_buckets = collections.defaultdict(list)
    for row in tqdm.tqdm(data):
        try:
            time_buckets[row.get("date")] = set(row.get("imports"))
            stats["success"] += 1
        except Exception as exc:
            stats[str(exc)] += 1

    sorted_buckets = sorted(time_buckets.items())
    distinct_libs, distinct_pairs = set(), set()
    distinct_libs_plot, distinct_pairs_plot = [], []

    for date_time, libs in sorted_buckets:
        distinct_libs |= libs
        distinct_pairs |= set(itertools.combinations(libs, 2))
        distinct_libs_plot.append(
            (date_time, len(distinct_libs))
        )
        distinct_pairs_plot.append(
            (date_time, len(distinct_pairs))
            )

    return {
            'distinct_libs_plot': distinct_libs_plot,
            'distinct_pairs_plot': distinct_pairs_plot,
    }, stats


@click.command()
@click.option("-i", "--input_path", type=str)
@click.option("-o", "--output_path", type=str)
def main(input_path, output_path):
    logger.info("Load input JSON (this takes a while...)")
    with open(input_path) as in_handle:
        input_data = json.load(in_handle)
    logger.info("Input JSON loaded.")

    data, stats = collect_post_count_to_new_libs_data(input_data)
    
    logger.info(stats)
    logger.info("Generating output file...")
    with open(f"{output_path}_post_to_libs.json", 'w') as out_handle:
        json.dump(data, out_handle)


if __name__ == "__main__":
    main()
