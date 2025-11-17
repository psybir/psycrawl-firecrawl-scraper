#!/usr/bin/env python3
"""
Enhanced Firecrawl v2.5 Client

Comprehensive wrapper for Firecrawl API v2.5 with:
- All 5 endpoints (scrape, crawl, map, extract, search)
- Stealth mode and actions support
- Semantic index caching
- FIRE-1 agent integration
- Rate limiting and retry logic
- Cost tracking and estimation
"""

import os
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
import requests  # Always needed for direct API calls

# Try to import firecrawl SDK (for simple crawls)
try:
    from firecrawl import Firecrawl
    HAS_FIRECRAWL_SDK = True
except ImportError:
    HAS_FIRECRAWL_SDK = False
    logging.warning("Firecrawl SDK not installed. Install with: pip install firecrawl-py")

logger = logging.getLogger(__name__)


@dataclass
class FirecrawlStats:
    """Track Firecrawl usage statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_credits_used: int = 0
    retry_count: int = 0
    rate_limit_hits: int = 0

    # Per-endpoint stats
    endpoint_usage: Dict[str, int] = field(default_factory=lambda: {
        'scrape': 0, 'crawl': 0, 'map': 0, 'extract': 0, 'search': 0
    })
    credits_by_endpoint: Dict[str, int] = field(default_factory=lambda: {
        'scrape': 0, 'crawl': 0, 'map': 0, 'extract': 0, 'search': 0
    })

    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


class EnhancedFirecrawlClient:
    """
    Enhanced Firecrawl v2.5 Client with comprehensive feature support

    Features:
    - All 5 endpoints (scrape, crawl, map, extract, search)
    - Stealth mode and interactive actions
    - Semantic index caching (5x faster)
    - FIRE-1 agent support
    - Exponential backoff retry
    - Rate limit handling
    - Cost estimation and tracking
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 2000,
        timeout: int = 30000
    ):
        """
        Initialize Firecrawl client

        Args:
            api_key: Firecrawl API key (defaults to FIRECRAWL_API_KEY env var)
            max_retries: Maximum retry attempts
            retry_delay: Base delay for exponential backoff (ms)
            timeout: Request timeout (ms)
        """
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
        if not self.api_key:
            raise ValueError("Firecrawl API key required. Set FIRECRAWL_API_KEY environment variable.")

        self.max_retries = max_retries
        self.retry_delay = retry_delay / 1000  # Convert to seconds
        self.timeout = timeout / 1000

        # Initialize API base URL and session (always needed for direct API)
        self.base_url = "https://api.firecrawl.dev/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })

        # Initialize SDK if available (for simple crawls)
        if HAS_FIRECRAWL_SDK:
            self.client = Firecrawl(api_key=self.api_key)

        self.stats = FirecrawlStats()

    # ========================================================================
    # SCRAPE ENDPOINT
    # ========================================================================

    async def scrape(
        self,
        url: str,
        formats: List[str] = None,
        only_main_content: bool = True,
        max_age: int = 172800000,  # 2 days default
        store_in_cache: bool = True,
        proxy: Optional[str] = None,
        actions: Optional[List[Dict]] = None,
        json_config: Optional[Dict] = None,
        location: Optional[Dict] = None,
        timeout: Optional[int] = None,
        agent: Optional[Dict] = None
    ) -> Dict:
        """
        Scrape single URL with v2.5 features

        Args:
            url: Target URL
            formats: Output formats ['markdown', 'html', 'screenshot', 'links', 'json']
            only_main_content: Extract only main content (remove nav/footer)
            max_age: Cache freshness in ms (0 = force fresh)
            store_in_cache: Store in semantic index
            proxy: Proxy mode ('auto' for stealth fallback, 'stealth' for always)
            actions: Interactive actions (wait, click, scroll, write, press, screenshot)
            json_config: JSON extraction config {'schema': {}, 'prompt': ''}
            location: Geographic targeting {'country': 'US', 'languages': ['en']}
            timeout: Request timeout override (ms)
            agent: FIRE-1 agent config {'model': 'FIRE-1', 'prompt': ''}

        Returns:
            Dict with 'success', 'data', 'creditsUsed'
        """
        self.stats.total_requests += 1
        self.stats.endpoint_usage['scrape'] += 1

        payload = {
            'url': url,
            'formats': formats or ['markdown'],
            'onlyMainContent': only_main_content,  # Fixed: API expects camelCase
            'maxAge': max_age,
            'storeInCache': store_in_cache
        }

        # Stealth mode
        if proxy:
            payload['proxy'] = proxy

        # Interactive actions
        if actions:
            payload['actions'] = actions

        # JSON extraction
        if json_config:
            payload['json'] = json_config

        # Geographic targeting
        if location:
            payload['location'] = location

        # FIRE-1 agent
        if agent:
            payload['agent'] = agent

        # Timeout override
        if timeout:
            payload['timeout'] = timeout

        result = await self._execute_with_retry(
            endpoint='/scrape',
            payload=payload,
            method='scrape',
            force_http=True  # Use direct API - SDK doesn't support all v2.5 parameters
        )

        if result.get('success'):
            # Estimate credits
            credits = self._estimate_credits(result, 'scrape', proxy, agent)
            result['creditsUsed'] = credits
            self.stats.credits_by_endpoint['scrape'] += credits
            self.stats.total_credits_used += credits

        return result

    # ========================================================================
    # CRAWL ENDPOINT
    # ========================================================================

    async def crawl(
        self,
        url: str,
        limit: int = 100,
        scrape_options: Optional[Dict] = None,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        allow_backward_links: bool = False,
        allow_external_links: bool = False,
        ignore_sitemap: bool = False,
        crawl_entire_domain: bool = False,
        allow_subdomains: bool = False,
        webhook: Optional[Dict] = None
    ) -> Dict:
        """
        Crawl website (blocking - recommended)

        Args:
            url: Base URL to crawl
            limit: Maximum pages to crawl (default: 10000)
            scrape_options: Options for each page (formats, onlyMainContent, etc.)
            include_paths: URL pathname regex patterns to include ['/docs/*']
            exclude_paths: URL pathname regex patterns to exclude ['/admin/*']
            max_depth: Maximum crawl depth based on discovery order (maps to API maxDiscoveryDepth)
                      Root site and sitemapped pages have depth 0. Saves 30% credits.
            allow_backward_links: DEPRECATED - Use crawl_entire_domain instead.
                                 This parameter doesn't exist in Firecrawl API v2.
            allow_external_links: Allow crawler to follow external website links
            ignore_sitemap: Controls sitemap usage (maps to API sitemap: 'skip'|'include')
                           True = skip sitemap, False = include sitemap
            crawl_entire_domain: Allow crawler to follow internal links including siblings/parents
                                (replaces allow_backward_links functionality)
            allow_subdomains: Allow crawler to follow subdomain links
            webhook: Webhook config {'url': '', 'events': ['page', 'completed'], 'headers': {}}

        Returns:
            Dict with 'success', 'data' (list of pages), 'creditsUsed', 'status', 'total', 'completed'

        Note:
            API parameter mappings:
            - max_depth → maxDiscoveryDepth (camelCase)
            - include_paths → includePaths
            - exclude_paths → excludePaths
            - ignore_sitemap → sitemap: "skip"|"include"
            - crawl_entire_domain → crawlEntireDomain
        """
        self.stats.total_requests += 1
        self.stats.endpoint_usage['crawl'] += 1

        # Detect if advanced crawl parameters are being used
        # SDK doesn't support these yet, so we need to use direct API
        has_advanced_params = (
            max_depth is not None or
            exclude_paths is not None or
            include_paths is not None or
            crawl_entire_domain or
            ignore_sitemap or
            allow_external_links or
            allow_subdomains or
            webhook is not None
        )

        # Route to SDK for simple crawls, direct API for advanced parameters
        if HAS_FIRECRAWL_SDK and not has_advanced_params:
            # Simple crawl via SDK - only basic parameters supported
            # Python SDK crawl() method signature:
            # crawl(url, limit, poll_interval, timeout, scrape_options)
            try:
                # SDK handles pagination automatically and returns CrawlJob object
                crawl_job = self.client.crawl(
                    url=url,
                    limit=limit,
                    scrape_options=scrape_options or {'formats': ['markdown']}
                )

                # CrawlJob is a Pydantic model with direct property access
                # Properties: status, total, completed, credits_used, data (List[Document])
                data = crawl_job.data if hasattr(crawl_job, 'data') else []
                credits = crawl_job.credits_used if hasattr(crawl_job, 'credits_used') else len(data)

                self.stats.successful_requests += 1
                self.stats.credits_by_endpoint['crawl'] += credits
                self.stats.total_credits_used += credits

                return {
                    'success': True,
                    'data': data,
                    'creditsUsed': credits,
                    'status': crawl_job.status if hasattr(crawl_job, 'status') else 'completed',
                    'total': crawl_job.total if hasattr(crawl_job, 'total') else len(data),
                    'completed': crawl_job.completed if hasattr(crawl_job, 'completed') else len(data)
                }
            except Exception as e:
                self.stats.failed_requests += 1
                logger.error(f"SDK crawl error: {e}")
                return {'success': False, 'error': str(e)}

        # Direct API path for advanced parameters or when SDK unavailable
        if has_advanced_params or not HAS_FIRECRAWL_SDK:
            # Direct API requests use camelCase
            payload = {
                'url': url,
                'limit': limit,
                'scrapeOptions': scrape_options or {'formats': ['markdown']},
                'crawlEntireDomain': crawl_entire_domain,
                'allowSubdomains': allow_subdomains
            }
            if include_paths:
                payload['includePaths'] = include_paths
            if exclude_paths:
                payload['excludePaths'] = exclude_paths
            if max_depth is not None:
                payload['maxDiscoveryDepth'] = max_depth  # FIXED: API uses maxDiscoveryDepth, not maxDepth
            if allow_external_links:
                payload['allowExternalLinks'] = allow_external_links
            # Note: Removed allowBackwardLinks - doesn't exist in API. Use crawlEntireDomain instead.
            if ignore_sitemap:
                payload['sitemap'] = 'skip' if ignore_sitemap else 'include'  # FIXED: API uses sitemap enum, not ignoreSitemap boolean
            if webhook:
                payload['webhook'] = webhook

            # Execute direct API request (bypass SDK)
            result = await self._execute_with_retry(
                endpoint='/crawl',
                payload=payload,
                method='POST',
                force_http=True  # Force direct HTTP, bypass SDK
            )

            if result.get('success'):
                # Poll for completion
                job_id = result.get('id')
                result = await self._poll_crawl_status(job_id)

            return result

    async def _poll_crawl_status(self, job_id: str, poll_interval: int = 5) -> Dict:
        """Poll crawl job status until completion"""
        while True:
            status = await self.get_crawl_status(job_id)

            if status.get('status') in ['completed', 'failed', 'cancelled']:
                credits = status.get('completed', 0) * 1
                self.stats.credits_by_endpoint['crawl'] += credits
                self.stats.total_credits_used += credits

                return {
                    'success': status.get('status') == 'completed',
                    'data': status.get('data', []),
                    'creditsUsed': credits,
                    'status': status.get('status')
                }

            logger.info(f"Crawl progress: {status.get('completed', 0)}/{status.get('total', '?')}")
            await asyncio.sleep(poll_interval)

    async def get_crawl_status(self, job_id: str) -> Dict:
        """Get crawl job status"""
        if HAS_FIRECRAWL_SDK:
            try:
                return self.client.get_crawl_status(job_id)
            except Exception as e:
                logger.error(f"Get crawl status error: {e}")
                return {'success': False, 'error': str(e)}
        else:
            response = self.session.get(f"{self.base_url}/crawl/status/{job_id}")
            return response.json()

    # ========================================================================
    # MAP ENDPOINT
    # ========================================================================

    async def map(
        self,
        url: str,
        search: Optional[str] = None,
        limit: int = 100,
        sitemap: str = "include",
        location: Optional[Dict] = None
    ) -> Dict:
        """
        Fast URL discovery

        Args:
            url: Base URL to map
            search: Keyword filtering
            limit: Maximum URLs to return
            sitemap: Include XML sitemap ('include' or 'exclude')
            location: Geographic targeting

        Returns:
            Dict with 'success', 'links' (list of {url, title, description})
        """
        self.stats.total_requests += 1
        self.stats.endpoint_usage['map'] += 1

        payload = {
            'url': url,
            'limit': limit,
            'sitemap': sitemap
        }

        if search:
            payload['search'] = search

        if location:
            payload['location'] = location

        result = await self._execute_with_retry(
            endpoint='/map',
            payload=payload,
            method='map'
        )

        if result.get('success'):
            credits = 1  # Map is cheap
            result['creditsUsed'] = credits
            self.stats.credits_by_endpoint['map'] += credits
            self.stats.total_credits_used += credits

        return result

    # ========================================================================
    # EXTRACT ENDPOINT
    # ========================================================================

    async def extract(
        self,
        urls: List[str],
        schema: Optional[Dict] = None,
        prompt: Optional[str] = None,
        enable_web_search: bool = False,
        agent: Optional[Dict] = None
    ) -> Dict:
        """
        AI-powered structured extraction

        Args:
            urls: List of URLs (supports wildcards: 'example.com/*')
            schema: JSON Schema for structured data
            prompt: Natural language extraction instructions
            enable_web_search: Expand beyond specified domain
            agent: FIRE-1 agent config {'model': 'FIRE-1'}

        Returns:
            Dict with 'success', 'data' (extracted structured data)
        """
        if not schema and not prompt:
            raise ValueError("Either schema or prompt required for extraction")

        self.stats.total_requests += 1
        self.stats.endpoint_usage['extract'] += 1

        payload = {
            'urls': urls,
            'enableWebSearch': enable_web_search
        }

        if schema:
            payload['schema'] = schema

        if prompt:
            payload['prompt'] = prompt

        if agent:
            payload['agent'] = agent

        result = await self._execute_with_retry(
            endpoint='/extract',
            payload=payload,
            method='extract'
        )

        if result.get('success'):
            # Extract is token-based, estimate conservatively
            credits = len(urls) * 4  # Approximate
            if agent:
                credits *= 8  # FIRE-1 is ~8x more expensive

            result['creditsUsed'] = credits
            self.stats.credits_by_endpoint['extract'] += credits
            self.stats.total_credits_used += credits

        return result

    # ========================================================================
    # SEARCH ENDPOINT
    # ========================================================================

    async def search(
        self,
        query: str,
        limit: int = 10,
        tbs: Optional[str] = None,
        location: Optional[str] = None,
        sources: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        scrape_options: Optional[Dict] = None
    ) -> Dict:
        """
        Web search with optional scraping

        Args:
            query: Search query
            limit: Maximum results
            tbs: Time-based search ('qdr:d' = day, 'qdr:w' = week, 'qdr:m' = month)
            location: Geographic location
            sources: Result types ['web', 'news', 'images']
            categories: Categories ['github', 'arxiv', 'pdf']
            scrape_options: Options if scraping results

        Returns:
            Dict with 'success', 'data' (search results with optional content)
        """
        self.stats.total_requests += 1
        self.stats.endpoint_usage['search'] += 1

        payload = {
            'query': query,
            'limit': limit
        }

        if tbs:
            payload['tbs'] = tbs

        if location:
            payload['location'] = location

        if sources:
            payload['sources'] = sources

        if categories:
            payload['categories'] = categories

        if scrape_options:
            payload['scrapeOptions'] = scrape_options

        result = await self._execute_with_retry(
            endpoint='/search',
            payload=payload,
            method='search'
        )

        if result.get('success'):
            # Search: 2 credits per 10 results + scraping costs
            credits = (limit // 10 + 1) * 2
            if scrape_options:
                credits += limit * 1  # Add scraping costs

            result['creditsUsed'] = credits
            self.stats.credits_by_endpoint['search'] += credits
            self.stats.total_credits_used += credits

        return result

    # ========================================================================
    # RETRY LOGIC
    # ========================================================================

    async def _execute_with_retry(
        self,
        endpoint: str,
        payload: Dict,
        method: str,
        attempt: int = 1,
        force_http: bool = False
    ) -> Dict:
        """
        Execute request with exponential backoff retry

        Args:
            endpoint: API endpoint path
            payload: Request payload
            method: HTTP method or SDK method name
            attempt: Current retry attempt
            force_http: If True, bypass SDK and use direct HTTP (for advanced parameters)

        Handles:
        - 429 rate limits
        - 402 quota exceeded
        - 401/403 auth errors
        - Transient failures
        """
        try:
            if HAS_FIRECRAWL_SDK and not force_http:
                # Use SDK method
                sdk_method = getattr(self.client, method)
                result = sdk_method(**payload)

                self.stats.successful_requests += 1
                return {
                    'success': True,
                    'data': result.get('data') if isinstance(result, dict) else result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Use requests
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    self.stats.successful_requests += 1
                    return {
                        'success': True,
                        'data': response.json().get('data'),
                        'timestamp': datetime.now().isoformat()
                    }
                elif response.status_code == 429:
                    raise Exception("Rate limit hit")
                elif response.status_code == 402:
                    raise Exception("Quota exceeded")
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            error_msg = str(e)

            # Handle rate limiting
            if "429" in error_msg or "rate limit" in error_msg.lower():
                self.stats.rate_limit_hits += 1

                if attempt < self.max_retries:
                    # Exponential backoff: 2s → 4s → 8s
                    backoff_delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit. Retrying in {backoff_delay}s... (attempt {attempt}/{self.max_retries})")

                    await asyncio.sleep(backoff_delay)
                    self.stats.retry_count += 1

                    return await self._execute_with_retry(endpoint, payload, method, attempt + 1, force_http)

            # Handle quota exceeded
            if "402" in error_msg or "quota" in error_msg.lower():
                self.stats.failed_requests += 1
                logger.error("Firecrawl quota exceeded. Check credit balance.")
                return {'success': False, 'error': 'Quota exceeded'}

            # Retry transient errors
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.warning(f"Request failed. Retrying in {delay}s... (attempt {attempt}/{self.max_retries})")

                await asyncio.sleep(delay)
                self.stats.retry_count += 1

                return await self._execute_with_retry(endpoint, payload, method, attempt + 1, force_http)

            # All retries exhausted
            self.stats.failed_requests += 1
            logger.error(f"All {self.max_retries} retries exhausted: {error_msg}")
            return {'success': False, 'error': error_msg}

    # ========================================================================
    # COST ESTIMATION
    # ========================================================================

    def _estimate_credits(
        self,
        result: Dict,
        endpoint: str,
        proxy: Optional[str] = None,
        agent: Optional[Dict] = None
    ) -> int:
        """Estimate credits used based on response"""
        credits = 1  # Base cost

        data = result.get('data', {})

        # Stealth mode
        if proxy == 'stealth':
            credits = 5

        # FIRE-1 agent
        if agent and agent.get('model') == 'FIRE-1':
            credits = 150  # Base + 0-900 for agent

        # Additional formats
        if isinstance(data, dict):
            if data.get('screenshot'):
                credits += 2
            if data.get('pdf'):
                credits += 3

        return credits

    # ========================================================================
    # STATS
    # ========================================================================

    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            'total_requests': self.stats.total_requests,
            'successful_requests': self.stats.successful_requests,
            'failed_requests': self.stats.failed_requests,
            'success_rate': f"{self.stats.get_success_rate():.2f}%",
            'total_credits_used': self.stats.total_credits_used,
            'retry_count': self.stats.retry_count,
            'rate_limit_hits': self.stats.rate_limit_hits,
            'endpoint_usage': self.stats.endpoint_usage,
            'credits_by_endpoint': self.stats.credits_by_endpoint
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = FirecrawlStats()

    # ========================================================================
    # SEO EXTRACTION METHODS
    # ========================================================================

    async def extract_seo_data(
        self,
        url: str,
        extract_schema: bool = True,
        extract_content_structure: bool = True,
        extract_meta: bool = True,
        max_age: int = 172800000  # 2 days cache
    ) -> Dict:
        """
        Extract comprehensive SEO data from a single page

        Args:
            url: Target URL to analyze
            extract_schema: Extract Schema.org markup
            extract_content_structure: Extract headings, content sections, word count
            extract_meta: Extract meta tags, Open Graph, Twitter Cards
            max_age: Cache freshness in ms

        Returns:
            Dict with SEO data:
            {
                'url': str,
                'meta': {...},
                'schema': [...],
                'content_structure': {...},
                'headings': {...},
                'local_business': {...},
                'creditsUsed': int
            }
        """
        # Use scrape endpoint with custom extraction
        scrape_result = await self.scrape(
            url=url,
            formats=['html', 'markdown'],
            only_main_content=False,  # Need full page for meta/schema
            max_age=max_age,
            store_in_cache=True
        )

        if not scrape_result.get('success'):
            return scrape_result

        data = scrape_result.get('data', {})
        html_content = data.get('html', '')
        markdown_content = data.get('markdown', '')

        seo_data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'creditsUsed': scrape_result.get('creditsUsed', 1)
        }

        # Extract meta tags
        if extract_meta:
            seo_data['meta'] = self._extract_meta_tags(html_content, data)

        # Extract Schema.org markup
        if extract_schema:
            seo_data['schema'] = self._extract_schema_markup(html_content)

        # Extract content structure
        if extract_content_structure:
            seo_data['content_structure'] = self._extract_content_structure(html_content, markdown_content)
            seo_data['headings'] = self._extract_heading_hierarchy(markdown_content)

        # Extract local business data (if present)
        seo_data['local_business'] = self._extract_local_business_data(html_content, seo_data.get('schema', []))

        return {
            'success': True,
            'data': seo_data,
            'creditsUsed': seo_data['creditsUsed']
        }

    async def bulk_extract_competitors(
        self,
        urls: List[str],
        schema_prompt: Optional[str] = None,
        max_concurrent: int = 5
    ) -> Dict:
        """
        Extract SEO data from multiple competitor URLs in parallel

        Args:
            urls: List of competitor URLs
            schema_prompt: Optional prompt for custom data extraction
            max_concurrent: Maximum concurrent requests (default: 5)

        Returns:
            Dict with competitor data array and total credits
        """
        # Process in batches to respect rate limits
        results = []
        total_credits = 0

        for i in range(0, len(urls), max_concurrent):
            batch = urls[i:i + max_concurrent]

            # Extract SEO data for batch
            batch_tasks = [self.extract_seo_data(url) for url in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch extraction error: {result}")
                    continue

                if result.get('success'):
                    results.append(result.get('data'))
                    total_credits += result.get('creditsUsed', 1)

            # Progress logging
            logger.info(f"Processed {min(i + max_concurrent, len(urls))}/{len(urls)} competitors")

        return {
            'success': True,
            'data': results,
            'total_urls': len(urls),
            'successful_extractions': len(results),
            'creditsUsed': total_credits
        }

    async def extract_local_seo_signals(
        self,
        url: str,
        business_name: Optional[str] = None
    ) -> Dict:
        """
        Extract local SEO ranking signals

        Args:
            url: Business website URL
            business_name: Optional business name for NAP verification

        Returns:
            Dict with local SEO signals:
            {
                'nap': {...},  # Name, Address, Phone
                'schema': {...},  # LocalBusiness schema
                'citations': [...],  # Citation mentions
                'reviews': {...},  # Review markup
                'geo_targeting': {...},  # Geographic signals
                'creditsUsed': int
            }
        """
        scrape_result = await self.scrape(
            url=url,
            formats=['html', 'markdown'],
            only_main_content=False,
            max_age=0  # Force fresh for local data
        )

        if not scrape_result.get('success'):
            return scrape_result

        data = scrape_result.get('data', {})
        html_content = data.get('html', '')

        local_signals = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'creditsUsed': scrape_result.get('creditsUsed', 1)
        }

        # Extract NAP data
        local_signals['nap'] = self._extract_nap_data(html_content, business_name)

        # Extract LocalBusiness schema
        schemas = self._extract_schema_markup(html_content)
        local_signals['schema'] = [s for s in schemas if s.get('type') in ['LocalBusiness', 'Organization', 'Place']]

        # Extract review markup
        local_signals['reviews'] = self._extract_review_markup(html_content, schemas)

        # Extract geographic targeting signals
        local_signals['geo_targeting'] = self._extract_geo_signals(html_content, data)

        return {
            'success': True,
            'data': local_signals,
            'creditsUsed': local_signals['creditsUsed']
        }

    def _extract_meta_tags(self, html_content: str, data: Dict) -> Dict:
        """Extract meta tags, Open Graph, Twitter Cards"""
        import re

        meta_data = {
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'open_graph': {},
            'twitter_card': {},
            'robots': None,
            'canonical': None
        }

        # Extract Open Graph tags
        og_pattern = r'<meta\s+property=["\']og:([^"\']+)["\']\s+content=["\']([^"\']+)["\']'
        for match in re.finditer(og_pattern, html_content, re.IGNORECASE):
            meta_data['open_graph'][match.group(1)] = match.group(2)

        # Extract Twitter Card tags
        twitter_pattern = r'<meta\s+name=["\']twitter:([^"\']+)["\']\s+content=["\']([^"\']+)["\']'
        for match in re.finditer(twitter_pattern, html_content, re.IGNORECASE):
            meta_data['twitter_card'][match.group(1)] = match.group(2)

        # Extract robots meta
        robots_pattern = r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']'
        robots_match = re.search(robots_pattern, html_content, re.IGNORECASE)
        if robots_match:
            meta_data['robots'] = robots_match.group(1)

        # Extract canonical URL
        canonical_pattern = r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']'
        canonical_match = re.search(canonical_pattern, html_content, re.IGNORECASE)
        if canonical_match:
            meta_data['canonical'] = canonical_match.group(1)

        return meta_data

    def _extract_schema_markup(self, html_content: str) -> List[Dict]:
        """Extract and parse Schema.org JSON-LD markup"""
        import re
        import json

        schemas = []

        # Find all JSON-LD script tags
        pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)

        for match in matches:
            try:
                schema_json = json.loads(match.group(1))

                # Handle @graph arrays
                if isinstance(schema_json, dict) and '@graph' in schema_json:
                    schemas.extend(schema_json['@graph'])
                elif isinstance(schema_json, list):
                    schemas.extend(schema_json)
                else:
                    schemas.append(schema_json)

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse schema JSON: {e}")

        # Extract type from @type field
        for schema in schemas:
            if '@type' in schema:
                schema['type'] = schema['@type']

        return schemas

    def _extract_content_structure(self, html_content: str, markdown_content: str) -> Dict:
        """Extract content structure metrics"""
        import re

        # Word count from markdown
        words = re.findall(r'\b\w+\b', markdown_content)
        word_count = len(words)

        # Paragraph count
        paragraphs = re.findall(r'<p[^>]*>.*?</p>', html_content, re.DOTALL)
        paragraph_count = len(paragraphs)

        # Image count
        images = re.findall(r'<img[^>]*>', html_content)
        image_count = len(images)

        # Link count
        internal_links = re.findall(r'<a[^>]*href=["\'](?!http)[^"\']*["\'][^>]*>', html_content)
        external_links = re.findall(r'<a[^>]*href=["\']https?://[^"\']*["\'][^>]*>', html_content)

        return {
            'word_count': word_count,
            'paragraph_count': paragraph_count,
            'image_count': image_count,
            'internal_link_count': len(internal_links),
            'external_link_count': len(external_links),
            'avg_paragraph_length': word_count / max(paragraph_count, 1)
        }

    def _extract_heading_hierarchy(self, markdown_content: str) -> Dict:
        """Extract heading structure"""
        import re

        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }

        # Extract headings from markdown
        for level in range(1, 7):
            pattern = r'^#{' + str(level) + r'}\s+(.+)$'
            matches = re.finditer(pattern, markdown_content, re.MULTILINE)
            headings[f'h{level}'] = [match.group(1).strip() for match in matches]

        # Calculate heading metrics
        total_headings = sum(len(h) for h in headings.values())

        return {
            'headings': headings,
            'total_count': total_headings,
            'h1_count': len(headings['h1']),
            'h2_count': len(headings['h2']),
            'hierarchy_depth': max([level for level in range(1, 7) if headings[f'h{level}']], default=0)
        }

    def _extract_local_business_data(self, html_content: str, schemas: List[Dict]) -> Dict:
        """Extract local business data from schema and HTML"""
        local_data = {
            'has_local_schema': False,
            'business_type': None,
            'address': None,
            'phone': None,
            'hours': None,
            'geo_coordinates': None
        }

        # Find LocalBusiness schema
        for schema in schemas:
            schema_type = schema.get('type', schema.get('@type', ''))

            if 'LocalBusiness' in str(schema_type) or 'Organization' in str(schema_type):
                local_data['has_local_schema'] = True
                local_data['business_type'] = schema_type

                # Extract address
                if 'address' in schema:
                    local_data['address'] = schema['address']

                # Extract phone
                if 'telephone' in schema:
                    local_data['phone'] = schema['telephone']

                # Extract hours
                if 'openingHoursSpecification' in schema:
                    local_data['hours'] = schema['openingHoursSpecification']

                # Extract geo coordinates
                if 'geo' in schema:
                    local_data['geo_coordinates'] = schema['geo']

                break

        return local_data

    def _extract_nap_data(self, html_content: str, business_name: Optional[str]) -> Dict:
        """Extract NAP (Name, Address, Phone) consistency data"""
        import re

        nap_data = {
            'name': business_name,
            'addresses_found': [],
            'phones_found': [],
            'consistency_score': 0.0
        }

        # Extract phone numbers (US format)
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, html_content)
        nap_data['phones_found'] = [''.join(p) for p in phones]

        # Extract addresses (simple pattern)
        address_pattern = r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way)'
        addresses = re.findall(address_pattern, html_content, re.IGNORECASE)
        nap_data['addresses_found'] = list(set(addresses))[:5]  # Limit to 5 unique

        # Calculate consistency (simplified)
        if len(nap_data['phones_found']) > 0 and len(nap_data['addresses_found']) > 0:
            # High consistency if single phone and address
            phone_consistency = 1.0 if len(set(nap_data['phones_found'])) == 1 else 0.5
            address_consistency = 1.0 if len(nap_data['addresses_found']) == 1 else 0.5
            nap_data['consistency_score'] = (phone_consistency + address_consistency) / 2

        return nap_data

    def _extract_review_markup(self, html_content: str, schemas: List[Dict]) -> Dict:
        """Extract review and rating markup"""
        review_data = {
            'has_reviews': False,
            'aggregate_rating': None,
            'review_count': 0,
            'rating_value': 0.0
        }

        # Find Review or AggregateRating schema
        for schema in schemas:
            schema_type = schema.get('type', schema.get('@type', ''))

            if 'aggregateRating' in schema:
                review_data['has_reviews'] = True
                rating = schema['aggregateRating']
                review_data['aggregate_rating'] = rating
                review_data['rating_value'] = float(rating.get('ratingValue', 0))
                review_data['review_count'] = int(rating.get('reviewCount', 0))
                break

            if 'Review' in str(schema_type):
                review_data['has_reviews'] = True
                if 'reviewRating' in schema:
                    review_data['rating_value'] = float(schema['reviewRating'].get('ratingValue', 0))

        return review_data

    def _extract_geo_signals(self, html_content: str, data: Dict) -> Dict:
        """Extract geographic targeting signals"""
        import re

        geo_signals = {
            'has_geo_meta': False,
            'location_keywords': [],
            'service_areas': []
        }

        # Extract geo meta tags
        geo_pattern = r'<meta\s+name=["\']geo\.[^"\']+["\']\s+content=["\']([^"\']+)["\']'
        geo_matches = re.findall(geo_pattern, html_content, re.IGNORECASE)
        if geo_matches:
            geo_signals['has_geo_meta'] = True

        # Extract common location keywords (cities, states)
        location_pattern = r'\b(?:in|near|serving|located)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?(?:,\s*[A-Z]{2})?)\b'
        locations = re.findall(location_pattern, html_content)
        geo_signals['location_keywords'] = list(set(locations))[:10]

        return geo_signals
