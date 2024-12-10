#!/usr/bin/env python3

import re
from pathlib import Path

from redbaron import RedBaron  # type: ignore[import-untyped]
from utils import sync_to_async_docstring

# Get the directory of the source files
clients_path = Path(__file__).parent.resolve() / '../src/apify_client'

# Go through every Python file in that directory
for client_source_path in clients_path.glob('**/*.py'):
    with open(client_source_path, 'r+', encoding='utf-8') as source_file:
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

            # If the sync method has a docstring, copy it to the async method (with adjustments)
            if isinstance(sync_method.value[0].value, str):
                sync_docstring = sync_method.value[0].value
                async_docstring = async_method.value[0].value

                correct_async_docstring = sync_to_async_docstring(sync_docstring)
                if async_docstring == correct_async_docstring:
                    continue

                # Work around a bug in Red Baron, which indents docstrings too much when you insert them,
                # so we have to un-indent it one level first.
                correct_async_docstring = re.sub('^    ', '', correct_async_docstring, flags=re.MULTILINE)

                if not isinstance(async_docstring, str):
                    print(f'Fixing missing docstring for "{async_class.name}.{async_method.name}"...')
                    async_method.value.insert(0, correct_async_docstring)
                else:
                    async_method.value[0] = correct_async_docstring

        updated_source_code = red.dumps()

        # Work around a bug in Red Baron, which adds indents to docstrings when you insert them (including empty lines),
        # so we have to remove the extra whitespace
        updated_source_code = re.sub('^    $', '', updated_source_code, flags=re.MULTILINE)

        # Work around a bug in Red Baron, which indents `except` and `finally` statements wrong
        # so we have to add some extra whitespace
        updated_source_code = re.sub('^except', '        except', updated_source_code, flags=re.MULTILINE)
        updated_source_code = re.sub('^    except', '        except', updated_source_code, flags=re.MULTILINE)
        updated_source_code = re.sub('^finally', '        finally', updated_source_code, flags=re.MULTILINE)
        updated_source_code = re.sub('^    finally', '        finally', updated_source_code, flags=re.MULTILINE)

        # Work around a bug in Red Baron, which sometimes adds an extra new line to the end of a file
        updated_source_code = updated_source_code.rstrip() + '\n'

        # Save the updated source code back to the file
        source_file.seek(0)
        source_file.write(updated_source_code)
        source_file.truncate()
