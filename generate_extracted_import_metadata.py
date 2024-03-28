import collections
import datetime
import json
import logging
import typing


import click
import tqdm


import utils.extractor as extractor
import utils.xml_parser as xml_parser

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)


def generate_extracted_import_metadata(
        input_path: str,
        target_language: str,
        bypass_validation: bool,
) -> typing.Dict[str, int]:
    stats = collections.defaultdict(int)
    valid_libs_stats = []
    invalid_libs_stats = collections. defaultdict(int)
    daily_post_stats = collections.defaultdict(int)

    with (
        open(input_path) as in_handle,
    ):
        for row in tqdm.tqdm(in_handle):
            stats["TOTAL"] += 1
            try:
                parsed_row = json.loads(row)
                post_id, data =\
                    extractor.extract_code_snippets_from_parsed_row(parsed_row)
                post_id, codes, import_list, invalids =\
                    extractor.extract_import_statements_from_single_row(
                        post_id,
                        parsed_data=data,
                        target_language=target_language,
                        bypass_validation=bypass_validation)
                
                if not post_id:
                    stats["no post id"] += 1
                    continue

                if not data.get("poster_id"):
                    stats["no poster id"] += 1
                    continue

                if not data.get("date_posted"):
                    stats["no date posted"] += 1
                    continue

                if not data.get("code_snippets"):
                    stats["no code"] += 1
                    continue

                # process invalid libs stats
                for invalid in invalids:
                    invalid_libs_stats[invalid] += 1

                # TODO: this should not happen here.
                # only keep reasonably looking imports. Ditch empty strings, etc.
                import_list = [item.strip() for item in import_list if item.strip()]


                if not import_list:
                    stats['empty list'] += 1

                payload = {
                    "id": post_id,
                    "imports": import_list,
                    "codes": codes,
                    "date": data.get("date_posted"),  # 
                    "poster_id": data.get("poster_id"),
                    "score": data.get("score"),
                }
                valid_libs_stats.append(payload)
                # log post in daily stats
                dt = datetime.datetime.strptime(
                    data.get(
                        "date_posted"),
                        "%Y-%m-%dT%H:%M:%S.%f").date()
                daily_post_stats[dt.strftime("%Y-%m-%d")] += 1

                stats['non-empty list'] += 1
            except Exception as exc:
                stats[str(exc)] += 1
            

    return valid_libs_stats, invalid_libs_stats, daily_post_stats, stats


@click.command()
@click.option("-t", "--target_language", type=str, required=True)
@click.option("-i", "--raw_input_path", type=str, default=None)
@click.option("--parse_xml_only", is_flag=True, show_default=True, default=False)
@click.option("-j", "--curated_posts_path", type=str, default=None)
@click.option("-m", "--metadata_output_path", type=str, default="meta.json")
@click.option("-o", "--imports_output_path", type=str)
@click.option("-x", "--bypass_validation", is_flag=True, show_default=True, default=False,
              help="Should we validate the packages obtained?")
@click.option("--gen_invalids", is_flag=True, show_default=True, default=False,
              help="Generates a JSON collection of encountered invalid libs.")
def main(
    target_language,
    raw_input_path,
    parse_xml_only,
    curated_posts_path,
    metadata_output_path,
    imports_output_path,
    bypass_validation,
    gen_invalids,
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
    if not raw_input_path and parse_xml_only:
        raise ValueError(
            "The flag >>parse_xml_only<< is only meaningful if we process a raw XML input!"
        )

    if raw_input_path:
        logger.info(f"Starting XML search. Target language is {target_language}")
        xml_parser.parse_xml_source_and_generate_output(
            target_language,
            raw_input_path,
            metadata_output_path,
        )
        curated_posts_path = metadata_output_path
        logger.info(f"XML extraction finished. Output file is {curated_posts_path}")
        if parse_xml_only:
            logger.info("Parse-XML-only enabled, exiting execution.")
            return

    valid_libs_stats, invalid_libs_stats, daily_post_stats, stats =\
        generate_extracted_import_metadata(
            input_path=curated_posts_path, 
            target_language=target_language,
            bypass_validation=bypass_validation)

    with open(f"{imports_output_path}_{target_language}_post_stats.json", "w") as out_handle:
        json.dump(valid_libs_stats, out_handle)

    with open(f"{imports_output_path}_{target_language}_daily_post_stats.json", "w") as out_handle:
        json.dump(daily_post_stats, out_handle)

    if gen_invalids:
        with open(f"{imports_output_path}_{target_language}_invalid_libs.json", 'w') as handle:
            json.dump(invalid_libs_stats, handle)

    logger.info(f"Extraction finished,  stats: {stats}")


if __name__ == "__main__":
    main()
