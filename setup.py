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
    raise RuntimeError("Unable to find version string.")

setup(
    name='apify_client',
    version=version,

    author="Apify Technologies s.r.o.",
    author_email="support@apify.com",
    url="https://github.com/apify/apify-client-python",
    project_urls={
        'Documentation': 'https://docs.apify.com/apify-client-python',
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
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='apify, api, client, scraping, automation',

    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
    install_requires=['requests ~= 2.25.1'],
    extras_require={
        'dev': [
            'autopep8 ~= 1.5.5',
            'flake8 ~= 3.8.4',
            'flake8-commas ~= 2.0.0',
            'flake8-docstrings ~= 1.5.0',
            'flake8-isort ~= 4.0.0',
            'isort ~= 5.7.0',
            'mypy ~= 0.812',
            'pep8-naming ~= 0.11.1',
            'pytest ~= 6.2.2',
            'sphinx ~= 3.5.1',
            'sphinx-autodoc-typehints ~= 1.11.1',
            'sphinx-markdown-builder ~= 0.5.4',
        ],
    },
)
