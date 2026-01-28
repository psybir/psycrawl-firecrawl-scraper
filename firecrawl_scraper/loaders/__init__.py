"""
Loaders - Load external research data into pipeline models

Specialized loaders for different data sources:
- ResearchDataLoader: Load markdown/JSON research from external repos
"""

from .research_data_loader import ResearchDataLoader

__all__ = [
    'ResearchDataLoader',
]
