"""
SEO Orchestrator - High-level SEO operations

Combines Firecrawl and DataForSEO for comprehensive SEO analysis.

Features:
- Full SEO audit for any domain
- Competitor analysis and comparison
- Keyword research and gap analysis
- Content optimization recommendations
- Automated report generation

Usage:
    from firecrawl_scraper.orchestrators import SEOOrchestrator

    seo = SEOOrchestrator()
    report = await seo.full_seo_audit('example.com')
    print(report.generate_summary())
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..config import Config
from ..core.firecrawl_client import EnhancedFirecrawlClient
from ..core.dataforseo_client import DataForSEOClient
from ..extraction.seo_enrichment import SEOEnrichmentStrategy
from ..models.seo_models import (
    SEOReport, SEOScore, ContentAnalysis, BacklinksSummary,
    CompetitorAnalysis, CompetitorData, KeywordData, KeywordIdea,
    SEORecommendation, IssueSeverity, IssueCategory
)

logger = logging.getLogger(__name__)


class SEOOrchestrator:
    """
    High-level orchestrator for comprehensive SEO operations.

    Combines:
    - Firecrawl batch scraping for content analysis
    - DataForSEO for SERP, keywords, backlinks, on-page analysis
    - Intelligent report generation

    Example:
        seo = SEOOrchestrator()

        # Full audit
        report = await seo.full_seo_audit('example.com')

        # Competitor analysis
        competitors = await seo.competitor_analysis(
            'mysite.com',
            ['competitor1.com', 'competitor2.com']
        )

        # Keyword research
        keywords = await seo.keyword_research(['seo tools', 'keyword research'])
    """

    def __init__(
        self,
        firecrawl_key: Optional[str] = None,
        dataforseo_login: Optional[str] = None,
        dataforseo_password: Optional[str] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize SEO Orchestrator.

        Args:
            firecrawl_key: Firecrawl API key (uses Config if not provided)
            dataforseo_login: DataForSEO login (uses Config if not provided)
            dataforseo_password: DataForSEO password (uses Config if not provided)
            output_dir: Directory for reports (uses Config if not provided)
        """
        self.firecrawl_key = firecrawl_key or Config.API_KEY
        self.dataforseo_login = dataforseo_login or Config.DATAFORSEO_LOGIN
        self.dataforseo_password = dataforseo_password or Config.DATAFORSEO_PASSWORD
        self.output_dir = output_dir or Config.SEO_OUTPUT_DIR

        # Initialize clients
        self.firecrawl = EnhancedFirecrawlClient(self.firecrawl_key)
        self.dataforseo = DataForSEOClient(
            login=self.dataforseo_login,
            password=self.dataforseo_password
        ) if self.dataforseo_login else None

        # Initialize strategy
        self.seo_strategy = SEOEnrichmentStrategy(
            firecrawl_client=self.firecrawl,
            dataforseo_client=self.dataforseo
        )

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def full_seo_audit(
        self,
        domain: str,
        keywords: List[str] = None,
        max_pages: int = 50,
        include_modules: List[str] = None,
        save_report: bool = True
    ) -> SEOReport:
        """
        Run a comprehensive SEO audit for a domain.

        Args:
            domain: Target domain (e.g., 'example.com')
            keywords: Keywords to track SERP rankings
            max_pages: Maximum pages to crawl
            include_modules: Modules to include (default: all available)
            save_report: Save report to file

        Returns:
            SEOReport with comprehensive analysis
        """
        logger.info(f"Starting full SEO audit for {domain}")

        # Default to all modules if not specified
        if include_modules is None:
            include_modules = ['content', 'backlinks', 'onpage']
            if keywords:
                include_modules.extend(['serp', 'keywords'])

        # Build source config
        source = {
            'url': f'https://{domain}',
            'strategy': 'seo',
            'base_strategy': 'map',
            'max_pages': max_pages,
            'seo_modules': include_modules,
            'keywords': keywords or [],
            'onpage_max_pages': min(max_pages, 100)
        }

        # Execute SEO strategy
        results = await self.seo_strategy.execute(source)

        # Get the report
        report = results.get('seo_report')

        # Save report if requested
        if save_report and report:
            await self._save_report(report, domain, 'audit')

        logger.info(
            f"SEO audit complete for {domain}. "
            f"Score: {report.seo_score.overall}/100, "
            f"Cost: ${report.total_cost:.4f}"
        )

        return report

    async def competitor_analysis(
        self,
        domain: str,
        competitors: List[str] = None,
        find_competitors: bool = True,
        max_competitors: int = 5,
        save_report: bool = True
    ) -> CompetitorAnalysis:
        """
        Analyze a domain against its competitors.

        Args:
            domain: Target domain
            competitors: List of competitor domains (auto-discovered if not provided)
            find_competitors: Auto-discover competitors if not provided
            max_competitors: Maximum competitors to analyze
            save_report: Save report to file

        Returns:
            CompetitorAnalysis with comparison data
        """
        logger.info(f"Starting competitor analysis for {domain}")

        if not self.dataforseo:
            raise ValueError("DataForSEO credentials required for competitor analysis")

        competitors_data = []
        keyword_gaps = []
        total_cost = 0

        # Find competitors if not provided
        if not competitors and find_competitors:
            logger.info("Auto-discovering competitors...")
            result = await self.dataforseo.labs_competitors_domain(
                target=domain,
                location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
                limit=max_competitors
            )

            if result.get('success'):
                items = result.get('data', {}).get('items', [])
                competitors = [item.get('domain') for item in items if item.get('domain') != domain]
                total_cost += result.get('cost', 0)

                # Convert to CompetitorData
                for item in items[:max_competitors]:
                    competitors_data.append(CompetitorData(
                        domain=item.get('domain', ''),
                        rank=item.get('rank'),
                        organic_traffic=item.get('organic_traffic'),
                        organic_keywords=item.get('organic_keywords'),
                        common_keywords=item.get('common_keywords', 0)
                    ))

        # Get detailed data for each competitor
        for comp_domain in competitors[:max_competitors]:
            logger.info(f"Analyzing competitor: {comp_domain}")

            # Get backlinks summary
            backlinks_result = await self.dataforseo.backlinks_summary(target=comp_domain)
            if backlinks_result.get('success'):
                data = backlinks_result.get('data', {})
                total_cost += backlinks_result.get('cost', 0)

                # Update competitor data
                for cd in competitors_data:
                    if cd.domain == comp_domain:
                        cd.backlinks = data.get('backlinks')
                        cd.referring_domains = data.get('referring_domains')
                        cd.rank = data.get('rank')
                        break

            await asyncio.sleep(Config.SEO_REQUEST_DELAY)

        # Get keyword intersection
        if competitors:
            targets = [domain] + competitors[:3]
            intersection_result = await self.dataforseo.labs_domain_intersection(
                targets=targets,
                location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
                limit=100
            )

            if intersection_result.get('success'):
                items = intersection_result.get('data', {}).get('items', [])
                total_cost += intersection_result.get('cost', 0)

                # Find keywords competitors rank for but target doesn't
                for item in items:
                    target_position = item.get(domain, {}).get('position')
                    competitor_positions = [
                        item.get(c, {}).get('position')
                        for c in competitors
                        if item.get(c, {}).get('position')
                    ]

                    if not target_position and competitor_positions:
                        keyword_gaps.append(KeywordData(
                            keyword=item.get('keyword', ''),
                            metrics=None,
                            location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                            language_code=Config.SEO_DEFAULT_LANGUAGE_CODE
                        ))

        analysis = CompetitorAnalysis(
            target=domain,
            competitors=competitors_data,
            keyword_gaps=keyword_gaps[:50] if keyword_gaps else None
        )

        # Save report
        if save_report:
            await self._save_competitor_report(analysis, domain, total_cost)

        logger.info(
            f"Competitor analysis complete. "
            f"Found {len(competitors_data)} competitors, "
            f"{len(keyword_gaps)} keyword gaps"
        )

        return analysis

    async def keyword_research(
        self,
        seed_keywords: List[str],
        domain: Optional[str] = None,
        max_ideas_per_seed: int = 50,
        save_report: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive keyword research.

        Args:
            seed_keywords: Seed keywords to expand
            domain: Optional domain to check rankings for
            max_ideas_per_seed: Max keyword ideas per seed
            save_report: Save report to file

        Returns:
            Dict with keyword research results
        """
        logger.info(f"Starting keyword research with seeds: {seed_keywords}")

        if not self.dataforseo:
            raise ValueError("DataForSEO credentials required for keyword research")

        results = {
            'seed_keywords': seed_keywords,
            'keyword_ideas': [],
            'keyword_metrics': [],
            'domain_keywords': [],
            'total_keywords': 0,
            'cost': 0
        }

        # Get keyword ideas for each seed
        all_ideas = []
        for seed in seed_keywords:
            logger.info(f"Researching: {seed}")

            ideas_result = await self.dataforseo.labs_keyword_ideas(
                keyword=seed,
                location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
                limit=max_ideas_per_seed
            )

            if ideas_result.get('success'):
                items = ideas_result.get('data', {}).get('items', [])
                results['cost'] += ideas_result.get('cost', 0)

                for item in items:
                    all_ideas.append(KeywordIdea(
                        keyword=item.get('keyword', ''),
                        search_volume=item.get('search_volume', 0),
                        cpc=item.get('cpc'),
                        competition=item.get('competition'),
                        keyword_difficulty=item.get('keyword_difficulty')
                    ))

            await asyncio.sleep(Config.SEO_REQUEST_DELAY)

        # Deduplicate and sort by search volume
        seen = set()
        unique_ideas = []
        for idea in sorted(all_ideas, key=lambda x: x.search_volume, reverse=True):
            if idea.keyword not in seen:
                seen.add(idea.keyword)
                unique_ideas.append(idea)

        results['keyword_ideas'] = unique_ideas

        # Get metrics for top keywords
        top_keywords = [idea.keyword for idea in unique_ideas[:20]]
        if top_keywords:
            metrics_result = await self.dataforseo.keywords_google_ads(
                keywords=top_keywords,
                location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                language_code=Config.SEO_DEFAULT_LANGUAGE_CODE
            )

            if metrics_result.get('success'):
                results['keyword_metrics'] = metrics_result.get('data', {}).get('items', [])
                results['cost'] += metrics_result.get('cost', 0)

        # Get domain's existing keywords if provided
        if domain:
            domain_result = await self.dataforseo.keywords_for_site(
                target=domain,
                location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
                include_serp_info=True
            )

            if domain_result.get('success'):
                results['domain_keywords'] = domain_result.get('data', {}).get('items', [])
                results['cost'] += domain_result.get('cost', 0)

        results['total_keywords'] = len(results['keyword_ideas'])

        # Save report
        if save_report:
            await self._save_keyword_report(results, seed_keywords)

        logger.info(
            f"Keyword research complete. "
            f"Found {results['total_keywords']} keyword ideas, "
            f"Cost: ${results['cost']:.4f}"
        )

        return results

    async def content_gap_analysis(
        self,
        domain: str,
        competitors: List[str],
        save_report: bool = True
    ) -> Dict[str, Any]:
        """
        Find content gaps - keywords competitors rank for but you don't.

        Args:
            domain: Your domain
            competitors: Competitor domains
            save_report: Save report to file

        Returns:
            Dict with content gap analysis
        """
        logger.info(f"Starting content gap analysis for {domain}")

        if not self.dataforseo:
            raise ValueError("DataForSEO credentials required for content gap analysis")

        results = {
            'domain': domain,
            'competitors': competitors,
            'content_gaps': [],
            'quick_wins': [],  # Keywords where you rank but could rank higher
            'opportunities': [],  # High volume, low competition
            'cost': 0
        }

        # Get domain intersection
        targets = [domain] + competitors[:3]
        intersection_result = await self.dataforseo.labs_domain_intersection(
            targets=targets,
            location_code=Config.SEO_DEFAULT_LOCATION_CODE,
            language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
            limit=500
        )

        if intersection_result.get('success'):
            items = intersection_result.get('data', {}).get('items', [])
            results['cost'] += intersection_result.get('cost', 0)

            for item in items:
                keyword = item.get('keyword', '')
                search_volume = item.get('search_volume', 0)

                # Our position
                our_data = item.get(domain, {})
                our_position = our_data.get('position')

                # Best competitor position
                best_comp_position = None
                for comp in competitors:
                    comp_data = item.get(comp, {})
                    comp_pos = comp_data.get('position')
                    if comp_pos:
                        if best_comp_position is None or comp_pos < best_comp_position:
                            best_comp_position = comp_pos

                # Categorize
                gap_item = {
                    'keyword': keyword,
                    'search_volume': search_volume,
                    'our_position': our_position,
                    'competitor_position': best_comp_position,
                    'gap': (our_position - best_comp_position) if our_position and best_comp_position else None
                }

                if not our_position and best_comp_position:
                    # We don't rank, competitor does = content gap
                    results['content_gaps'].append(gap_item)
                elif our_position and best_comp_position and our_position > best_comp_position:
                    if our_position <= 20:
                        # We rank but competitor ranks higher = quick win
                        results['quick_wins'].append(gap_item)
                    else:
                        # Opportunity to improve
                        results['opportunities'].append(gap_item)

        # Sort by search volume
        results['content_gaps'] = sorted(
            results['content_gaps'],
            key=lambda x: x.get('search_volume', 0),
            reverse=True
        )[:100]

        results['quick_wins'] = sorted(
            results['quick_wins'],
            key=lambda x: x.get('search_volume', 0),
            reverse=True
        )[:50]

        # Save report
        if save_report:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"content_gap_{domain.replace('.', '_')}_{timestamp}.json"
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"Content gap report saved to {filepath}")

        logger.info(
            f"Content gap analysis complete. "
            f"Found {len(results['content_gaps'])} gaps, "
            f"{len(results['quick_wins'])} quick wins"
        )

        return results

    async def quick_audit(
        self,
        domain: str,
        save_report: bool = False
    ) -> Dict[str, Any]:
        """
        Run a quick SEO audit (backlinks + on-page summary only).

        Args:
            domain: Target domain
            save_report: Save report to file

        Returns:
            Dict with quick audit results
        """
        logger.info(f"Running quick audit for {domain}")

        results = {
            'domain': domain,
            'backlinks': None,
            'domain_rank': None,
            'referring_domains': None,
            'organic_keywords': None,
            'cost': 0
        }

        if self.dataforseo:
            # Get backlinks summary
            backlinks_result = await self.dataforseo.backlinks_summary(target=domain)
            if backlinks_result.get('success'):
                data = backlinks_result.get('data', {})
                results['backlinks'] = data.get('backlinks')
                results['domain_rank'] = data.get('rank')
                results['referring_domains'] = data.get('referring_domains')
                results['cost'] += backlinks_result.get('cost', 0)

            await asyncio.sleep(Config.SEO_REQUEST_DELAY)

            # Get ranked keywords count
            ranked_result = await self.dataforseo.labs_ranked_keywords(
                target=domain,
                location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
                limit=1
            )
            if ranked_result.get('success'):
                results['organic_keywords'] = ranked_result.get('data', {}).get('total_count', 0)
                results['cost'] += ranked_result.get('cost', 0)

        logger.info(
            f"Quick audit complete for {domain}. "
            f"Rank: {results['domain_rank']}, "
            f"Backlinks: {results['backlinks']}, "
            f"Cost: ${results['cost']:.4f}"
        )

        return results

    async def batch_quick_audit(
        self,
        domains: List[str],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Run quick audits on multiple domains.

        Args:
            domains: List of domains to audit
            max_concurrent: Maximum concurrent requests

        Returns:
            List of quick audit results
        """
        logger.info(f"Starting batch quick audit for {len(domains)} domains")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def audit_with_semaphore(domain):
            async with semaphore:
                return await self.quick_audit(domain, save_report=False)

        tasks = [audit_with_semaphore(domain) for domain in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]

        total_cost = sum(r.get('cost', 0) for r in valid_results)
        logger.info(
            f"Batch quick audit complete. "
            f"{len(valid_results)}/{len(domains)} successful, "
            f"Total cost: ${total_cost:.4f}"
        )

        return valid_results

    async def _save_report(
        self,
        report: SEOReport,
        domain: str,
        report_type: str
    ):
        """Save SEO report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"seo_{report_type}_{domain.replace('.', '_')}_{timestamp}"

        # Save JSON
        json_path = self.output_dir / f"{base_filename}.json"
        with open(json_path, 'w') as f:
            json.dump(report.model_dump(), f, indent=2, default=str)

        # Save Markdown
        md_path = self.output_dir / f"{base_filename}.md"
        with open(md_path, 'w') as f:
            f.write(report.to_markdown())

        logger.info(f"Reports saved: {json_path}, {md_path}")

    async def _save_competitor_report(
        self,
        analysis: CompetitorAnalysis,
        domain: str,
        cost: float
    ):
        """Save competitor analysis report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"competitor_analysis_{domain.replace('.', '_')}_{timestamp}.json"
        filepath = self.output_dir / filename

        data = {
            'target': analysis.target,
            'analyzed_at': analysis.analyzed_at.isoformat(),
            'competitors': [c.model_dump() for c in analysis.competitors],
            'keyword_gaps_count': len(analysis.keyword_gaps) if analysis.keyword_gaps else 0,
            'keyword_gaps': [k.model_dump() for k in (analysis.keyword_gaps or [])[:50]],
            'cost': cost
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Competitor analysis saved to {filepath}")

    async def _save_keyword_report(
        self,
        results: Dict[str, Any],
        seed_keywords: List[str]
    ):
        """Save keyword research report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        seed_slug = '_'.join(seed_keywords[:3]).replace(' ', '-')[:50]
        filename = f"keyword_research_{seed_slug}_{timestamp}.json"
        filepath = self.output_dir / filename

        # Convert KeywordIdea objects to dicts
        data = {
            'seed_keywords': results['seed_keywords'],
            'total_keywords': results['total_keywords'],
            'keyword_ideas': [
                k.model_dump() if hasattr(k, 'model_dump') else k
                for k in results['keyword_ideas'][:100]
            ],
            'keyword_metrics': results['keyword_metrics'],
            'domain_keywords': results.get('domain_keywords', [])[:50],
            'cost': results['cost']
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Keyword research saved to {filepath}")

    def get_api_status(self) -> Dict[str, Any]:
        """Check API status and credentials"""
        return {
            'firecrawl': {
                'configured': bool(self.firecrawl_key),
                'key_preview': f"...{self.firecrawl_key[-8:]}" if self.firecrawl_key else None
            },
            'dataforseo': {
                'configured': bool(self.dataforseo_login and self.dataforseo_password),
                'login': self.dataforseo_login,
                'enabled': Config.DATAFORSEO_ENABLED,
                'modules': {
                    'serp': Config.SEO_SERP_ENABLED,
                    'keywords': Config.SEO_KEYWORDS_ENABLED,
                    'backlinks': Config.SEO_BACKLINKS_ENABLED,
                    'onpage': Config.SEO_ONPAGE_ENABLED,
                    'labs': Config.SEO_LABS_ENABLED
                }
            },
            'output_dir': str(self.output_dir)
        }
