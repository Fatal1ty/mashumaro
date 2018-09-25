#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="mashumaro",
    version="0.1.3",
    description="Fast serialization framework on top of dataclasses",
    platforms="all",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 3 - Alpha",
    ],
    license="Apache License, Version 2.0",
    author="Alexander Tikhonov",
    author_email="random.gauss@gmail.com",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.6",
    install_requires=[
        "dataclasses;python_version=='3.6'",
        "msgpack>=0.5.6",
        "pyyaml>=3.13",
    ]
)
