import collections
import logging


import click


import utils.extractor as extractor
import utils.xml_parser as xml_parser

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
        xml_parser.parse_xml_source_and_generate_output(
            raw_input_path,
            metadata_output_path,
        )
        curated_posts_path = metadata_output_path


    stats = extractor.generate_imports_collection(
        input_path=curated_posts_path,
        output_path=imports_output_path,
    )
 
    print(stats)    


if __name__ == "__main__":
    main()
