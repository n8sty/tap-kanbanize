#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-kanbanize",
    version="0.1.1",
    description="Singer.io tap for extracting data",
    author="Nate Giraldi",
    author_email="ng269@cornell.edu",
    url="https://github.com/n8sty/tap-kanbanize",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_kanbanize"],
    install_requires=[
        "singer-python>=5.0.12",
        "requests",
    ],
    extras_require={
        "dev": [
            "nose>=1.3.7"
        ]
    },
    entry_points="""
        [console_scripts]
        tap-kanbanize=tap_kanbanize:main
    """,
    packages=["tap_kanbanize"],
    package_data={
        "schemas": ["tap_kanbanize/schemas/*.json"]
    },
    include_package_data=True,
)
