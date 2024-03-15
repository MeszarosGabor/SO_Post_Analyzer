import pytest

import utils.common as common


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
    assert common.to_lowercase_underscored([word]) == ['foo_bar']