# flake8: noqa
import collections
import json
import logging
import re
import typing

import tqdm

import utils.pypi_packages as pypi_packages 
import utils.models as models
import utils.regex_patterns as regex_patterns

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _revise_post_blocks(post_blocks):
    post_blocks = list(post_blocks)
    marked_for_deletion = set()

    for i in range(len(post_blocks)):
        current_post_block = post_blocks[i]

        # ignore post block if it is already marked for deletion
        if current_post_block in marked_for_deletion:
            continue

        # In some cases when a code blocks ends with a single character, the indention by 4 spaces is missing in
        # the table PostHistory (see, e.g., PostHistoryId=96888165). The following code should prevent most of
        # these cases from being recognized as text blocks.

        # remove this post block if does not contain letters or digits
        contains_letter_or_digit = regex_patterns.contains_letter_or_digit_regex.search(
            current_post_block.content
        )

        if contains_letter_or_digit:
            continue

        if i == 0:
            # current post block is first one
            if len(post_blocks) > 1:
                next_post_block = post_blocks[i + 1]
                next_post_block.prepend(current_post_block.content)
                marked_for_deletion.add(current_post_block)
        else:
            # current post block is not first one (has predecessor)
            previous_post_block = post_blocks[i - 1]

            if previous_post_block in marked_for_deletion:
                continue

            previous_post_block.append(current_post_block.content)
            marked_for_deletion.add(current_post_block)

            # current post block must have successor
            if i >= (len(post_blocks) - 1):
                continue

            next_post_block = post_blocks[i + 1]

            # merge predecessor and successor if they have same type
            if previous_post_block.__class__ != next_post_block.__class__:
                continue

            previous_post_block.append(next_post_block.content)
            marked_for_deletion.add(next_post_block)

    # remove post blocks marked for deletion
    for current_post_block in marked_for_deletion:
        post_blocks.remove(current_post_block)


def extract_text_blocks(text, post_id: str):
    """
    Extracts all text blocks from the Markdown source of a post version
    :param post_edit_pair: pair of post id, attribute dict element of most recent version
    :return: tuple of post_id and text_blocks



    # TODO: post_id is undefined, find it!!!
    """
    markdown_content = text
    post_blocks = []

    lines = re.split(regex_patterns.newline_regex, markdown_content)

    current_post_block = None
    previous_line = None
    code_block_ends_with_next_line = False

    in_code_tag_block = False
    in_stack_snippet_code_block = False
    in_script_tag_code_block = False
    in_alternative_code_block = False

    for line in lines:
        # ignore empty lines
        if not line:
            previous_line = line
            continue

        # end code block which contained a code tag in the previous line (see below)
        if code_block_ends_with_next_line:
            in_code_tag_block = False
            code_block_ends_with_next_line = False

        # check for indented code blocks (Stack Overflow's standard way)
        # even if tab is not listed here: http://stackoverflow.com/editing-help#code
        # we observed cases where it was important to check for the tab, sometimes preceded by spaces
        in_markdown_code_block = (
            regex_patterns.code_block_regex.match(line) is not None
        )  # only match beginning of line
        # check if line only contains whitespaces
        # (ignore whitespaces at the beginning of posts and not end blocks with whitespace lines)
        is_whitespace_line = (
            regex_patterns.whitespace_line_regex.fullmatch(line) is not None
        )  # match whole line
        # e.g. "<!-- language: lang-js -->" (see https://stackoverflow.com/editing-help#syntax-highlighting)
        is_snippet_language = (
            regex_patterns.snippet_language_regex.fullmatch(line) is not None
        )  # match whole line
        # in some posts an empty XML comment ("<!-- -->") is used to divide code blocks (see, e.g., post 33058542)
        is_snippet_divider = (
            regex_patterns.snippet_divider_regex.fullmatch(line) is not None
        )  # match whole line
        # in some cases, there are inline code blocks in a single line (`...`)
        is_inline_code_line = (
            regex_patterns.inline_code_line_regex.fullmatch(line) is not None
        )  # match whole line

        # if line is not part of a regular Stack Overflow code block, try to detect alternative code block styles
        if (
            not in_markdown_code_block
            and not is_whitespace_line
            and not is_snippet_language
        ):
            # see https://stackoverflow.blog/2014/09/16/introducing-runnable-javascript-css-and-html-code-snippets/
            # ignore stack snippet begin in post block version
            if regex_patterns.stack_snippet_begin_regex.match(
                line
            ):  # only match beginning of line
                in_stack_snippet_code_block = True
                # remove stack snippet info from code block
                line = regex_patterns.stack_snippet_begin_regex.sub("", line)
                if (
                    not line.strip()
                ):  # if string empty after removing leading and trailing whitespaces
                    # line only contained stack snippet begin
                    continue

            # ignore stack snippet end in post block version
            if regex_patterns.stack_snippet_end_regex.match(
                line
            ):  # only match beginning of line
                in_stack_snippet_code_block = False
                # remove stack snippet info from code block
                line = regex_patterns.stack_snippet_end_regex.sub("", line)
                if (
                    not line.strip()
                ):  # if string empty after removing leading and trailing whitespaces
                    # line only contained stack snippet begin
                    continue

            # code block that is marked by <pre><code> ... </pre></code> instead of indention
            if regex_patterns.code_tag_begin_regex.match(
                line
            ):  # only match beginning of line
                # remove code tag from line
                line = regex_patterns.code_tag_begin_regex.sub("", line)
                in_code_tag_block = True
                if (
                    not line.strip()
                ):  # if string empty after removing leading and trailing whitespaces
                    # line only contained opening code tags -> skip
                    continue

            if regex_patterns.code_tag_end_regex.match(
                line
            ):  # only match beginning of line
                # remove code tag from line
                line = regex_patterns.code_tag_end_regex.sub("", line)
                if (
                    not line.strip()
                ):  # if string empty after removing leading and trailing whitespaces
                    # line only contained closing code tags -> close code block and skip
                    in_code_tag_block = False
                    continue
                else:
                    # line also contained content -> close code block in next line
                    code_block_ends_with_next_line = True

            # code block that is marked by <script...> ... </script> instead of correct indention
            if regex_patterns.script_tag_begin_regex.match(
                line
            ):  # only match beginning of line
                # remove opening script tag
                line = regex_patterns.script_tag_open_regex.sub("", line, count=1)
                in_script_tag_code_block = True
                if (
                    not line.strip()
                ):  # if string empty after removing leading and trailing whitespaces
                    # line only contained opening script tag -> skip
                    continue

            if regex_patterns.script_tag_end_regex.match(
                line
            ):  # only match beginning of line
                # remove closing script tag
                line = regex_patterns.script_tag_close_regex.sub("", line)
                if (
                    not line.strip()
                ):  # if string empty after removing leading and trailing whitespaces
                    # line only contained closing script tag -> close code block and skip
                    in_script_tag_code_block = False
                    continue
                else:
                    # line also contained content -> close script block in next line
                    code_block_ends_with_next_line = True

            # see https://meta.stackexchange.com/q/125148
            # example: https://stackoverflow.com/posts/32342082/revisions
            if regex_patterns.alternative_code_block_begin_regex.match(
                line
            ):  # only match beginning of line
                # remove first "```" from line
                line = regex_patterns.alternative_code_block_begin_regex.sub(
                    "", line, count=1
                )
                in_alternative_code_block = True
                # continue if line only contained "```"
                if (
                    not line.strip()
                ):  # if string empty after removing leading and trailing whitespaces
                    continue
                else:
                    if regex_patterns.alternative_code_block_marker_regex.match(line):
                        # alternative code block was inline code block (which should be part of a text block)
                        line = regex_patterns.alternative_code_block_marker_regex.sub(
                            "", line
                        )
                        in_alternative_code_block = False

            if regex_patterns.alternative_code_block_end_regex.match(
                line
            ):  # only match beginning of line
                # remove "```" from line
                line = regex_patterns.alternative_code_block_marker_regex.sub("", line)
                in_alternative_code_block = False

        if is_snippet_language:
            # remove snippet language information
            line = regex_patterns.snippet_language_regex.sub("", line)

        if is_inline_code_line:
            # replace leading and trailing backtick and HTML line break if present
            line = regex_patterns.inline_code_line_regex.match(line).group(1)

        # decide if the current line is part of a code block
        in_non_markdown_code_block = (
            (is_snippet_language and not line.strip())
            or in_stack_snippet_code_block
            or in_alternative_code_block
            or in_code_tag_block
            or in_script_tag_code_block
            or is_inline_code_line
        )

        if not current_post_block:  # first block in post
            # ignore whitespaces at the beginning of a post
            if not is_whitespace_line:
                # first line, block element not created yet
                if in_markdown_code_block or in_non_markdown_code_block:
                    current_post_block = models.CodeBlock(post_id)
                else:
                    current_post_block = models.TextBlock(post_id)
        else:
            # current block has length > 0 => check if current line belongs to this block
            # or if it is first line of next block
            if isinstance(current_post_block, models.TextBlock):
                # check if line contains letters or digits (heuristic for malformed post blocks)
                previous_line_contains_letters_or_digits = (
                    regex_patterns.contains_letter_or_digit_regex.search(previous_line)
                    is not None
                )

                if (
                    (
                        in_markdown_code_block
                        and (
                            not previous_line.strip()
                            or not previous_line_contains_letters_or_digits
                        )
                    )
                    or in_non_markdown_code_block
                ) and not is_whitespace_line:
                    # End of text block, beginning of code block.
                    # Do not end text block if next line is whitespace line
                    # see, e.g., second line of PostHistory, Id=97576027
                    if not current_post_block.is_empty():
                        post_blocks.append(current_post_block)
                    current_post_block = models.CodeBlock(post_id)

            elif isinstance(current_post_block, models.CodeBlock):
                # snippet language or snippet divider divide two code blocks ( if first block is not empty)
                if is_snippet_language or is_snippet_divider:
                    if not current_post_block.is_empty():
                        post_blocks.append(current_post_block)
                    current_post_block = models.CodeBlock(post_id)
                elif (
                    not in_markdown_code_block and not in_non_markdown_code_block
                ) and not is_whitespace_line:
                    # In a Stack Snippet, the lines do not have to be indented (see version 12 of answer
                    # 26044128 and corresponding test case).
                    # Do not close code postBlocks when whitespace line is reached
                    # see, e.g., PostHistory, Id=55158265, PostId=20991163 (-> test case).
                    # Do not end code block if next line is whitespace line
                    # see, e.g., second line of PostHistory, Id=97576027
                    if not current_post_block.is_empty():
                        post_blocks.append(current_post_block)
                    current_post_block = models.TextBlock(post_id)

        # ignore snippet language information (see https://stackoverflow.com/editing-help#syntax-highlighting)
        if current_post_block and not is_snippet_language:
            current_post_block.append(line)

        previous_line = line

    if current_post_block and not current_post_block.is_empty():
        # last block not added yet
        post_blocks.append(current_post_block)

    _revise_post_blocks(post_blocks)

    return post_blocks


def extract_code_snippets_from_parsed_row(parsed_row: typing.Dict) -> None:
        post_id, data = list(parsed_row.items())[0]
        return (
            post_id,
            {
                "post_type": data[0],
                "accepted_answer_id": data[1],
                "date_posted": data[2],
                "score": data[3],
                "view_count": data[4],
                "code_snippets": [
                    x.content
                    for x in extract_text_blocks(data[5], post_id)
                    if type(x) == models.CodeBlock
                ],
                "post_length": len(data[5]),
                "poster_id": data[6],
                "last_activity": data[7],
                "tags": [
                    x.replace("<", "").replace(">", "") for x in data[8].split("><")
                ],
                "n_comments": data[9],
                "n_answers": data[10],
                "parent_id": data[11],
            }
        )


def extract_import_statements_from_code(code):
    import_statements = set()

    for statement in regex_patterns.import_pattern.findall(code):
        words = statement.split()
        if words[0] == "import":
            import_statements.add(words[1].split(".")[0].rstrip(","))
        elif len(words) > 1 and words[0] == "from":
            import_statements.add(words[1].split(".")[0].rstrip(","))

    return list(import_statements)


def extract_import_statements_from_single_row(post_id: str,  parsed_data: typing.Dict):
    libs = []
    for cs in parsed_data["code_snippets"]:
        cs2 = cs.replace("\n", " ")
        try:
            libs += extract_import_statements_from_code(cs2)
        except Exception as exc:
            print(f"Exception at code extraction with cs:{cs}, cs2: {cs2}, exc: {exc}")
    
    pypi_package_names = pypi_packages.get_pypi_package_names()
    
    return post_id, list(set(libs) & pypi_package_names)


def generate_imports_collection(
        input_path: str,
        output_path: str,
) -> typing.Dict[str, int]:
    stats = collections.defaultdict(int)

    with open(f"{output_path}_imports_and_dates", "w") as out_handle:
            with open(output_path, "w") as out_handle:
                with open(input_path) as in_handle:
                    for row in tqdm.tqdm(in_handle):
                        try:
                            parsed_row = json.loads(row)
                            post_id, data = extract_code_snippets_from_parsed_row(parsed_row)
                            post_id, import_list = extract_import_statements_from_single_row(
                                post_id, parsed_data=data)
                            if not import_list:
                                stats['empty list'] += 1
                                continue
                            # Persist libs
                            payload = {
                                "id": post_id,
                                "imports": import_list,
                                "date": data.get("date_posted"),
                            }
                            out_handle.write(json.dumps(payload))
                            out_handle.write("\n")

                            stats['success'] += 1
                        except Exception as exc:
                            stats[str(exc)] += 1
    return stats
