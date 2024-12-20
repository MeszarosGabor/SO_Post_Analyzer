import re
import typing

import requests

from utils.common import to_lowercase_underscored


BUILT_IN_PACKAGES = None
PYPI_PACKAGES = None
ALL_PACKAGES = None

VALID_PACKAGE_WHITELIST = {
    'rest_framework',  # https://pypi.org/project/djangorestframework/
    'win32com',  # https://pypi.org/project/pywin32/;https://pbpython.com/windows-com.html   # noqa: E501
    'win32api',  # https://pypi.org/project/pywin32/
    'win32con',  # https://pypi.org/project/pywin32/
}


def get_built_in_package_names() -> typing.Set:
    global BUILT_IN_PACKAGES
    if BUILT_IN_PACKAGES is None:
        python2_url_path = "https://docs.python.org/2.7/py-modindex.html#cap-u"
        python3_url_path = "https://docs.python.org/3/py-modindex.html#cap-u"

        p2_resp = requests.get(python2_url_path)
        p3_resp = requests.get(python3_url_path)

        if p2_resp.status_code != 200 or p3_resp.status_code != 200:
            raise ValueError("Could not collect built-in package names")

        pattern = r'<code class="xref">(\w+)</code>'
        BUILT_IN_PACKAGES =\
            to_lowercase_underscored(re.findall(pattern, p2_resp.text)) +\
            to_lowercase_underscored(re.findall(pattern, p3_resp.text))

    return set(BUILT_IN_PACKAGES)


def get_pypi_package_names() -> typing.Set:
    global PYPI_PACKAGES
    if PYPI_PACKAGES is None:
        url = "https://pypi.org/simple/"
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ValueError("Could not collect PYPI package names")
        pattern = '<a href=".*">(.*)</a>'
        PYPI_PACKAGES = set(
            to_lowercase_underscored(re.findall(pattern, resp.text))
        )

    return PYPI_PACKAGES


def get_all_package_names() -> typing.Set:
    global ALL_PACKAGES, VALID_PACKAGE_WHITELIST
    if ALL_PACKAGES is None:
        ALL_PACKAGES = (
            VALID_PACKAGE_WHITELIST |
            get_built_in_package_names() |
            get_pypi_package_names()
        )

    return ALL_PACKAGES
