import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apify_client",
    version="0.0.1",
    author="Apify Technologies s.r.o.",
    author_email="support@apify.com",
    description="Work in progress: Apify API client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/apifytech/apify-client-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

