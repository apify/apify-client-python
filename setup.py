import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

version_file = (here / 'src/apify_client/_version.py').read_text(encoding='utf-8')
version = None
for line in version_file.splitlines():
    if line.startswith('__version__'):
        delim = '"' if '"' in line else "'"
        version = line.split(delim)[1]
        break
else:
    raise RuntimeError('Unable to find version string.')

setup(
    name='apify_client',
    version=version,

    author='Apify Technologies s.r.o.',
    author_email='support@apify.com',
    url='https://github.com/apify/apify-client-python',
    project_urls={
        'Documentation': 'https://docs.apify.com/api/client/python/',
        'Source': 'https://github.com/apify/apify-client-python',
        'Issue tracker': 'https://github.com/apify/apify-client-python/issues',
        'Apify Homepage': 'https://apify.com',
    },
    license='Apache Software License',
    license_files=['LICENSE'],

    description='Apify API client for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='apify, api, client, scraping, automation',

    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={'apify_client': ['py.typed']},
    python_requires='>=3.8',
    install_requires=[
        'httpx ~= 0.23.0',
    ],
    extras_require={
        'dev': [
            'autopep8 ~= 2.0.1',
            'flake8 ~= 6.0.0',
            'flake8-bugbear ~= 23.1.20',
            'flake8-commas ~= 2.1.0',
            'flake8-comprehensions ~= 3.10.1',
            'flake8-datetimez ~= 20.10.0',
            'flake8-docstrings ~= 1.7.0',
            'flake8-isort ~= 6.0.0',
            'flake8-noqa ~= 1.3.0',
            'flake8-pytest-style ~= 1.7.2',
            'flake8-quotes ~= 3.3.1',
            'flake8-unused-arguments ~= 0.0.13',
            'isort ~= 5.12.0',
            'mypy ~= 1.0.0',
            'pep8-naming ~= 0.13.2',
            'pre-commit ~= 3.0.1',
            'pytest ~= 7.2.0',
            'pytest-asyncio ~= 0.20.3',
            'pytest-only ~= 2.0.0',
            'pytest-randomly ~= 3.12.0',
            'pytest-timeout ~= 2.1.0',
            'pytest-xdist ~= 3.2.0',
            'redbaron ~= 0.9.2',
            'sphinx ~= 6.1.3',
            'sphinx-autodoc-typehints ~= 1.22',
            'sphinx-markdown-builder == 0.5.4',  # pinned to 0.5.4, because 0.5.5 has a formatting bug
            'types-setuptools',  # always latest, since we always install latest setuptools
        ],
    },
)
