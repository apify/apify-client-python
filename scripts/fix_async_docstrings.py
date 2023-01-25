import re
from pathlib import Path

from redbaron import RedBaron  # type: ignore
from utils import sync_to_async_docstring

clients_path = Path(__file__).parent.resolve() / '../src/apify_client'
for client_source_path in clients_path.glob('**/*.py'):
    with open(client_source_path, 'r+') as source_file:
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
                correct_async_docstring = sync_to_async_docstring(sync_docstring)
                if async_docstring == correct_async_docstring:
                    continue

                # work around a bug in Red Baron, which indents docstrings too much when you insert them, so we have to un-indent it one level first
                correct_async_docstring = re.sub('^    ', '', correct_async_docstring, flags=re.M)

                if not isinstance(async_docstring, str):
                    print(f'Fixing missing docstring for "{async_class.name}.{async_method.name}"...')
                    async_method.value.insert(0, correct_async_docstring)
                else:
                    async_method.value[0] = correct_async_docstring

        updated_source_code = red.dumps()

        # work around a bug in Red Baron, which adds indents to docstrings when you insert them (including empty lines),
        # so we have to remove the extra whitespace
        updated_source_code = re.sub('^    $', '', updated_source_code, flags=re.M)

        # work around a bug in Red Baron, which indents `except` and `finally` statements wrong
        # so we have to add some extra whitespace
        updated_source_code = re.sub('^except', '        except', updated_source_code, flags=re.M)
        updated_source_code = re.sub('^    except', '        except', updated_source_code, flags=re.M)
        updated_source_code = re.sub('^finally', '        finally', updated_source_code, flags=re.M)
        updated_source_code = re.sub('^    finally', '        finally', updated_source_code, flags=re.M)

        # work around a bug in Red Baron, which sometimes adds an extra new line to the end of a file
        updated_source_code = updated_source_code.rstrip() + '\n'

        source_file.seek(0)
        source_file.write(updated_source_code)
        source_file.truncate()
