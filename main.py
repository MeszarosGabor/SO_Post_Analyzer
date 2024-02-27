import json
import logging
import time

import click

from extractor import collect_all_import_statements, extract_code_snippets
from xml_parser import parse_xml_source_and_generate_output

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@click.command()
@click.option("-i", "--raw_input_path", type=str, default=None)
@click.option("-j", "--curated_posts_path", type=str, default=None)
@click.option("-m", "--metadata_output_path", type=str, default="meta.json")
@click.option("-o", "--imports_output_path", type=str)
def main(
    raw_input_path,
    curated_posts_path,
    metadata_output_path,
    imports_output_path
):
    if (
        not raw_input_path
        and not curated_posts_path
        or raw_input_path
        and curated_posts_path
    ):
        raise ValueError(
            "Exactly one of raw_input_path and curated_posts_path "
            "should be provided!"
        )

    if raw_input_path:
        parse_xml_source_and_generate_output(
            raw_input_path,
            metadata_output_path,
        )
        curated_posts_path = metadata_output_path

    logger.info("Loading posts...")
    t0 = time.time()
    with open(curated_posts_path) as handle:
        parsed_posts = [json.loads(line) for line in handle]
    t1 = time.time()
    logger.info(f"Loaded posts. Took {(t1-t0)} seconds.")

    code_snippets = extract_code_snippets(parsed_posts)
    all_imports = collect_all_import_statements(code_snippets)

    with open(imports_output_path, "w") as handle:
        json.dump(all_imports, handle)


if __name__ == "__main__":
    main()
