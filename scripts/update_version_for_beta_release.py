#!/usr/bin/env python3

import json
import re
import urllib.request

from utils import PACKAGE_NAME, get_current_package_version, set_current_package_version

# Checks whether the current package version number was not already used in a published release,
# and if not, modifies the package version number in src/package_name/_version.py from a stable release version (X.Y.Z) to a beta version (X.Y.ZbN)
if __name__ == '__main__':
    current_version = get_current_package_version()

    # We can only transform a stable release version (X.Y.Z) to a beta version (X.Y.ZbN)
    if not re.match(r'^\d+\.\d+\.\d+$', current_version):
        raise RuntimeError(f'The current version {current_version} does not match the proper semver format for stable releases (X.Y.Z)')

    # Load the version numbers of the currently published versions from PyPI
    # If the URL returns 404, it means the package has no releases yet (which is okay in our case)
    package_info_url = f'https://pypi.org/pypi/{PACKAGE_NAME}/json'
    try:
        conn = urllib.request.urlopen(package_info_url)
        package_data = json.load(urllib.request.urlopen(package_info_url))
        published_versions = list(package_data['releases'].keys())
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise e
        published_versions = []

    # We don't want to publish a beta version with the same version number as an already released stable version
    if current_version in published_versions:
        raise RuntimeError(f'The current version {current_version} was already released!')

    # Find the highest beta version number that was already published
    latest_beta = 0
    for version in published_versions:
        if version.startswith(f'{current_version}b'):
            beta_version = int(version.split('b')[1])
            if beta_version > latest_beta:
                latest_beta = beta_version

    # Write the latest beta version number to src/package_name/_version.py
    new_beta_version_number = f'{current_version}b{latest_beta + 1}'
    set_current_package_version(new_beta_version_number)
