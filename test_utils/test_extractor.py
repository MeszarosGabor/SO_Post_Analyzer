from unittest.mock import patch

import pytest

import utils.extractor as extractor


@pytest.mark.parametrize(
    "snippet,expected_imports",
    [
        pytest.param(
            "import foo",
            {"foo"},
            id="Simple full import",
        ),
        pytest.param(
            "from foo import Foo",
            {"foo"},
            id="Simple >>from<< import",
        ),
        pytest.param(
            'import urllib2\nfrom BeautifulSoup import BeautifulSoup\nsoup = BeautifulSoup(urllib2.urlopen("https://www.google.com"))\nprint soup.title.string',
            {"BeautifulSoup", "urllib2"},
            id="multiple imports real scenario #1"
        ),
        pytest.param(
            'from lxml import etree\nfrom StringIO import StringIO\netree.parse(StringIO(html), etree.HTMLParser(recover=False))',
            {"StringIO", "lxml"},
            id="multiple imports real scenario #2"
        ),
        pytest.param(
            'import os,sys',
            {"os", "sys"},
            id="Comma separated import",
        ),
        pytest.param(
            'import os;',
            {"os"},
            id="Trailing semicolon",
        ),
    ]
)
def test_extract_import_statements_from_code(snippet, expected_imports):
    imports = extractor.extract_import_statements_from_code(snippet)
    assert imports == expected_imports


@pytest.mark.parametrize(
    "parsed_row,expected_imports",
    [
        pytest.param(
            {
                "code_snippets":  [
                    'import urllib2\nfrom BeautifulSoup import BeautifulSoup\nsoup = BeautifulSoup(urllib2.urlopen("https://www.google.com"))\nprint soup.title.string',
                ],
            },
            ['BeautifulSoup', 'urllib2'],
            id="Multiline multiple imports"
        ),
        pytest.param(
            {
                "code_snippets":  [
                    'import urllib2\nfrom BeautifulSoup import BeautifulSoup\nsoup = BeautifulSoup(urllib2.urlopen("https://www.google.com"))\nprint soup.title.string',
                    'from lxml import etree\nfrom StringIO import StringIO\netree.parse(StringIO(html), etree.HTMLParser(recover=False))',
                ],
            },
            ['BeautifulSoup', 'StringIO', 'lxml', 'urllib2'],
            id="Multiple snippets, multiple multiline imports"
        ),
    ],
)
def test_extract_import_statements_from_single_row_find_valid(parsed_row, expected_imports):
    with patch(
        "utils.valid_python_packages.get_all_package_names",
        return_value={
            'urllib2',
            'beautifulsoup',
            'lxml',
            'stringio',
            }
    ):
        _, _, import_list, _ = extractor.extract_import_statements_from_single_row(
            post_id="123",
            parsed_data=parsed_row
        )
    assert import_list == expected_imports



@pytest.mark.parametrize(
    "parsed_row,expected_imports",
    [
        pytest.param(
            {
                "code_snippets":  [
                    "import invalidpackage\nimporturllib2",
                ],
            },
            ['invalidpackage'],
            id="invalid package present"
        ),
    ],
)
def test_extract_import_statements_from_single_row_find_invalid(parsed_row, expected_imports):
    with patch(
        "utils.valid_python_packages.get_all_package_names",
        return_value={
            'urllib2',
            }
    ):
        _, _, _, invalid_list = extractor.extract_import_statements_from_single_row(
            post_id="123",
            parsed_data=parsed_row
        )
    assert invalid_list == expected_imports
