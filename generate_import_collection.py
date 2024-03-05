import collections
import json
import logging
import typing


import click
import tqdm


import utils.extractor as extractor
import utils.xml_parser as xml_parser

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def generate_imports_collection(
        input_path: str,
        output_path: str,
) -> typing.Dict[str, int]:
    stats = collections.defaultdict(int)
    invalid_libs_stat = collections. defaultdict(int)
    with (
        open(output_path, "w") as out_handle,
        open(input_path) as in_handle,
    ):
        for row in tqdm.tqdm(in_handle):
            try:
                parsed_row = json.loads(row)
                post_id, data = extractor.extract_code_snippets_from_parsed_row(parsed_row)
                post_id, codes, import_list, invalids = extractor.extract_import_statements_from_single_row(
                    post_id, parsed_data=data)

                # process invalid libs stats
                for invalid in invalids:
                    invalid_libs_stat[invalid] += 1

                if not import_list:
                    stats['empty list'] += 1
                    continue
                payload = {
                    "id": post_id,
                    "imports": import_list,
                    "codes": codes,
                    "date": data.get("date_posted"),
                }
                out_handle.write(json.dumps(payload))
                out_handle.write("\n")

                stats['success'] += 1
            except Exception as exc:
                stats[str(exc)] += 1

    # save invalid libs stat
    with open(f"{output_path}_invalid_libs.json", 'w') as handle:
        json.dump(invalid_libs_stat, handle)

    return stats


@click.command()
@click.option("-i", "--raw_input_path", type=str, default=None)
@click.option("-j", "--curated_posts_path", type=str, default=None)
@click.option("-m", "--metadata_output_path", type=str, default="meta.json")
@click.option("-o", "--imports_output_path", type=str)
def main(
    raw_input_path,
    curated_posts_path,
    metadata_output_path,
    imports_output_path,
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
        xml_parser.parse_xml_source_and_generate_output(
            raw_input_path,
            metadata_output_path,
        )
        curated_posts_path = metadata_output_path


    stats = generate_imports_collection(
        input_path=curated_posts_path,
        output_path=imports_output_path,
    )

    print(stats)    


if __name__ == "__main__":
    main()
