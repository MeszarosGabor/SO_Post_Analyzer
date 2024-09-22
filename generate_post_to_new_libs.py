import collections
import itertools
import json
import logging
import typing

import click
import tqdm

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)


def collect_post_count_to_new_libs_data(language: str, count_lower_limit: int = 0):
    stats = collections.defaultdict(int)
    time_buckets = collections.defaultdict(list)


    with open(f"data/results/{language}/{language}_{language}_post_stats.json") as in_handle:
        data = json.load(in_handle)

    with open(f"data/results/{language}/{language}_libs_count.json") as handle:
        counts = json.load(handle)
    
    for row in tqdm.tqdm(data):
        try:
            imports = {lib_ for lib_ in row.get("imports", []) if counts.get(lib_, 0) > count_lower_limit}
            if not imports:
                continue
            time_buckets[row.get("date")] = imports
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
