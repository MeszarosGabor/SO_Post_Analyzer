from unittest.mock import patch, MagicMock

import pytest

import utils.valid_python_packages as valid_python_packages


@pytest.mark.parametrize(
    "word",
     [
        'foo-bar',
        'foo_bar',
        'Foo-Bar',
        'Foo_Bar',
        'FOO-BAR',
        'FOO_BAR',
    ],
)
def test_to_lowercase_underscored(word):
    assert valid_python_packages.to_lowercase_underscored([word]) == ['foo_bar']



@pytest.fixture
def set_BUILT_IN_PACKAGES():
    before_BUILT_IN_PACKAGES = valid_python_packages.BUILT_IN_PACKAGES
    yield
    valid_python_packages.BUILT_IN_PACKAGES = before_BUILT_IN_PACKAGES


@pytest.fixture
def set_PYPI_PACKAGES():
    before_PYPI_PACKAGES = valid_python_packages.PYPI_PACKAGES
    yield
    valid_python_packages.PYPI_PACKAGES = before_PYPI_PACKAGES


@pytest.fixture
def set_globals(set_BUILT_IN_PACKAGES, set_PYPI_PACKAGES):
    pass


def test_get_built_in_package_names_only_call_twice(set_globals):
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


def test_get_pypi_package_names_only_call_once(set_globals):
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


def test_get_all_package_names_only_call_once(set_globals):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = 'foo bar'
    with patch(
        "utils.valid_python_packages.requests"
    ) as mock_requests:
        mock_requests.get.return_value = mock_resp
        valid_python_packages.get_all_package_names()
        valid_python_packages.get_all_package_names()

        assert len(mock_requests.method_calls) == 3
