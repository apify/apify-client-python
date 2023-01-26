import re
import sys
from pathlib import Path

from redbaron import RedBaron  # type: ignore
from utils import sync_to_async_docstring

found_issues = False

clients_path = Path(__file__).parent.resolve() / '../src/apify_client'
for client_source_path in clients_path.glob('**/*.py'):
    with open(client_source_path, 'r') as source_file:
        red = RedBaron(source_code=source_file.read())
        async_class = red.find('ClassNode', name=re.compile('.*ClientAsync$'))
        if not async_class:
            continue
        sync_class = red.find('ClassNode', name=async_class.name.replace('ClientAsync', 'Client'))
        for async_method in async_class.find_all('DefNode'):
            sync_method = sync_class.find('DefNode', name=async_method.name)
            if isinstance(sync_method.value[0].value, str):
                sync_docstring = sync_method.value[0].value
                async_docstring = async_method.value[0].value
                expected_docstring = sync_to_async_docstring(sync_docstring)

                if not isinstance(async_docstring, str):
                    print(f'Missing docstring for "{async_class.name}.{async_method.name}"!')
                    found_issues = True
                    continue
                if expected_docstring != async_docstring:
                    print(f'Docstring for "{async_class.name}.{async_method.name}" is out of sync with "{sync_class.name}.{sync_method.name}"!')
                    found_issues = True

if found_issues:
    print()
    print('Issues with async docstrings found. Please fix them manually or by running `make fix-async-docstrings`.')
    sys.exit(1)
else:
    print('Success: async method docstrings are in sync with sync method docstrings.')
