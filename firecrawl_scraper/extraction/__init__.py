"""Extraction modules for Firecrawl Scraper."""

from .design_analyzer import DesignAnalyzer
from .seo_enrichment import SEOEnrichmentStrategy
from .universal_scraper import UniversalScraper

__all__ = [
    "DesignAnalyzer",
    "SEOEnrichmentStrategy",
    "UniversalScraper"
]
