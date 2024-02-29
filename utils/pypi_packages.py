import re

import requests


PYPI_PACKAGES = None


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
