"""
SEO Enrichment Strategy - Combines Firecrawl + DataForSEO

A scraping strategy that:
1. Scrapes content with Firecrawl (batch, crawl, or map)
2. Enriches with SEO data from DataForSEO
3. Returns comprehensive SEO-enriched results

Usage:
    result = await scraper.scrape_source({
        'url': 'https://example.com',
        'strategy': 'seo',
        'seo_modules': ['keywords', 'backlinks', 'onpage'],
        'max_pages': 50
    })
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

from ..config import Config
from ..core.firecrawl_client import EnhancedFirecrawlClient
from ..core.dataforseo_client import DataForSEOClient
from ..models.seo_models import (
    SEOReport, SEOScore, ContentAnalysis, TechnicalSEO,
    BacklinksSummary, SERPRankingData, OnPageResult, OnPageSummary, OnPageIssue,
    SEORecommendation, IssueSeverity, IssueCategory, KeywordData
)

logger = logging.getLogger(__name__)


class SEOEnrichmentStrategy:
    """
    Strategy that combines Firecrawl content scraping with DataForSEO SEO data.

    Modules available:
    - content: Scrape and analyze content with Firecrawl
    - serp: Get SERP rankings for keywords
    - keywords: Get keyword metrics and ideas
    - backlinks: Get backlink analysis
    - onpage: Run technical SEO audit
    - competitors: Analyze competitors
    """

    name = "seo"
    description = "SEO-enriched scraping combining Firecrawl content with DataForSEO metrics"

    def __init__(
        self,
        firecrawl_client: Optional[EnhancedFirecrawlClient] = None,
        dataforseo_client: Optional[DataForSEOClient] = None
    ):
        """
        Initialize SEO enrichment strategy.

        Args:
            firecrawl_client: Firecrawl client instance
            dataforseo_client: DataForSEO client instance
        """
        self.firecrawl = firecrawl_client or EnhancedFirecrawlClient(Config.API_KEY)
        self.dataforseo = dataforseo_client or DataForSEOClient(
            login=Config.DATAFORSEO_LOGIN,
            password=Config.DATAFORSEO_PASSWORD
        ) if Config.DATAFORSEO_LOGIN else None

        self.config = Config

    async def execute(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SEO-enriched scraping.

        Args:
            source: Source configuration dict with:
                - url: Target URL or domain
                - strategy: Base scraping strategy (crawl, map, batch)
                - seo_modules: List of SEO modules to run
                - max_pages: Maximum pages to scrape
                - keywords: Keywords to track (for SERP module)
                - competitors: Competitor domains (for competitor module)

        Returns:
            Dict containing scraped content and SEO data
        """
        start_time = time.time()
        url = source.get('url', '')
        domain = self._extract_domain(url)

        # Determine which modules to run
        seo_modules = source.get('seo_modules', ['content', 'backlinks'])
        if isinstance(seo_modules, str):
            seo_modules = [seo_modules]

        logger.info(f"Starting SEO enrichment for {domain} with modules: {seo_modules}")

        # Results container
        results = {
            'domain': domain,
            'url': url,
            'strategy': 'seo',
            'modules_executed': [],
            'content': None,
            'serp_data': None,
            'keywords_data': None,
            'backlinks_data': None,
            'onpage_data': None,
            'competitors_data': None,
            'seo_report': None,
            'costs': {
                'firecrawl': 0.0,
                'dataforseo': 0.0,
                'total': 0.0
            }
        }

        # Run modules concurrently where possible
        tasks = []

        # Content scraping (always runs if in modules or no modules specified)
        if 'content' in seo_modules or not seo_modules:
            tasks.append(('content', self._scrape_content(source)))

        # DataForSEO modules (run if client available and enabled)
        if self.dataforseo and Config.DATAFORSEO_ENABLED:
            if 'serp' in seo_modules and Config.SEO_SERP_ENABLED:
                keywords = source.get('keywords', [])
                if keywords:
                    tasks.append(('serp', self._get_serp_data(keywords, domain)))

            if 'keywords' in seo_modules and Config.SEO_KEYWORDS_ENABLED:
                tasks.append(('keywords', self._get_keyword_data(domain, source.get('keywords', []))))

            if 'backlinks' in seo_modules and Config.SEO_BACKLINKS_ENABLED:
                tasks.append(('backlinks', self._get_backlinks_data(domain)))

            if 'onpage' in seo_modules and Config.SEO_ONPAGE_ENABLED:
                max_pages = source.get('onpage_max_pages', 100)
                tasks.append(('onpage', self._get_onpage_data(domain, max_pages)))

            if 'competitors' in seo_modules and Config.SEO_LABS_ENABLED:
                competitors = source.get('competitors', [])
                tasks.append(('competitors', self._get_competitor_data(domain, competitors)))

        # Execute all tasks concurrently
        if tasks:
            task_results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )

            # Process results
            for (module_name, _), result in zip(tasks, task_results):
                if isinstance(result, Exception):
                    logger.error(f"Module {module_name} failed: {result}")
                    continue

                results['modules_executed'].append(module_name)

                if module_name == 'content':
                    results['content'] = result.get('data', [])
                    results['costs']['firecrawl'] = result.get('credits_used', 0)
                elif module_name == 'serp':
                    results['serp_data'] = result
                    results['costs']['dataforseo'] += result.get('cost', 0) if isinstance(result, dict) else 0
                elif module_name == 'keywords':
                    results['keywords_data'] = result
                    results['costs']['dataforseo'] += result.get('cost', 0) if isinstance(result, dict) else 0
                elif module_name == 'backlinks':
                    results['backlinks_data'] = result
                    results['costs']['dataforseo'] += result.get('cost', 0) if isinstance(result, dict) else 0
                elif module_name == 'onpage':
                    results['onpage_data'] = result
                    results['costs']['dataforseo'] += result.get('cost', 0) if isinstance(result, dict) else 0
                elif module_name == 'competitors':
                    results['competitors_data'] = result
                    results['costs']['dataforseo'] += result.get('cost', 0) if isinstance(result, dict) else 0

        # Calculate total cost
        results['costs']['total'] = results['costs']['firecrawl'] + results['costs']['dataforseo']

        # Generate comprehensive SEO report
        processing_time = time.time() - start_time
        results['seo_report'] = self._generate_seo_report(results, processing_time)
        results['processing_time'] = processing_time

        logger.info(f"SEO enrichment completed in {processing_time:.1f}s. Cost: ${results['costs']['total']:.4f}")

        return results

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url.startswith('http'):
            url = f'https://{url}'
        parsed = urlparse(url)
        return parsed.netloc or url

    async def _scrape_content(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape content using Firecrawl"""
        url = source.get('url')
        base_strategy = source.get('base_strategy', 'map')
        max_pages = source.get('max_pages', 50)

        logger.info(f"Scraping content from {url} using {base_strategy} strategy")

        try:
            if base_strategy == 'crawl':
                result = await self.firecrawl.crawl(
                    url=url,
                    limit=max_pages,
                    scrape_options={'formats': ['markdown', 'html']}
                )
            elif base_strategy == 'map':
                result = await self.firecrawl.map(url=url, limit=max_pages)
            elif base_strategy == 'batch':
                urls = source.get('urls', [url])
                result = await self.firecrawl.batch_scrape(urls=urls)
            else:
                result = await self.firecrawl.scrape(url=url)

            return {
                'data': result.get('data', []),
                'credits_used': result.get('creditsUsed', 0)
            }
        except Exception as e:
            logger.error(f"Content scraping failed: {e}")
            return {'data': [], 'credits_used': 0, 'error': str(e)}

    async def _get_serp_data(
        self,
        keywords: List[str],
        target_domain: str
    ) -> Dict[str, Any]:
        """Get SERP rankings for keywords"""
        if not keywords:
            return {'rankings': {}, 'cost': 0}

        logger.info(f"Getting SERP data for {len(keywords)} keywords")

        rankings = {}
        total_cost = 0

        for keyword in keywords[:20]:  # Limit to 20 keywords
            try:
                result = await self.dataforseo.serp_google_organic(
                    keyword=keyword,
                    location_name=Config.SEO_DEFAULT_LOCATION,
                    language_code=Config.SEO_DEFAULT_LANGUAGE,
                    device=Config.SEO_DEFAULT_DEVICE,
                    depth=100
                )

                if result.get('success'):
                    data = result.get('data', {})
                    items = data.get('items', [])

                    # Find target domain position
                    our_position = None
                    for item in items:
                        if target_domain in item.get('url', ''):
                            our_position = item.get('rank_absolute')
                            break

                    rankings[keyword] = {
                        'keyword': keyword,
                        'our_position': our_position,
                        'results_count': len(items),
                        'top_results': items[:10],
                        'cost': result.get('cost', 0)
                    }
                    total_cost += result.get('cost', 0)

                # Rate limiting
                await asyncio.sleep(Config.SEO_REQUEST_DELAY)

            except Exception as e:
                logger.error(f"SERP query failed for '{keyword}': {e}")

        return {
            'rankings': rankings,
            'keywords_tracked': len(rankings),
            'cost': total_cost
        }

    async def _get_keyword_data(
        self,
        domain: str,
        seed_keywords: List[str] = None
    ) -> Dict[str, Any]:
        """Get keyword data for domain"""
        logger.info(f"Getting keyword data for {domain}")

        result = {
            'domain_keywords': [],
            'keyword_ideas': [],
            'cost': 0
        }

        try:
            # Get keywords the domain ranks for
            domain_result = await self.dataforseo.keywords_for_site(
                target=domain,
                location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
                include_serp_info=True
            )

            if domain_result.get('success'):
                result['domain_keywords'] = domain_result.get('data', {}).get('items', [])
                result['cost'] += domain_result.get('cost', 0)

            # Get keyword ideas if seed keywords provided
            if seed_keywords:
                for keyword in seed_keywords[:5]:
                    ideas_result = await self.dataforseo.labs_keyword_ideas(
                        keyword=keyword,
                        location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                        language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
                        limit=20
                    )

                    if ideas_result.get('success'):
                        result['keyword_ideas'].extend(
                            ideas_result.get('data', {}).get('items', [])
                        )
                        result['cost'] += ideas_result.get('cost', 0)

                    await asyncio.sleep(Config.SEO_REQUEST_DELAY)

        except Exception as e:
            logger.error(f"Keyword data retrieval failed: {e}")
            result['error'] = str(e)

        return result

    async def _get_backlinks_data(self, domain: str) -> Dict[str, Any]:
        """Get backlinks data for domain"""
        logger.info(f"Getting backlinks data for {domain}")

        result = {
            'summary': None,
            'top_backlinks': [],
            'referring_domains': [],
            'cost': 0
        }

        try:
            # Get backlinks summary
            summary_result = await self.dataforseo.backlinks_summary(target=domain)
            if summary_result.get('success'):
                result['summary'] = summary_result.get('data', {})
                result['cost'] += summary_result.get('cost', 0)

            await asyncio.sleep(Config.SEO_REQUEST_DELAY)

            # Get top backlinks
            backlinks_result = await self.dataforseo.backlinks_backlinks(
                target=domain,
                limit=100,
                order_by=['rank:desc']
            )
            if backlinks_result.get('success'):
                result['top_backlinks'] = backlinks_result.get('data', {}).get('items', [])
                result['cost'] += backlinks_result.get('cost', 0)

            await asyncio.sleep(Config.SEO_REQUEST_DELAY)

            # Get referring domains
            domains_result = await self.dataforseo.backlinks_referring_domains(
                target=domain,
                limit=50
            )
            if domains_result.get('success'):
                result['referring_domains'] = domains_result.get('data', {}).get('items', [])
                result['cost'] += domains_result.get('cost', 0)

        except Exception as e:
            logger.error(f"Backlinks data retrieval failed: {e}")
            result['error'] = str(e)

        return result

    async def _get_onpage_data(
        self,
        domain: str,
        max_pages: int = 100
    ) -> Dict[str, Any]:
        """Run on-page SEO audit"""
        logger.info(f"Running on-page audit for {domain} (max {max_pages} pages)")

        result = {
            'task_id': None,
            'summary': None,
            'pages': [],
            'issues': [],
            'cost': 0
        }

        try:
            # Create on-page task
            task_result = await self.dataforseo.onpage_task_post(
                target=domain,
                max_crawl_pages=max_pages,
                enable_javascript=True
            )

            if task_result.get('success'):
                task_id = task_result.get('data', {}).get('id')
                result['task_id'] = task_id
                result['cost'] += task_result.get('cost', 0)

                # Wait for crawl to complete (poll status)
                max_wait = 300  # 5 minutes max
                poll_interval = 10
                waited = 0

                while waited < max_wait:
                    await asyncio.sleep(poll_interval)
                    waited += poll_interval

                    summary_result = await self.dataforseo.onpage_summary(task_id)
                    if summary_result.get('success'):
                        data = summary_result.get('data', {})
                        crawl_progress = data.get('crawl_progress', 'in_progress')

                        if crawl_progress == 'finished':
                            result['summary'] = data
                            result['cost'] += summary_result.get('cost', 0)
                            break

                # Get pages data
                if result['summary']:
                    pages_result = await self.dataforseo.onpage_pages(
                        task_id=task_id,
                        limit=100
                    )
                    if pages_result.get('success'):
                        result['pages'] = pages_result.get('data', {}).get('items', [])
                        result['cost'] += pages_result.get('cost', 0)

        except Exception as e:
            logger.error(f"On-page audit failed: {e}")
            result['error'] = str(e)

        return result

    async def _get_competitor_data(
        self,
        domain: str,
        competitors: List[str] = None
    ) -> Dict[str, Any]:
        """Get competitor analysis data"""
        logger.info(f"Getting competitor data for {domain}")

        result = {
            'competitors': [],
            'domain_intersection': [],
            'cost': 0
        }

        try:
            # Find competitors if not provided
            if not competitors:
                competitors_result = await self.dataforseo.labs_competitors_domain(
                    target=domain,
                    location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                    language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
                    limit=10
                )

                if competitors_result.get('success'):
                    items = competitors_result.get('data', {}).get('items', [])
                    competitors = [item.get('domain') for item in items[:5]]
                    result['competitors'] = items
                    result['cost'] += competitors_result.get('cost', 0)

            # Get domain intersection (keyword overlap)
            if competitors:
                await asyncio.sleep(Config.SEO_REQUEST_DELAY)

                targets = [domain] + competitors[:3]
                intersection_result = await self.dataforseo.labs_domain_intersection(
                    targets=targets,
                    location_code=Config.SEO_DEFAULT_LOCATION_CODE,
                    language_code=Config.SEO_DEFAULT_LANGUAGE_CODE,
                    limit=100
                )

                if intersection_result.get('success'):
                    result['domain_intersection'] = intersection_result.get('data', {}).get('items', [])
                    result['cost'] += intersection_result.get('cost', 0)

        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            result['error'] = str(e)

        return result

    def _generate_seo_report(
        self,
        results: Dict[str, Any],
        processing_time: float
    ) -> SEOReport:
        """Generate comprehensive SEO report from collected data"""
        domain = results['domain']

        # Calculate scores
        scores = self._calculate_seo_scores(results)

        # Build content analysis
        content_analysis = None
        if results.get('content'):
            content_analysis = self._build_content_analysis(results['content'])

        # Build backlinks summary
        backlinks_summary = None
        if results.get('backlinks_data'):
            backlinks_summary = self._build_backlinks_summary(results['backlinks_data'])

        # Build technical SEO
        technical_seo = None
        if results.get('onpage_data'):
            technical_seo = self._build_technical_seo(results['onpage_data'])

        # Calculate keyword metrics
        keywords_tracked = 0
        keywords_in_top_10 = 0
        keywords_in_top_100 = 0
        avg_position = None

        if results.get('serp_data'):
            rankings = results['serp_data'].get('rankings', {})
            keywords_tracked = len(rankings)
            positions = []

            for kw_data in rankings.values():
                pos = kw_data.get('our_position')
                if pos:
                    positions.append(pos)
                    if pos <= 10:
                        keywords_in_top_10 += 1
                    if pos <= 100:
                        keywords_in_top_100 += 1

            if positions:
                avg_position = sum(positions) / len(positions)

        # Generate recommendations
        recommendations = self._generate_recommendations(results)

        return SEOReport(
            domain=domain,
            seo_score=scores,
            content_analysis=content_analysis,
            backlinks_summary=backlinks_summary,
            technical_seo=technical_seo,
            keywords_tracked=keywords_tracked,
            keywords_in_top_10=keywords_in_top_10,
            keywords_in_top_100=keywords_in_top_100,
            avg_position=avg_position,
            recommendations=recommendations,
            firecrawl_credits_used=results['costs']['firecrawl'],
            dataforseo_cost=results['costs']['dataforseo'],
            total_cost=results['costs']['total'],
            processing_time=processing_time
        )

    def _calculate_seo_scores(self, results: Dict[str, Any]) -> SEOScore:
        """Calculate SEO scores from data"""
        technical_score = 70  # Default
        content_score = 70
        authority_score = 70

        # Technical score from onpage
        if results.get('onpage_data', {}).get('summary'):
            summary = results['onpage_data']['summary']
            pages_crawled = summary.get('pages_crawled', 0)
            pages_with_errors = summary.get('pages_with_errors', 0)

            if pages_crawled > 0:
                error_rate = pages_with_errors / pages_crawled
                technical_score = max(0, int(100 - (error_rate * 100)))

        # Content score from scraped content
        if results.get('content'):
            pages = results['content']
            if pages:
                # Score based on content length, structure, etc.
                avg_length = sum(len(p.get('markdown', '')) for p in pages) / len(pages)
                if avg_length > 5000:
                    content_score = 90
                elif avg_length > 2000:
                    content_score = 80
                elif avg_length > 1000:
                    content_score = 70
                else:
                    content_score = 60

        # Authority score from backlinks
        if results.get('backlinks_data', {}).get('summary'):
            summary = results['backlinks_data']['summary']
            domain_rank = summary.get('rank') or summary.get('domain_rank', 0)

            if domain_rank:
                authority_score = min(100, int(domain_rank))
            else:
                # Estimate from referring domains
                ref_domains = summary.get('referring_domains', 0)
                if ref_domains > 1000:
                    authority_score = 85
                elif ref_domains > 100:
                    authority_score = 70
                elif ref_domains > 10:
                    authority_score = 50
                else:
                    authority_score = 30

        # Overall score is weighted average
        overall = int(
            technical_score * 0.35 +
            content_score * 0.35 +
            authority_score * 0.30
        )

        return SEOScore(
            overall=overall,
            technical=technical_score,
            content=content_score,
            authority=authority_score
        )

    def _build_content_analysis(self, content: List[Dict]) -> ContentAnalysis:
        """Build content analysis from scraped pages"""
        total_words = 0
        total_chars = 0
        pages_with_h1 = 0
        pages_with_thin_content = 0

        for page in content:
            markdown = page.get('markdown', '')
            words = len(markdown.split())
            total_words += words
            total_chars += len(markdown)

            if words < 300:
                pages_with_thin_content += 1

            html = page.get('html', '')
            if '<h1' in html.lower():
                pages_with_h1 += 1

        pages_count = len(content) or 1

        return ContentAnalysis(
            pages_scraped=len(content),
            total_words=total_words,
            avg_word_count=total_words / pages_count,
            total_chars=total_chars,
            avg_reading_time=(total_words / pages_count) / 200,  # 200 wpm
            pages_with_thin_content=pages_with_thin_content,
            pages_with_h1=pages_with_h1
        )

    def _build_backlinks_summary(self, data: Dict) -> Optional[BacklinksSummary]:
        """Build backlinks summary from data"""
        summary = data.get('summary', {})
        if not summary:
            return None

        total_backlinks = summary.get('backlinks', 0)
        dofollow = summary.get('backlinks_nofollow', 0)
        nofollow = total_backlinks - dofollow if total_backlinks else 0

        return BacklinksSummary(
            target=summary.get('target', ''),
            total_backlinks=total_backlinks,
            referring_domains=summary.get('referring_domains', 0),
            referring_main_domains=summary.get('referring_main_domains', 0),
            referring_ips=summary.get('referring_ips', 0),
            referring_subnets=summary.get('referring_subnets', 0),
            dofollow_backlinks=dofollow,
            nofollow_backlinks=nofollow,
            domain_rank=summary.get('rank'),
            new_backlinks=summary.get('new_backlinks', 0),
            lost_backlinks=summary.get('lost_backlinks', 0),
            dofollow_ratio=dofollow / total_backlinks if total_backlinks else 0,
            cost=data.get('cost', 0)
        )

    def _build_technical_seo(self, data: Dict) -> Optional[TechnicalSEO]:
        """Build technical SEO summary from onpage data"""
        summary = data.get('summary', {})
        if not summary:
            return None

        pages_crawled = summary.get('pages_crawled', 0)
        pages_with_errors = summary.get('pages_with_errors', 0)

        # Calculate score based on error rate
        error_rate = pages_with_errors / pages_crawled if pages_crawled else 0
        score = max(0, int(100 - (error_rate * 100)))

        # Build issues list
        issues = []
        checks = summary.get('checks', {})
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                count = check_data.get('count', 0)
                if count > 0:
                    issues.append(OnPageIssue(
                        issue_type=check_name,
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.TECHNICAL,
                        pages_affected=count,
                        description=f"{check_name}: {count} pages affected",
                        recommendation=f"Review and fix {check_name} issues"
                    ))

        return TechnicalSEO(
            score=score,
            has_robots_txt=summary.get('checks', {}).get('robots_txt', {}).get('is_valid', False),
            has_sitemap=summary.get('checks', {}).get('sitemap', {}).get('is_valid', False),
            indexed_pages=summary.get('pages_indexed', 0),
            has_ssl=True,  # Assume HTTPS
            critical_issues=sum(1 for i in issues if i.severity == IssueSeverity.CRITICAL),
            high_issues=sum(1 for i in issues if i.severity == IssueSeverity.HIGH),
            medium_issues=sum(1 for i in issues if i.severity == IssueSeverity.MEDIUM),
            low_issues=sum(1 for i in issues if i.severity == IssueSeverity.LOW),
            issues=issues[:20]  # Limit to top 20 issues
        )

    def _generate_recommendations(self, results: Dict) -> List[SEORecommendation]:
        """Generate SEO recommendations from analysis"""
        recommendations = []

        # Content recommendations
        if results.get('content'):
            content = results['content']
            thin_pages = sum(1 for p in content if len(p.get('markdown', '').split()) < 300)

            if thin_pages > 0:
                recommendations.append(SEORecommendation(
                    priority=IssueSeverity.HIGH,
                    category=IssueCategory.CONTENT,
                    issue=f"{thin_pages} pages have thin content (< 300 words)",
                    recommendation="Add more comprehensive content to pages with less than 300 words",
                    impact="Improved rankings and user engagement",
                    effort="medium",
                    affected_pages=thin_pages
                ))

        # Backlinks recommendations
        if results.get('backlinks_data', {}).get('summary'):
            summary = results['backlinks_data']['summary']
            ref_domains = summary.get('referring_domains', 0)

            if ref_domains < 10:
                recommendations.append(SEORecommendation(
                    priority=IssueSeverity.HIGH,
                    category=IssueCategory.TECHNICAL,
                    issue=f"Low domain authority: only {ref_domains} referring domains",
                    recommendation="Focus on link building and content marketing to acquire more backlinks",
                    impact="Significant improvement in domain authority and rankings",
                    effort="high",
                    affected_pages=0
                ))

        # Technical recommendations
        if results.get('onpage_data', {}).get('summary'):
            summary = results['onpage_data']['summary']
            errors = summary.get('pages_with_errors', 0)

            if errors > 0:
                recommendations.append(SEORecommendation(
                    priority=IssueSeverity.CRITICAL,
                    category=IssueCategory.TECHNICAL,
                    issue=f"{errors} pages have errors",
                    recommendation="Fix technical errors including 4xx/5xx status codes, broken links, and missing resources",
                    impact="Better crawlability and user experience",
                    effort="medium",
                    affected_pages=errors
                ))

        # SERP recommendations
        if results.get('serp_data'):
            rankings = results['serp_data'].get('rankings', {})
            not_ranking = sum(1 for r in rankings.values() if r.get('our_position') is None)

            if not_ranking > 0:
                recommendations.append(SEORecommendation(
                    priority=IssueSeverity.MEDIUM,
                    category=IssueCategory.CONTENT,
                    issue=f"Not ranking for {not_ranking} tracked keywords",
                    recommendation="Create targeted content for keywords you're not ranking for",
                    impact="Increased organic visibility",
                    effort="high",
                    affected_pages=0
                ))

        # Sort by priority
        priority_order = {
            IssueSeverity.CRITICAL: 0,
            IssueSeverity.HIGH: 1,
            IssueSeverity.MEDIUM: 2,
            IssueSeverity.LOW: 3,
            IssueSeverity.INFO: 4
        }
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 5))

        return recommendations
