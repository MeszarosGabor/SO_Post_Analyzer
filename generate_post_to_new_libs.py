import collections
import itertools
import json

import click
import tqdm

import utils.extractor as extractor


@click.command()
@click.option("-i", "--input_path", type=str)
@click.option("-o", "--output_path", type=str)
def main(input_path, output_path):
    stats = collections.defaultdict(int)
    time_buckets = collections.defaultdict(list)

    with open(input_path) as in_handle:
        for row in tqdm.tqdm(in_handle):
            try:
                parsed_row = json.loads(row)

                post_id, data = extractor.extract_code_snippets_from_parsed_row(parsed_row)
                date_posted = data.get("date_posted")
                if not date_posted:
                    stats["missing date"] += 1
                    continue

                post_id, _, import_list, _ = extractor.extract_import_statements_from_single_row(
                    post_id, parsed_data=data)
                time_buckets[date_posted] = set(import_list)
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
    
    with open(output_path, 'w') as out_handle:
        json.dump({
            'distinct_libs_plot': distinct_libs_plot,
            'distinct_pairs_plot': distinct_pairs_plot,
        }, out_handle)


if __name__ == "__main__":
    main()
