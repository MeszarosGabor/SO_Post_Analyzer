# flake8: noqa501
from unittest.mock import patch, MagicMock

import pytest

import utils.valid_python_packages as valid_python_packages


@pytest.fixture(autouse=True)
def set_VALID_PACKAGE_WHITELIST():
    before_VALID_PACKAGE_WHITELIST = valid_python_packages.VALID_PACKAGE_WHITELIST
    yield
    valid_python_packages.VALID_PACKAGE_WHITELIST = before_VALID_PACKAGE_WHITELIST


@pytest.fixture(autouse=True)
def set_BUILT_IN_PACKAGES():
    before_BUILT_IN_PACKAGES = valid_python_packages.BUILT_IN_PACKAGES
    yield
    valid_python_packages.BUILT_IN_PACKAGES = before_BUILT_IN_PACKAGES


@pytest.fixture(autouse=True)
def set_PYPI_PACKAGES():
    before_PYPI_PACKAGES = valid_python_packages.PYPI_PACKAGES
    yield
    valid_python_packages.PYPI_PACKAGES = before_PYPI_PACKAGES


def test_get_built_in_package_names_only_call_twice():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = 'foo bar'
    with patch(
        "utils.valid_python_packages.requests"
    ) as mock_requests:
        mock_requests.get.return_value = mock_resp
        valid_python_packages.get_built_in_package_names()
        valid_python_packages.get_built_in_package_names()

        assert len(mock_requests.method_calls) == 2


def test_get_pypi_package_names_only_call_once():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = 'foo bar'
    with patch(
        "utils.valid_python_packages.requests"
    ) as mock_requests:
        mock_requests.get.return_value = mock_resp
        valid_python_packages.get_pypi_package_names()
        valid_python_packages.get_pypi_package_names()
  
        assert len(mock_requests.method_calls) == 1


def test_get_all_package_names_only_call_once():
    with (
        patch("utils.valid_python_packages.get_built_in_package_names") as
            mock_get_built_in_package_names, 
        patch("utils.valid_python_packages.get_pypi_package_names") as
            mock_get_pypi_package_names,
    ):
        mock_get_built_in_package_names.return_value = {"foo"}
        mock_get_pypi_package_names.return_value = {"bar"}
        valid_python_packages.get_all_package_names()
        valid_python_packages.get_all_package_names()

        assert mock_get_built_in_package_names._mock_call_count == 1
        assert mock_get_pypi_package_names._mock_call_count == 1
