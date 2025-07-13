#!/usr/bin/env python3
"""
Setup script for the deduper package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A platform-agnostic CLI tool for finding and managing duplicate files."


setup(
    name="deduper",
    version="1.0.0",
    author="Deduper Team",
    author_email="",
    description="A platform-agnostic CLI tool for finding and managing duplicate files",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "deduper=deduper.cli_click:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="duplicate files deduplication cli utility",
    project_urls={
        "Bug Reports": "",
        "Source": "",
        "Documentation": "",
    },
) 