#!/usr/bin/env python3
"""
Lead Generation Pipeline for PsyCrawl

Automated extraction of business lead data for 360 virtual tour sales.
Uses Spark 1 Pro for maximum quality extraction.

Credit Usage Strategy:
- 93,500 available credits
- Target: 1,300+ business leads
- ~50-100 credits per deep extraction

Usage:
    from firecrawl_scraper.pipelines.lead_pipeline import LeadPipeline

    pipeline = LeadPipeline()
    leads = await pipeline.extract_industry_leads('wineries', region='Lehigh Valley PA')
"""

import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass, field
import logging

from tqdm import tqdm

from ..config import Config
from ..core.firecrawl_client import EnhancedFirecrawlClient

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Lead:
    """Business lead data"""
    name: str
    source_url: str
    industry: str
    region: Optional[str] = None

    # Contact
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

    # Decision makers
    owner_name: Optional[str] = None
    decision_makers: List[Dict] = field(default_factory=list)

    # Social
    social_media: Dict = field(default_factory=dict)

    # Virtual tour status
    has_virtual_tour: bool = False
    virtual_tour_provider: Optional[str] = None

    # Ratings
    google_rating: Optional[float] = None
    google_reviews_count: Optional[int] = None

    # Services
    services: List[str] = field(default_factory=list)

    # Intelligence
    pain_points: List[str] = field(default_factory=list)
    marketing_gaps: List[str] = field(default_factory=list)
    competitors_nearby: List[str] = field(default_factory=list)

    # Scoring
    lead_score: int = 50
    lead_notes: Optional[str] = None

    # Metadata
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    credits_used: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'source_url': self.source_url,
            'industry': self.industry,
            'region': self.region,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'owner_name': self.owner_name,
            'decision_makers': self.decision_makers,
            'social_media': self.social_media,
            'has_virtual_tour': self.has_virtual_tour,
            'virtual_tour_provider': self.virtual_tour_provider,
            'google_rating': self.google_rating,
            'google_reviews_count': self.google_reviews_count,
            'services': self.services,
            'pain_points': self.pain_points,
            'marketing_gaps': self.marketing_gaps,
            'competitors_nearby': self.competitors_nearby,
            'lead_score': self.lead_score,
            'lead_notes': self.lead_notes,
            'extracted_at': self.extracted_at,
            'credits_used': self.credits_used
        }

    @classmethod
    def from_dict(cls, data: dict, url: str, industry: str) -> 'Lead':
        """Create Lead from extraction result"""
        return cls(
            name=data.get('name') or data.get('business_name', 'Unknown'),
            source_url=url,
            industry=industry,
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            phone=data.get('phone'),
            email=data.get('email'),
            website=data.get('website'),
            owner_name=data.get('owner_name'),
            decision_makers=data.get('decision_makers', []),
            social_media=data.get('social_media', {}),
            has_virtual_tour=data.get('has_virtual_tour', False),
            virtual_tour_provider=data.get('virtual_tour_provider'),
            google_rating=data.get('google_rating'),
            google_reviews_count=data.get('google_reviews_count'),
            services=data.get('services', []),
            pain_points=data.get('pain_points', []),
            marketing_gaps=data.get('marketing_gaps', []),
            competitors_nearby=data.get('competitors_nearby', []),
            lead_score=data.get('lead_score', 50),
            lead_notes=data.get('lead_notes')
        )


@dataclass
class PipelineStats:
    """Pipeline execution statistics"""
    total_urls_processed: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    total_credits_used: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def get_duration(self) -> float:
        """Get duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

    def get_success_rate(self) -> float:
        """Get success rate percentage"""
        if self.total_urls_processed == 0:
            return 0.0
        return (self.successful_extractions / self.total_urls_processed) * 100


# ============================================================================
# INDUSTRY CONFIGURATIONS
# ============================================================================

INDUSTRY_SEARCH_TEMPLATES = {
    'wineries': [
        "{region} wineries",
        "{region} wine tasting",
        "{region} vineyards",
        "wineries near {region}"
    ],
    'auto_dealerships': [
        "{region} car dealerships",
        "{region} auto dealers",
        "used cars {region}",
        "new car dealer {region}"
    ],
    'senior_living': [
        "{region} senior living communities",
        "{region} assisted living",
        "{region} retirement homes",
        "nursing homes {region}"
    ],
    'wedding_venues': [
        "{region} wedding venues",
        "{region} event venues",
        "{region} wedding reception",
        "banquet halls {region}"
    ],
    'fitness_centers': [
        "{region} gyms",
        "{region} fitness centers",
        "{region} health clubs",
        "crossfit {region}"
    ],
    'medical_dental': [
        "{region} dental office",
        "{region} dentist",
        "{region} medical practice",
        "{region} doctor office"
    ],
    'real_estate': [
        "{region} real estate agents",
        "{region} realtors",
        "{region} property listings",
        "homes for sale {region}"
    ],
    'restaurants': [
        "{region} restaurants",
        "{region} fine dining",
        "{region} catering",
        "private dining {region}"
    ]
}

INDUSTRY_SCHEMAS = {
    'wineries': {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"},
            "has_virtual_tour": {"type": "boolean"},
            "has_event_space": {"type": "boolean"},
            "offers_tastings": {"type": "boolean"},
            "wedding_venue": {"type": "boolean"},
            "google_rating": {"type": "number"},
            "wine_varieties": {"type": "array", "items": {"type": "string"}},
            "owner_name": {"type": "string"},
            "social_media": {"type": "object"},
            "pain_points": {"type": "array", "items": {"type": "string"}},
            "marketing_gaps": {"type": "array", "items": {"type": "string"}}
        }
    },
    'general': {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "email": {"type": "string"},
            "website": {"type": "string"},
            "has_virtual_tour": {"type": "boolean"},
            "google_rating": {"type": "number"},
            "google_reviews_count": {"type": "integer"},
            "services": {"type": "array", "items": {"type": "string"}},
            "owner_name": {"type": "string"},
            "social_media": {"type": "object"},
            "pain_points": {"type": "array", "items": {"type": "string"}},
            "marketing_gaps": {"type": "array", "items": {"type": "string"}}
        }
    }
}


# ============================================================================
# LEAD PIPELINE
# ============================================================================

class LeadPipeline:
    """
    Automated lead extraction pipeline using Spark 1 Pro.

    Designed to maximize value from 93.5k available Firecrawl credits.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize pipeline"""
        self.client = EnhancedFirecrawlClient()
        self.output_dir = output_dir or Config.LEAD_OUTPUT_DIR
        self.stats = PipelineStats()

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def discover_urls(
        self,
        industry: str,
        region: str,
        max_urls: int = 100
    ) -> List[str]:
        """
        Discover business URLs for an industry/region

        Args:
            industry: Industry type
            region: Geographic region
            max_urls: Maximum URLs to discover

        Returns:
            List of discovered URLs
        """
        templates = INDUSTRY_SEARCH_TEMPLATES.get(industry, ["{region} businesses"])
        all_urls = set()

        for template in templates:
            query = template.format(region=region)
            logger.info(f"Searching: {query}")

            result = await self.client.search(
                query=query,
                limit=10,
                scrape_options={'formats': ['markdown']}
            )

            if result.get('success'):
                for item in result.get('data', []):
                    url = item.get('url')
                    if url:
                        all_urls.add(url)

            if len(all_urls) >= max_urls:
                break

        return list(all_urls)[:max_urls]

    async def extract_lead(
        self,
        url: str,
        industry: str,
        region: Optional[str] = None
    ) -> Optional[Lead]:
        """
        Extract lead data from a single URL

        Args:
            url: Business website URL
            industry: Industry type for context
            region: Geographic region

        Returns:
            Lead object or None if extraction failed
        """
        schema = INDUSTRY_SCHEMAS.get(industry, INDUSTRY_SCHEMAS['general'])

        system_prompt = f"""You are a business intelligence expert extracting lead data for a 360 virtual tour company.

Industry: {industry}
Region: {region or 'Not specified'}

Focus on:
1. Identifying businesses that could benefit from virtual tours
2. Finding contact information for decision makers
3. Detecting marketing gaps (no virtual presence, outdated website, etc.)
4. Noting any existing virtual tours or 360 content

Be thorough but accurate. Only extract information that is clearly present."""

        try:
            result = await self.client.extract(
                urls=[url],
                schema=schema,
                system_prompt=system_prompt,
                model='spark-1-pro',
                max_poll_time=180.0
            )

            if result.get('success'):
                data = result.get('data', {})
                lead = Lead.from_dict(data, url, industry)
                lead.region = region
                lead.credits_used = result.get('creditsUsed', 5)
                self.stats.successful_extractions += 1
                self.stats.total_credits_used += lead.credits_used
                return lead
            else:
                logger.warning(f"Extraction failed for {url}: {result.get('error')}")
                self.stats.failed_extractions += 1
                return None

        except Exception as e:
            logger.error(f"Error extracting {url}: {e}")
            self.stats.failed_extractions += 1
            return None

    async def extract_leads_batch(
        self,
        urls: List[str],
        industry: str,
        region: Optional[str] = None,
        concurrency: int = 3
    ) -> List[Lead]:
        """
        Extract leads from multiple URLs with controlled concurrency

        Args:
            urls: List of URLs to process
            industry: Industry type
            region: Geographic region
            concurrency: Max concurrent extractions

        Returns:
            List of extracted leads
        """
        self.stats.start_time = datetime.now()
        leads = []
        semaphore = asyncio.Semaphore(concurrency)

        async def extract_with_semaphore(url: str) -> Optional[Lead]:
            async with semaphore:
                self.stats.total_urls_processed += 1
                return await self.extract_lead(url, industry, region)

        tasks = [extract_with_semaphore(url) for url in urls]

        for future in tqdm(
            asyncio.as_completed(tasks),
            total=len(urls),
            desc=f"Extracting {industry} leads"
        ):
            lead = await future
            if lead:
                leads.append(lead)

        self.stats.end_time = datetime.now()
        return leads

    async def run_industry_campaign(
        self,
        industry: str,
        region: str,
        max_leads: int = 50,
        save_results: bool = True
    ) -> Dict:
        """
        Run complete lead generation campaign for an industry

        Args:
            industry: Industry type
            region: Geographic region
            max_leads: Maximum leads to extract
            save_results: Save results to files

        Returns:
            Campaign results dictionary
        """
        logger.info(f"Starting lead campaign: {industry} in {region}")
        self.stats = PipelineStats()
        self.stats.start_time = datetime.now()

        # Step 1: Discover URLs
        logger.info("Step 1: Discovering business URLs...")
        urls = await self.discover_urls(industry, region, max_urls=max_leads * 2)
        logger.info(f"Found {len(urls)} potential URLs")

        if not urls:
            return {
                'success': False,
                'error': 'No URLs found',
                'industry': industry,
                'region': region
            }

        # Step 2: Extract leads
        logger.info("Step 2: Extracting lead data with Spark 1 Pro...")
        leads = await self.extract_leads_batch(
            urls=urls[:max_leads],
            industry=industry,
            region=region
        )

        self.stats.end_time = datetime.now()

        # Step 3: Save results
        if save_results and leads:
            await self._save_campaign_results(leads, industry, region)

        # Compile results
        results = {
            'success': True,
            'industry': industry,
            'region': region,
            'total_leads': len(leads),
            'urls_processed': self.stats.total_urls_processed,
            'successful_extractions': self.stats.successful_extractions,
            'failed_extractions': self.stats.failed_extractions,
            'success_rate': f"{self.stats.get_success_rate():.1f}%",
            'total_credits_used': self.stats.total_credits_used,
            'duration_seconds': self.stats.get_duration(),
            'leads': [lead.to_dict() for lead in leads]
        }

        # Summary
        logger.info(f"\nCampaign Complete!")
        logger.info(f"  Leads extracted: {len(leads)}")
        logger.info(f"  Credits used: {self.stats.total_credits_used}")
        logger.info(f"  Duration: {self.stats.get_duration():.1f}s")

        return results

    async def _save_campaign_results(
        self,
        leads: List[Lead],
        industry: str,
        region: str
    ):
        """Save campaign results to files"""
        # Create industry directory
        industry_dir = self.output_dir / industry
        industry_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        region_slug = region.lower().replace(' ', '_').replace(',', '')

        # Save JSON
        json_path = industry_dir / f"leads_{region_slug}_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'industry': industry,
                'region': region,
                'timestamp': timestamp,
                'total_leads': len(leads),
                'leads': [lead.to_dict() for lead in leads]
            }, f, indent=2, default=str)

        logger.info(f"Saved JSON: {json_path}")

        # Save CSV for easy viewing
        csv_path = industry_dir / f"leads_{region_slug}_{timestamp}.csv"
        if leads:
            # Flatten for CSV
            fieldnames = [
                'name', 'phone', 'email', 'website', 'address', 'city', 'state',
                'has_virtual_tour', 'google_rating', 'owner_name', 'lead_score',
                'source_url', 'services', 'pain_points', 'marketing_gaps'
            ]

            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                for lead in leads:
                    row = lead.to_dict()
                    # Flatten lists for CSV
                    row['services'] = '; '.join(row.get('services', []))
                    row['pain_points'] = '; '.join(row.get('pain_points', []))
                    row['marketing_gaps'] = '; '.join(row.get('marketing_gaps', []))
                    writer.writerow(row)

            logger.info(f"Saved CSV: {csv_path}")

    async def run_multi_industry_campaign(
        self,
        industries: List[str],
        region: str,
        leads_per_industry: int = 25
    ) -> Dict:
        """
        Run campaigns for multiple industries

        Args:
            industries: List of industries
            region: Geographic region
            leads_per_industry: Leads to extract per industry

        Returns:
            Combined results
        """
        all_results = []
        total_credits = 0

        for industry in industries:
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting: {industry}")
            logger.info(f"{'='*60}")

            results = await self.run_industry_campaign(
                industry=industry,
                region=region,
                max_leads=leads_per_industry
            )

            all_results.append(results)
            total_credits += results.get('total_credits_used', 0)

        return {
            'success': True,
            'region': region,
            'industries': industries,
            'total_credits_used': total_credits,
            'campaigns': all_results
        }

    def get_stats(self) -> Dict:
        """Get pipeline statistics"""
        return {
            'total_urls_processed': self.stats.total_urls_processed,
            'successful_extractions': self.stats.successful_extractions,
            'failed_extractions': self.stats.failed_extractions,
            'success_rate': f"{self.stats.get_success_rate():.1f}%",
            'total_credits_used': self.stats.total_credits_used,
            'duration_seconds': self.stats.get_duration()
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def extract_leads_for_industry(
    industry: str,
    region: str,
    max_leads: int = 50
) -> Dict:
    """
    Quick function to extract leads for an industry

    Args:
        industry: Industry type
        region: Geographic region
        max_leads: Maximum leads to extract

    Returns:
        Campaign results
    """
    pipeline = LeadPipeline()
    return await pipeline.run_industry_campaign(industry, region, max_leads)


async def burn_credits_campaign(region: str = "Lehigh Valley PA") -> Dict:
    """
    Run aggressive lead generation to use available credits.

    Target: Extract 1,300+ leads across multiple industries.
    Expected credit usage: ~72,500 credits

    Args:
        region: Primary geographic region

    Returns:
        Combined campaign results
    """
    pipeline = LeadPipeline()

    industries = [
        ('wineries', 50),
        ('auto_dealerships', 100),
        ('senior_living', 75),
        ('wedding_venues', 150),
        ('fitness_centers', 75),
        ('medical_dental', 200),
        ('real_estate', 100),
        ('restaurants', 100)
    ]

    all_results = []
    total_credits = 0
    total_leads = 0

    for industry, target_count in industries:
        logger.info(f"\n{'='*60}")
        logger.info(f"Campaign: {industry} (target: {target_count} leads)")
        logger.info(f"{'='*60}")

        results = await pipeline.run_industry_campaign(
            industry=industry,
            region=region,
            max_leads=target_count
        )

        all_results.append(results)
        total_credits += results.get('total_credits_used', 0)
        total_leads += results.get('total_leads', 0)

        logger.info(f"Running total: {total_leads} leads, {total_credits} credits")

    return {
        'success': True,
        'region': region,
        'total_leads': total_leads,
        'total_credits_used': total_credits,
        'credits_remaining': Config.CREDITS_AVAILABLE - total_credits,
        'campaigns': all_results
    }


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Lead Generation Pipeline')
    parser.add_argument('industry', help='Industry to target')
    parser.add_argument('--region', default='Lehigh Valley PA', help='Geographic region')
    parser.add_argument('--max-leads', type=int, default=50, help='Max leads to extract')
    parser.add_argument('--burn-credits', action='store_true', help='Run aggressive campaign')

    args = parser.parse_args()

    if args.burn_credits:
        results = asyncio.run(burn_credits_campaign(args.region))
    else:
        results = asyncio.run(extract_leads_for_industry(
            args.industry,
            args.region,
            args.max_leads
        ))

    print(json.dumps(results, indent=2, default=str))
