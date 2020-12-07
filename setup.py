import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='apify_client',
    version='0.0.1',

    author="Apify Technologies s.r.o.",
    author_email="support@apify.com",
    url="https://github.com/apify/apify-client-python",
    project_urls={
        'Apify Homepage': 'https://apify.com',
    },

    description='Apify API client for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='apify, api, client, scraping, automation',

    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
    install_requires=['requests ~=2.25.0'],
    extras_require={
        'dev': [
            'flake8 ~= 3.8.4',
            'flake8-commas ~= 2.0.0',
            'flake8-docstrings ~= 1.5.0',
            'flake8-isort ~= 4.0.0',
            'isort ~= 5.6.4',
            'mypy ~= 0.790',
            'pep8-naming ~= 0.11.1',
            'pytest ~= 6.1.2',
        ],
    },
)
