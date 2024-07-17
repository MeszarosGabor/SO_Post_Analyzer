# flake8: noqa

# from Baltes
# https://github.com/sotorrent/preprocessing-pipeline/blob/master/preprocessing_pipeline/so/util/regex.py

import re


# regex for escaped newline characters
newline_regex = re.compile(r"[\r\n]?\n")

# a code block is indented by four spaces or a tab (which can be preceded by spaces)
code_block_regex = re.compile(r"^( {4}|[ ]*\t)")

# see, e.g., source of question 17158055, version 6 (line containing only `mydomain.com/bn/products/1`)
# also consider possible HTML newline character, as in question 49311849, version 4
inline_code_line_regex = re.compile(r"\s*`([^`]+)`\s*(?:<br\s*/?\s*>)?", re.IGNORECASE)

# a line only containing whitespace characters
whitespace_line_regex = re.compile(r"^\s+$")

# see https://stackoverflow.com/editing-help#syntax-highlighting
snippet_language_regex = re.compile(r"<!--\s+language:[^>]+>", re.IGNORECASE)
snippet_divider_regex = re.compile(r"<([!?])--\s+-->\s*")

# see https://stackoverflow.blog/2014/09/16/introducing-runnable-javascript-css-and-html-code-snippets/
stack_snippet_begin_regex = re.compile(r"<!--\s+begin\s+snippet[^>]+>", re.IGNORECASE)
stack_snippet_end_regex = re.compile(r"<!--\s+end\s+snippet\s+-->", re.IGNORECASE)

# see, e.g., source of question 19175014 (<pre><code> ... </pre></code> instead of indention)
code_tag_begin_regex = re.compile(
    r"^\s*(<pre[^>]*>)|(<pre[^>]*>\s*<code>)|(<code>)", re.IGNORECASE
)
code_tag_end_regex = re.compile(
    r"(</code>)|(</code>\s*</pre>)|(</pre>)\s*$", re.IGNORECASE
)

# see, e.g., source of question 3381751 version 1 (<script type="text/javascript"> ... </script> instead of indention)
script_tag_begin_regex = re.compile(r"^\s*<script[^>]+>", re.IGNORECASE)
script_tag_end_regex = re.compile(r"</script>\s*$", re.IGNORECASE)
script_tag_open_regex = re.compile(r"<script[^>]+>", re.IGNORECASE)
script_tag_close_regex = re.compile(r"</script>", re.IGNORECASE)

# see https://meta.stackexchange.com/q/125148; example: https://stackoverflow.com/posts/32342082/revisions
alternative_code_block_begin_regex = re.compile(r"^\s*(```)")
alternative_code_block_end_regex = re.compile(r"(```)\s*$")
alternative_code_block_marker_regex = re.compile(r"```")

contains_letter_or_digit_regex = re.compile(r"[a-zA-Z0-9]")

job_name_regex = re.compile(r"[^-a-z0-9]+")


import_pattern_by_language = {
    'python': re.compile(r"(?m)^\s*(from[^\n]+|import[^\n]+)"), #syntax: various but import XYZ
    'ruby': re.compile(r"require\s*['\"](.*?)['\"]"), # syntax: require XYZ
    'rust': re.compile(r"use\s+([\w:]+)(?:\s*::\s*\{([^}]+)\})?;?"),
    #'rust': re.compile(r"^use\s+([\w:]+)(::\{\w+(,\s*\w+)*\})?;$"),
    #'rust':re.compile(r"(?:extern crate\s+(\w+)|use\s+(!std::)(\w+))"), #extern crate XYZ OR use XYZ
    
    #library(XYZ) or library("XYZ") or require(XYZ) or require("XYZ")
    'r':re.compile(r"library\s*\(\s*['\"]?(.*?)['\"]?\s*\)|require\s*\(\s*['\"]?(.*?)['\"]?\s*\)"), 
    'julia':re.compile(r"(?:using|import)\s+([A-Za-z0-9_]+(?:\s*,\s*[A-Za-z0-9_]+)*)"), #various, but using XYZ or import XYZ
    'c':re.compile(r'#include\s*(?:[<"])([^>"]+)[>"]'), #various but include <XYZ> or include "XYZ",
    'javascript':re.compile(r"require\(['\"](.*?)['\"]\)|import(?:.*?from\s+)?['\"](.*?)['\"];?|import\s*['\"](.*?)['\"];?"), #require('X') and import y from 'Y' and import 'Y'
    'java':re.compile(r'import\s+(?:static\s+)?([a-zA-Z0-9_]+)\..*?;'), #import X.Y -> get X, import static Z -> get Z
    'perl':re.compile(r'use\s+([a-zA-Z0-9_]+)(?:::[a-zA-Z0-9_]+)*[; ]'),
    'php': re.compile(r'(?:\b(?:require|require_once|include|include_once)\s*\(?\s*[\'"])([^\'"]+)(?:[\'"]\s*\)?)'),
    'matlab':re.compile(r'import\s+[\w\.]+\.\*'),
    #'matlab':re.compile(r'import\s+([a-zA-Z0-9_]+)\.?'),
    'objectivec':re.compile(r'import\s+(["<][\w/]+\.h[">])'),
    #'objectivec':re.compile(r'#import\s+<([a-zA-Z0-9_]+)\/'),
    'swift':re.compile(r'import\s+([\w.]+)'),
    #'swift':re.compile(r'import\s+([a-zA-Z0-9_]+)'),
    'cpp': re.compile(r'#\s*include\s*<([^>]+)>|#\s*include\s*"([^"]+)"'),
    'c#': re.compile(r'^using\s+([a-zA-Z_]\w*(\.[a-zA-Z_]\w*)*)\s*;\s*$', re.MULTILINE),
}


