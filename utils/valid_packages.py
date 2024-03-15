from utils.valid_python_packages import get_all_package_names as python_get_all_package_names
from utils.valid_ruby_packages import get_all_package_names as ruby_get_all_package_names


def get_valid_packages(target_language: str):
    target_getter = {
        "python": python_get_all_package_names,
        "ruby": ruby_get_all_package_names,
    }.get(target_language)
    if target_getter is None:
        return None

    return target_getter()
