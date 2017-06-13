#!/usr/bin/env python3

import os
from setuptools import setup, find_packages
import easyhtml

setup(
    name = "easyhtml",
    version = easyhtml.__version__,
    fullname = "EasyHTML",
    description = "A package that provides an API to create a DOM of HTML documents and access to its elements",
    author = "Taras Gaidukov",
    author_email = "kemaweyan@gmail.com",
    keywords = "html dom parser",
    long_description = open('README').read(),
    url = "https://github.com/Kemaweyan/easyhtml",
    license = "GPLv3",
    packages=find_packages(exclude=["tests"]),
    test_suite='tests'
)
