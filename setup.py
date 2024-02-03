import os
import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="svd-downloader",
    packages=["svd_downloader"],
    version=os.environ["RELEASE_VERSION"],
    license="MIT",
    description="Simple utility to download Saarbruecken Voice Database",
    author="Rijul Gupta",
    author_email="rijulg@neblar.com",
    url="https://github.com/rijulg/svd-downloader",
    keywords=["Downloader", "SVD", "Disordered Voice Database"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "dask>=2024.1.1",
        "beautifulsoup4>=4.12.3",
        "requests>=2.31.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
)
