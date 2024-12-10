#!/usr/bin/env python3

"""Check if async docstrings are the same as sync."""

import re
import sys
from pathlib import Path

from redbaron import RedBaron  # type: ignore[import-untyped]
from utils import sync_to_async_docstring

found_issues = False

# Get the directory of the source files
clients_path = Path(__file__).parent.resolve() / '../src/apify_client'

# Go through every Python file in that directory
for client_source_path in clients_path.glob('**/*.py'):
    with open(client_source_path, encoding='utf-8') as source_file:
        # Read the source file and parse the code using Red Baron
        red = RedBaron(source_code=source_file.read())

        # Find all classes which end with "ClientAsync" (there should be at most 1 per file)
        async_class = red.find('ClassNode', name=re.compile('.*ClientAsync$'))
        if not async_class:
            continue

        # Find the corresponding sync classes (same name, but without -Async)
        sync_class = red.find('ClassNode', name=async_class.name.replace('ClientAsync', 'Client'))

        # Go through all methods in the async class
        for async_method in async_class.find_all('DefNode'):
            # Find corresponding sync method in the sync class
            sync_method = sync_class.find('DefNode', name=async_method.name)

            # Skip methods with @ignore_docs decorator
            if len(async_method.decorators) and str(async_method.decorators[0].value) == 'ignore_docs':
                continue

            # If the sync method has a docstring, check if it matches the async dostring
            if sync_method and isinstance(sync_method.value[0].value, str):
                sync_docstring = sync_method.value[0].value
                async_docstring = async_method.value[0].value
                expected_docstring = sync_to_async_docstring(sync_docstring)

                if not isinstance(async_docstring, str):
                    print(f'Missing docstring for "{async_class.name}.{async_method.name}"!')
                    found_issues = True
                elif expected_docstring != async_docstring:
                    print(
                        f'Docstring for "{async_class.name}.{async_method.name}" is out of sync with "{sync_class.name}.{sync_method.name}"!'  # noqa: E501
                    )
                    found_issues = True

if found_issues:
    print()
    print('Issues with async docstrings found. Please fix them manually or by running `make fix-async-docstrings`.')
    sys.exit(1)
else:
    print('Success: async method docstrings are in sync with sync method docstrings.')
