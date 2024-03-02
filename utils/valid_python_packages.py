import re

import requests


BUILT_IN_PACKAGES = None
PYPI_PACKAGES = None
ALL_PACKAGES = None


def get_built_in_package_names():
    global BUILT_IN_PACKAGES
    if not BUILT_IN_PACKAGES:
        python2_url_path = "https://docs.python.org/2.7/py-modindex.html#cap-u"
        python3_url_path = "https://docs.python.org/3/py-modindex.html#cap-u"

        p2_resp = requests.get(python2_url_path)
        p3_resp = requests.get(python3_url_path)

        if p2_resp.status_code != 200 or p3_resp.status_code != 200:
            raise ValueError("Could not collect built-in package names")
        
        pattern = '<code class="xref">(\w+)</code>'
        BUILT_IN_PACKAGES =\
            re.findall(pattern, p2_resp.text) +\
            re.findall(pattern, p3_resp.text)
    return set(BUILT_IN_PACKAGES)


def get_pypi_package_names():
    global PYPI_PACKAGES
    if not PYPI_PACKAGES:
        url = "https://pypi.org/simple/"
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ValueError("Could not collect PYPI package names")
        pattern = '<a href=".*">(.*)</a>'
        PYPI_PACKAGES = set(re.findall(pattern, resp.text))
    return PYPI_PACKAGES


def get_all_package_names():
    global ALL_PACKAGES
    if not ALL_PACKAGES:
        ALL_PACKAGES =  get_built_in_package_names() | get_pypi_package_names()
    return ALL_PACKAGES
