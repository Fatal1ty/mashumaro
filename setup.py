#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="mashumaro",
    version="2.6.3",
    description="Fast serialization framework on top of dataclasses",
    long_description=open("README.md", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    platforms="all",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
    ],
    license="Apache License, Version 2.0",
    author="Alexander Tikhonov",
    author_email="random.gauss@gmail.com",
    url="https://github.com/Fatal1ty/mashumaro",
    packages=find_packages(include=("mashumaro", "mashumaro.*")),
    package_data={"mashumaro": ["py.typed"]},
    python_requires=">=3.6",
    install_requires=[
        "dataclasses;python_version=='3.6'",
        "msgpack>=0.5.6",
        "pyyaml>=3.13",
        "backports-datetime-fromisoformat;python_version=='3.6'",
        "typing_extensions",
    ],
    zip_safe=False,
)
