import itertools
import json
import logging
import typing

import click
import tqdm

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)


def generate_time_based_new_stats(
        data: typing.List[typing.Dict],
        output_path: str,
):
    LIBS_SEEN = set()
    PAIRS_SEEN = set()
    with open(output_path, "w") as json_file:
        for row in tqdm.tqdm(data):
            payload = {
                "post_id": row.get("id"),
                "post_date": row.get("date"),
                "user_id": row.get("poster_id"),
                "post_type": row.get("post_type"),
                "imports": row.get("imports"),
                "new_libs": [],
                "new_pairs": [],
            }

            for package in row.get("imports"):
                if package not in LIBS_SEEN:
                    payload["new_libs"].append(package)
                    LIBS_SEEN.add(package)

            for p1, p2 in itertools.combinations(row.get("imports"), 2):
                canonical_pair_name = "|".join(sorted([p1, p2]))
                if canonical_pair_name not in PAIRS_SEEN:
                    payload["new_pairs"].append(canonical_pair_name)
                    PAIRS_SEEN.add(canonical_pair_name)

            json_file.write(json.dumps(payload))
            json_file.write("\n")


@click.command()
@click.option("-i", "--input_path", type=str)
@click.option("-o", "--output_path", type=str)
def main(input_path, output_path):
    logger.info("Load input JSON (this takes a while...)")
    with open(input_path) as handle:
        data = json.load(handle)
    logger.info("Input JSON loaded.")

    generate_time_based_new_stats(data, output_path + "_time_based_new.jsonl")
    logger.info("DONE")


if __name__ == "__main__":
    main()
