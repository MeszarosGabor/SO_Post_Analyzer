import re
import typing


def to_lowercase_underscored(items: typing.List[str]):
    return [re.sub("-", "_", item).lower() for item in items]
