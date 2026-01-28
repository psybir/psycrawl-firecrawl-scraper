#!/usr/bin/env python3
"""
Setup script for Firecrawl Scraper package

This allows the package to be installed with pip:
    pip install -e .  (development mode)
    pip install .     (production install)
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="psycrawl",
    version="2.7.0",
    author="PsyCrawl Contributors",
    author_email="",
    description="Maximum-value data extraction system with Firecrawl v2.7 and Spark 1 Pro",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/firecrawl-scraper",  # Update with your repo URL
    packages=find_packages(exclude=["tests", "examples", "data", "docs"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'psycrawl=firecrawl_scraper.cli:main',  # Primary CLI entry point
            'firecrawl-scraper=firecrawl_scraper.cli:main',  # Legacy alias
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=['web scraping', 'firecrawl', 'crawler', 'documentation', 'data extraction'],
    project_urls={
        'Documentation': 'https://github.com/yourusername/firecrawl-scraper#readme',
        'Source': 'https://github.com/yourusername/firecrawl-scraper',
        'Tracker': 'https://github.com/yourusername/firecrawl-scraper/issues',
    },
)
