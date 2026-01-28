"""
Integrations - Transform external data into pipeline models

Converts data from external sources (research repos, APIs, etc.)
into the canonical pipeline models for processing.
"""

from .research_integration import ResearchIntegration

__all__ = [
    'ResearchIntegration',
]
