import collections
import json
import logging
import typing

import lxml.etree

import utils.models as models

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)


def fast_iter(context, func, *args, **kwargs):
    """
    http://lxml.de/parsing.html#modifying-the-tree
    Based on Liza Daly's fast_iter
    http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    See also http://effbot.org/zone/element-iterparse.htm
    from: https://stackoverflow.com/questions/12160418/why-is-lxml-etree-iterparse-eating-up-all-my-memory  # noqa: E501
    """
    for event, elem in context:
        try:
            func(elem, *args, **kwargs)
            # It's safe to call clear() here because no descendants will be
            # accessed
            elem.clear()
            # Also eliminate now-empty references from the root node to elem
            for ancestor in elem.xpath("ancestor-or-self::*"):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        except Exception as exc:
            logger.error(f"Exception! {str(exc)}")
    del context


def link_a_to_q_tags(
    row, questions_to_tags: typing.Dict, answers_to_questions: typing.Dict
):
    if row.attrib.get("PostTypeId", "") == "1":
        questions_to_tags[row.attrib["Id"]] = row.attrib.get("Tags", "")
    elif row.attrib.get("PostTypeId", "") == "2":
        answers_to_questions[row.attrib["Id"]] = row.attrib["ParentId"]


def get_row_data_json(
    row,
    posts_to_tags: typing.Dict,
    output_path: str,
):
    with open(output_path, "a") as outfile:
        tags = posts_to_tags.get(row.attrib.get("Id", ""), "")
        if "python" in tags:
            post_dict = {}
            post_dict[row.attrib.get("Id", "")] = [
                row.attrib.get(x, "") for x in models.POSTS_COLS
            ]
            json.dump(post_dict, outfile)
            outfile.write("\n")


def parse_xml_source_and_generate_output(
        xml_path: str, output_path: str) -> None:
    questions_to_tags = {}
    answers_to_questions = {}
    posts_to_tags = {}

    logging.info("Starting parsing...")
    context = lxml.etree.iterparse(xml_path)
    fast_iter(context, link_a_to_q_tags,
              questions_to_tags, answers_to_questions)

    logging.info("Posts_to_tags population (questions) started.")
    stats_posts_to_tags_questions = collections.defaultdict(int)
    for question, tags in questions_to_tags.items():
        if question in posts_to_tags:
            stats_posts_to_tags_questions["overwrite"] += 1
        posts_to_tags[question] = tags
        stats_posts_to_tags_questions["success"] = 1
    logging.info(
        "Posts_to_tags population (questions) finished. "
        "Stats: {stats_posts_to_tags_questions}"
    )

    logging.info("Posts_to_tags population (answers) started")
    stats_posts_to_tags_answers = collections.defaultdict(int)
    for answer, question in answers_to_questions.items():
        if questions_to_tags.get(question):
            posts_to_tags[answer] = questions_to_tags[question]
            stats_posts_to_tags_answers["success"] += 1
        else:
            stats_posts_to_tags_answers["key error"] += 1
    logging.info(
        "Posts_to_tags population (answers)finished. "
        "Stats: {stats_posts_to_tags_answers}"
    )

    context = lxml.etree.iterparse(xml_path)
    fast_iter(context, get_row_data_json, posts_to_tags, output_path)
