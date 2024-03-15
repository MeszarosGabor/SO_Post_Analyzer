import subprocess  # must have ruby and gems installed !!!
import typing

import utils.common as common

ALL_RUBY_PACKAGES = None


def get_all_package_names() -> typing.Set:
    global ALL_RUBY_PACKAGES

    if ALL_RUBY_PACKAGES is None:
        result = subprocess.run(["gem", "search", "-b", ".*"], capture_output=True, text=True)
        if result.returncode != 0:
            raise ValueError("Gems could not be collected! Call a plumber!")

        libs_raw = result.stdout.split("\n")
        libs_curated = [
            lb for lb in libs_raw if lb and lb not in (
                            '*** LOCAL GEMS ***',
                            '*** REMOTE GEMS ***')
        ]
        libs_formatted = [l.split()[0] for l in libs_curated]

        ALL_RUBY_PACKAGES = set(common.to_lowercase_underscored(libs_formatted))

    return ALL_RUBY_PACKAGES
