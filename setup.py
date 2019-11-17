#!/usr/local/bin python3
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="gitProjTool",
    version="0.0.2",
    author="Onion-Shen",
    author_email="18513385631@163.com",
    description="a tool that analyse project on git",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Onion-Shen/GitProjectTool",
    install_requires=["prettytable"],
    packages=["gitProjTool"],
    entry_points={
        'console_scripts': [
            'gitProjTool=gitProjTool:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS",
    ]
)
