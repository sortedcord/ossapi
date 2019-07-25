from distutils.core import setup
from setuptools import find_packages
from ossapi.__init__ import __version__

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="ossapi",
    version=__version__,
    description="A thin python wrapper around the osu! api, delegating error "
                "handling and rate limiting (among other things) to the user.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords = ["osu!, wrapper, api, python"],
    author="Liam DeVoe",
    author_email="orionldevoe@gmail.com",
    url="https://github.com/circleguard/ossapi",
    download_url = "https://github.com/circleguard/ossapi/tarball/v" + __version__,
    license="MIT",
    packages=find_packages(),
)
