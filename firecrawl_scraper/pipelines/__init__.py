"""
PsyCrawl Pipelines

Automated data extraction pipelines for lead generation
and business intelligence using Firecrawl v2.7 and Spark 1 Pro.
"""

from .lead_pipeline import (
    LeadPipeline,
    Lead,
    extract_leads_for_industry,
    burn_credits_campaign
)

__all__ = [
    'LeadPipeline',
    'Lead',
    'extract_leads_for_industry',
    'burn_credits_campaign'
]
