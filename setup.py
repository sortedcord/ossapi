import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="osuAPI",
    version="1.1.1",
    author="Liam DeVoe",
    author_email="orionldevoe@gmail.com",
    description="A simple, incomplete python wrapper for the osu api.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/circleguard/osu-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
