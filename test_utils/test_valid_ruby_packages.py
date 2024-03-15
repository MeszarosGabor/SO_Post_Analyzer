import dataclasses
from unittest.mock import patch

import pytest

import utils.valid_ruby_packages as valid_ruby_packages

@dataclasses.dataclass
class MockResp:
        returncode: int = 0
        stdout: str = '*** LOCAL GEMS ***\nfoo\n\n*** REMOTE GEMS ***\nbar\n'


@pytest.fixture(autouse=True)
def set_ALL_RUBY_PACKAGES():
    before_ALL_RUBY_PACKAGES = valid_ruby_packages.ALL_RUBY_PACKAGES
    yield
    valid_ruby_packages.ALL_RUBY_PACKAGES = before_ALL_RUBY_PACKAGES


def test_get_all_package_names():
    with patch("utils.valid_ruby_packages.subprocess.run") as mock_sp:
        mock_sp.return_value = MockResp(returncode=0, stdout="foo\nbar")
        response = valid_ruby_packages.get_all_package_names()
        
        assert response == {'bar', 'foo'}


def test_get_all_package_names_filters_headers_and_empty_lines():
    with patch("utils.valid_ruby_packages.subprocess.run") as mock_sp:
        mock_sp.return_value = MockResp()
        response = valid_ruby_packages.get_all_package_names()
        
        assert response == {'bar', 'foo'}


def test_get_ruby_package_names_only_call_once():
    with patch("utils.valid_ruby_packages.subprocess.run") as mock_sp:
        mock_sp.return_value = MockResp()

        valid_ruby_packages.get_all_package_names()
        valid_ruby_packages.get_all_package_names()
  
        assert mock_sp.call_count == 1
