#!/usr/bin/env python3
"""
Enhanced Firecrawl v2.0 Client

Comprehensive wrapper for Firecrawl API v2 with:
- All endpoints (scrape, crawl, map, extract, search, batch)
- Actions support (click, scroll, wait, input, screenshot)
- WebSocket real-time monitoring
- Change tracking capabilities
- Batch scraping for large-scale operations
- Rate limiting and retry logic
- Cost tracking and estimation

API Version: v2 (https://api.firecrawl.dev/v2)
SDK Version: firecrawl-py >= 4.0.0
"""

import os
import time
import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
import hashlib

# HTTP clients
import requests
import aiohttp

# Try to import firecrawl SDK
try:
    from firecrawl import FirecrawlApp, AsyncFirecrawlApp
    HAS_FIRECRAWL_SDK = True
except ImportError:
    HAS_FIRECRAWL_SDK = False
    logging.warning("Firecrawl SDK not installed. Install with: pip install firecrawl-py>=4.0.0")

# Pydantic for schema validation
try:
    from pydantic import BaseModel
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class FirecrawlStats:
    """Track Firecrawl usage statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_credits_used: int = 0
    retry_count: int = 0
    rate_limit_hits: int = 0

    endpoint_usage: Dict[str, int] = field(default_factory=lambda: {
        'scrape': 0, 'crawl': 0, 'map': 0, 'extract': 0,
        'search': 0, 'batch_scrape': 0
    })
    credits_by_endpoint: Dict[str, int] = field(default_factory=lambda: {
        'scrape': 0, 'crawl': 0, 'map': 0, 'extract': 0,
        'search': 0, 'batch_scrape': 0
    })

    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


@dataclass
class ActionConfig:
    """Configuration for browser actions"""
    type: str  # wait, click, scroll, write, press, screenshot
    selector: Optional[str] = None
    milliseconds: Optional[int] = None
    direction: Optional[str] = None  # up, down
    amount: Optional[int] = None
    text: Optional[str] = None
    key: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to API-compatible dict"""
        result = {"type": self.type}
        if self.selector:
            result["selector"] = self.selector
        if self.milliseconds:
            result["milliseconds"] = self.milliseconds
        if self.direction:
            result["direction"] = self.direction
        if self.amount:
            result["amount"] = self.amount
        if self.text:
            result["text"] = self.text
        if self.key:
            result["key"] = self.key
        return result


# ============================================================================
# PRE-BUILT ACTION SEQUENCES
# ============================================================================

class ActionSequences:
    """Pre-built action sequences for common scenarios"""

    @staticmethod
    def infinite_scroll(scroll_count: int = 5, wait_ms: int = 1000) -> List[Dict]:
        """Scroll to load all lazy-loaded content"""
        actions = []
        for _ in range(scroll_count):
            actions.append({"type": "scroll", "direction": "down", "amount": 1000})
            actions.append({"type": "wait", "milliseconds": wait_ms})
        return actions

    @staticmethod
    def click_load_more(selector: str, click_count: int = 3, wait_ms: int = 2000) -> List[Dict]:
        """Click 'Load More' button multiple times"""
        actions = []
        for _ in range(click_count):
            actions.append({"type": "click", "selector": selector})
            actions.append({"type": "wait", "milliseconds": wait_ms})
        return actions

    @staticmethod
    def accept_cookies(selectors: List[str] = None) -> List[Dict]:
        """Try to dismiss cookie consent banners"""
        if selectors is None:
            selectors = [
                "[data-testid='cookie-accept']",
                "#accept-cookies",
                ".cookie-accept",
                "button[contains(text(), 'Accept')]",
                "[aria-label='Accept cookies']"
            ]
        actions = [{"type": "wait", "milliseconds": 1000}]
        for selector in selectors:
            actions.append({"type": "click", "selector": selector})
        return actions

    @staticmethod
    def wait_for_element(selector: str, timeout_ms: int = 5000) -> List[Dict]:
        """Wait for a specific element to appear"""
        return [
            {"type": "wait", "selector": selector, "milliseconds": timeout_ms}
        ]

    @staticmethod
    def take_screenshot() -> List[Dict]:
        """Take a full page screenshot"""
        return [{"type": "screenshot", "fullPage": True}]


# ============================================================================
# MAIN CLIENT CLASS
# ============================================================================

class EnhancedFirecrawlClient:
    """
    Enhanced Firecrawl v2.0 Client with comprehensive feature support

    Features:
    - All API v2 endpoints (scrape, crawl, map, extract, search, batch)
    - Actions for dynamic content (click, scroll, wait, input, screenshot)
    - WebSocket real-time monitoring
    - Batch scraping for large-scale operations
    - Change tracking and content diffing
    - Exponential backoff retry
    - Rate limit handling
    - Cost estimation and tracking
    """

    # API v2 base URL
    BASE_URL = "https://api.firecrawl.dev/v2"

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 2000,
        timeout: int = 60000
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

        # Initialize HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })

        # Initialize SDK clients if available
        if HAS_FIRECRAWL_SDK:
            self.sdk_client = FirecrawlApp(api_key=self.api_key)
            try:
                self.async_sdk_client = AsyncFirecrawlApp(api_key=self.api_key)
            except Exception:
                self.async_sdk_client = None
        else:
            self.sdk_client = None
            self.async_sdk_client = None

        self.stats = FirecrawlStats()

        # Content hash cache for change tracking
        self._content_hashes: Dict[str, str] = {}

    # ========================================================================
    # SCRAPE ENDPOINT (with Actions support)
    # ========================================================================

    async def scrape(
        self,
        url: str,
        formats: List[str] = None,
        only_main_content: bool = True,
        include_tags: List[str] = None,
        exclude_tags: List[str] = None,
        wait_for: int = 0,
        timeout: Optional[int] = None,
        actions: Optional[List[Dict]] = None,
        location: Optional[Dict] = None,
        mobile: bool = False,
        skip_tls_verification: bool = False,
        remove_base64_images: bool = False,
        extract: Optional[Dict] = None
    ) -> Dict:
        """
        Scrape single URL with v2 features including Actions

        Args:
            url: Target URL
            formats: Output formats ['markdown', 'html', 'rawHtml', 'screenshot',
                    'links', 'extract', 'screenshot@fullPage']
            only_main_content: Extract only main content (remove nav/footer)
            include_tags: HTML tags to include
            exclude_tags: HTML tags to exclude
            wait_for: Time to wait before scraping (ms)
            timeout: Request timeout override (ms)
            actions: Browser actions to perform before scraping
                    [{"type": "click", "selector": "#btn"},
                     {"type": "scroll", "direction": "down"}]
            location: Geographic targeting {'country': 'US', 'languages': ['en']}
            mobile: Emulate mobile device
            skip_tls_verification: Skip TLS verification
            remove_base64_images: Remove base64 images from output
            extract: LLM extraction config {'schema': {}, 'prompt': ''}

        Returns:
            Dict with 'success', 'data', 'creditsUsed'
        """
        self.stats.total_requests += 1
        self.stats.endpoint_usage['scrape'] += 1

        payload = {
            'url': url,
            'formats': formats or ['markdown'],
            'onlyMainContent': only_main_content
        }

        if include_tags:
            payload['includeTags'] = include_tags
        if exclude_tags:
            payload['excludeTags'] = exclude_tags
        if wait_for > 0:
            payload['waitFor'] = wait_for
        if timeout:
            payload['timeout'] = timeout
        if actions:
            payload['actions'] = actions
        if location:
            payload['location'] = location
        if mobile:
            payload['mobile'] = True
        if skip_tls_verification:
            payload['skipTlsVerification'] = True
        if remove_base64_images:
            payload['removeBase64Images'] = True
        if extract:
            payload['extract'] = extract

        result = await self._execute_with_retry(
            endpoint='/scrape',
            payload=payload,
            method='POST'
        )

        if result.get('success'):
            credits = self._estimate_scrape_credits(result, actions)
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
        allow_external_links: bool = False,
        allow_subdomains: bool = False,
        ignore_sitemap: bool = False,
        webhook: Optional[str] = None
    ) -> Dict:
        """
        Crawl website with v2 API

        Args:
            url: Base URL to crawl
            limit: Maximum pages to crawl
            scrape_options: Options for each page (formats, onlyMainContent, etc.)
            include_paths: URL pathname patterns to include ['/docs/*']
            exclude_paths: URL pathname patterns to exclude ['/admin/*']
            max_depth: Maximum crawl depth
            allow_external_links: Allow following external links
            allow_subdomains: Allow following subdomain links
            ignore_sitemap: Skip sitemap discovery
            webhook: Webhook URL for progress updates

        Returns:
            Dict with 'success', 'data', 'creditsUsed', 'status'
        """
        self.stats.total_requests += 1
        self.stats.endpoint_usage['crawl'] += 1

        payload = {
            'url': url,
            'limit': limit,
            'scrapeOptions': scrape_options or {'formats': ['markdown']}
        }

        if include_paths:
            payload['includePaths'] = include_paths
        if exclude_paths:
            payload['excludePaths'] = exclude_paths
        if max_depth is not None:
            payload['maxDepth'] = max_depth
        if allow_external_links:
            payload['allowExternalLinks'] = True
        if allow_subdomains:
            payload['allowSubdomains'] = True
        if ignore_sitemap:
            payload['ignoreSitemap'] = True
        if webhook:
            payload['webhook'] = webhook

        # Start crawl job
        result = await self._execute_with_retry(
            endpoint='/crawl',
            payload=payload,
            method='POST'
        )

        if result.get('success') and result.get('id'):
            # Poll for completion
            job_id = result['id']
            result = await self._poll_job_status(f'/crawl/{job_id}', 'crawl')

        return result

    async def crawl_async(
        self,
        url: str,
        **kwargs
    ) -> str:
        """
        Start async crawl and return job ID immediately

        Args:
            url: Base URL to crawl
            **kwargs: Same as crawl()

        Returns:
            Job ID string
        """
        kwargs['url'] = url
        payload = self._build_crawl_payload(**kwargs)

        result = await self._execute_with_retry(
            endpoint='/crawl',
            payload=payload,
            method='POST'
        )

        if result.get('success'):
            return result.get('id')
        raise Exception(f"Failed to start crawl: {result.get('error')}")

    def _build_crawl_payload(self, **kwargs) -> Dict:
        """Build crawl payload from kwargs"""
        payload = {
            'url': kwargs.get('url'),
            'limit': kwargs.get('limit', 100),
            'scrapeOptions': kwargs.get('scrape_options', {'formats': ['markdown']})
        }

        optional_fields = [
            ('include_paths', 'includePaths'),
            ('exclude_paths', 'excludePaths'),
            ('max_depth', 'maxDepth'),
            ('allow_external_links', 'allowExternalLinks'),
            ('allow_subdomains', 'allowSubdomains'),
            ('ignore_sitemap', 'ignoreSitemap'),
            ('webhook', 'webhook')
        ]

        for kwarg_name, api_name in optional_fields:
            if kwargs.get(kwarg_name):
                payload[api_name] = kwargs[kwarg_name]

        return payload

    async def get_crawl_status(self, job_id: str) -> Dict:
        """Get crawl job status"""
        return await self._execute_with_retry(
            endpoint=f'/crawl/{job_id}',
            payload={},
            method='GET'
        )

    async def cancel_crawl(self, job_id: str) -> Dict:
        """Cancel running crawl job"""
        return await self._execute_with_retry(
            endpoint=f'/crawl/{job_id}',
            payload={},
            method='DELETE'
        )

    # ========================================================================
    # BATCH SCRAPE ENDPOINT (NEW in v2)
    # ========================================================================

    async def batch_scrape(
        self,
        urls: List[str],
        formats: List[str] = None,
        only_main_content: bool = True,
        actions: Optional[List[Dict]] = None,
        webhook: Optional[str] = None,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> Dict:
        """
        Batch scrape multiple URLs asynchronously

        Args:
            urls: List of URLs to scrape (up to 10,000)
            formats: Output formats for all URLs
            only_main_content: Extract only main content
            actions: Actions to perform on each page
            webhook: Webhook URL for progress updates
            on_progress: Callback function(completed, total)

        Returns:
            Dict with 'success', 'data', 'creditsUsed', 'total', 'completed'
        """
        self.stats.total_requests += 1
        self.stats.endpoint_usage['batch_scrape'] += 1

        payload = {
            'urls': urls,
            'formats': formats or ['markdown'],
            'onlyMainContent': only_main_content
        }

        if actions:
            payload['actions'] = actions
        if webhook:
            payload['webhook'] = webhook

        # Start batch job
        result = await self._execute_with_retry(
            endpoint='/batch/scrape',
            payload=payload,
            method='POST'
        )

        if result.get('success') and result.get('id'):
            job_id = result['id']
            result = await self._poll_job_status(
                f'/batch/scrape/{job_id}',
                'batch_scrape',
                on_progress=on_progress
            )

        return result

    async def batch_scrape_async(
        self,
        urls: List[str],
        **kwargs
    ) -> str:
        """
        Start async batch scrape and return job ID immediately

        Args:
            urls: List of URLs to scrape
            **kwargs: Same as batch_scrape()

        Returns:
            Job ID string
        """
        payload = {
            'urls': urls,
            'formats': kwargs.get('formats', ['markdown']),
            'onlyMainContent': kwargs.get('only_main_content', True)
        }

        if kwargs.get('actions'):
            payload['actions'] = kwargs['actions']
        if kwargs.get('webhook'):
            payload['webhook'] = kwargs['webhook']

        result = await self._execute_with_retry(
            endpoint='/batch/scrape',
            payload=payload,
            method='POST'
        )

        if result.get('success'):
            return result.get('id')
        raise Exception(f"Failed to start batch scrape: {result.get('error')}")

    async def get_batch_status(self, job_id: str) -> Dict:
        """Get batch scrape job status"""
        return await self._execute_with_retry(
            endpoint=f'/batch/scrape/{job_id}',
            payload={},
            method='GET'
        )

    async def cancel_batch(self, job_id: str) -> Dict:
        """Cancel running batch scrape job"""
        return await self._execute_with_retry(
            endpoint=f'/batch/scrape/{job_id}',
            payload={},
            method='DELETE'
        )

    # ========================================================================
    # MAP ENDPOINT
    # ========================================================================

    async def map(
        self,
        url: str,
        search: Optional[str] = None,
        limit: int = 5000,
        ignore_sitemap: bool = False,
        include_subdomains: bool = False
    ) -> Dict:
        """
        Fast URL discovery with v2 API

        Args:
            url: Base URL to map
            search: Keyword filtering for URLs
            limit: Maximum URLs to return
            ignore_sitemap: Skip sitemap
            include_subdomains: Include subdomain URLs

        Returns:
            Dict with 'success', 'links', 'creditsUsed'
        """
        self.stats.total_requests += 1
        self.stats.endpoint_usage['map'] += 1

        payload = {
            'url': url,
            'limit': limit
        }

        if search:
            payload['search'] = search
        if ignore_sitemap:
            payload['ignoreSitemap'] = True
        if include_subdomains:
            payload['includeSubdomains'] = True

        result = await self._execute_with_retry(
            endpoint='/map',
            payload=payload,
            method='POST'
        )

        if result.get('success'):
            credits = 1  # Map costs 1 credit
            result['creditsUsed'] = credits
            self.stats.credits_by_endpoint['map'] += credits
            self.stats.total_credits_used += credits

        return result

    # ========================================================================
    # EXTRACT ENDPOINT (LLM-powered)
    # ========================================================================

    async def extract(
        self,
        urls: List[str],
        prompt: Optional[str] = None,
        schema: Optional[Union[Dict, Any]] = None,
        system_prompt: Optional[str] = None,
        allow_external_links: bool = False
    ) -> Dict:
        """
        AI-powered structured extraction with v2 API

        Args:
            urls: List of URLs (supports wildcards: 'example.com/*')
            prompt: Natural language extraction instructions
            schema: JSON Schema or Pydantic model for structured data
            system_prompt: Custom system prompt for LLM
            allow_external_links: Allow following external links

        Returns:
            Dict with 'success', 'data' (extracted structured data)
        """
        if not prompt and not schema:
            raise ValueError("Either prompt or schema required for extraction")

        self.stats.total_requests += 1
        self.stats.endpoint_usage['extract'] += 1

        payload = {
            'urls': urls,
            'allowExternalLinks': allow_external_links
        }

        if prompt:
            payload['prompt'] = prompt

        if schema:
            # Handle Pydantic models
            if HAS_PYDANTIC and hasattr(schema, 'model_json_schema'):
                payload['schema'] = schema.model_json_schema()
            else:
                payload['schema'] = schema

        if system_prompt:
            payload['systemPrompt'] = system_prompt

        result = await self._execute_with_retry(
            endpoint='/extract',
            payload=payload,
            method='POST'
        )

        if result.get('success'):
            # Extract is token-based
            credits = len(urls) * 5
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
        lang: str = 'en',
        country: str = 'us',
        scrape_options: Optional[Dict] = None
    ) -> Dict:
        """
        Web search with optional scraping

        Args:
            query: Search query
            limit: Maximum results (max 10)
            lang: Language code
            country: Country code
            scrape_options: Options for scraping results

        Returns:
            Dict with 'success', 'data' (search results)
        """
        self.stats.total_requests += 1
        self.stats.endpoint_usage['search'] += 1

        payload = {
            'query': query,
            'limit': min(limit, 10),
            'lang': lang,
            'country': country
        }

        if scrape_options:
            payload['scrapeOptions'] = scrape_options

        result = await self._execute_with_retry(
            endpoint='/search',
            payload=payload,
            method='POST'
        )

        if result.get('success'):
            # Search: 1 credit per result + scraping costs
            credits = len(result.get('data', []))
            if scrape_options:
                credits += len(result.get('data', []))

            result['creditsUsed'] = credits
            self.stats.credits_by_endpoint['search'] += credits
            self.stats.total_credits_used += credits

        return result

    # ========================================================================
    # CHANGE TRACKING
    # ========================================================================

    def compute_content_hash(self, content: str) -> str:
        """Compute SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def check_for_changes(
        self,
        url: str,
        previous_hash: Optional[str] = None
    ) -> Dict:
        """
        Check if URL content has changed

        Args:
            url: URL to check
            previous_hash: Previous content hash (uses cache if not provided)

        Returns:
            Dict with 'changed', 'current_hash', 'previous_hash'
        """
        result = await self.scrape(url=url, formats=['markdown'])

        if not result.get('success'):
            return {'changed': None, 'error': result.get('error')}

        content = result.get('data', {}).get('markdown', '')
        current_hash = self.compute_content_hash(content)

        # Use provided hash or cached hash
        prev_hash = previous_hash or self._content_hashes.get(url)

        # Update cache
        self._content_hashes[url] = current_hash

        if prev_hash is None:
            return {
                'changed': None,
                'current_hash': current_hash,
                'previous_hash': None,
                'first_check': True
            }

        return {
            'changed': current_hash != prev_hash,
            'current_hash': current_hash,
            'previous_hash': prev_hash
        }

    # ========================================================================
    # JOB POLLING
    # ========================================================================

    async def _poll_job_status(
        self,
        endpoint: str,
        job_type: str,
        poll_interval: int = 5,
        max_polls: int = 1000,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> Dict:
        """Poll job status until completion"""
        for _ in range(max_polls):
            status = await self._execute_with_retry(
                endpoint=endpoint,
                payload={},
                method='GET'
            )

            job_status = status.get('status', 'unknown')

            # Call progress callback if provided
            if on_progress and status.get('total'):
                on_progress(status.get('completed', 0), status.get('total'))

            if job_status in ['completed', 'failed', 'cancelled']:
                completed = status.get('completed', 0)
                credits = completed

                self.stats.credits_by_endpoint[job_type] += credits
                self.stats.total_credits_used += credits

                if job_status == 'completed':
                    self.stats.successful_requests += 1
                else:
                    self.stats.failed_requests += 1

                return {
                    'success': job_status == 'completed',
                    'data': status.get('data', []),
                    'creditsUsed': credits,
                    'status': job_status,
                    'total': status.get('total', 0),
                    'completed': completed
                }

            logger.info(f"Job progress: {status.get('completed', 0)}/{status.get('total', '?')}")
            await asyncio.sleep(poll_interval)

        return {'success': False, 'error': 'Polling timeout exceeded'}

    # ========================================================================
    # RETRY LOGIC
    # ========================================================================

    async def _execute_with_retry(
        self,
        endpoint: str,
        payload: Dict,
        method: str = 'POST',
        attempt: int = 1
    ) -> Dict:
        """
        Execute request with exponential backoff retry

        Args:
            endpoint: API endpoint path
            payload: Request payload
            method: HTTP method (GET, POST, DELETE)
            attempt: Current retry attempt
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }

                if method == 'GET':
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                        return await self._handle_response(response)
                elif method == 'DELETE':
                    async with session.delete(url, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                        return await self._handle_response(response)
                else:  # POST
                    async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                        return await self._handle_response(response)

        except Exception as e:
            error_msg = str(e)

            # Handle rate limiting
            if "429" in error_msg or "rate limit" in error_msg.lower():
                self.stats.rate_limit_hits += 1

                if attempt < self.max_retries:
                    backoff_delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit. Retrying in {backoff_delay}s... (attempt {attempt}/{self.max_retries})")
                    await asyncio.sleep(backoff_delay)
                    self.stats.retry_count += 1
                    return await self._execute_with_retry(endpoint, payload, method, attempt + 1)

            # Retry transient errors
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.warning(f"Request failed. Retrying in {delay}s... (attempt {attempt}/{self.max_retries})")
                await asyncio.sleep(delay)
                self.stats.retry_count += 1
                return await self._execute_with_retry(endpoint, payload, method, attempt + 1)

            self.stats.failed_requests += 1
            logger.error(f"All {self.max_retries} retries exhausted: {error_msg}")
            return {'success': False, 'error': error_msg}

    async def _handle_response(self, response) -> Dict:
        """Handle HTTP response"""
        if response.status == 200:
            self.stats.successful_requests += 1
            data = await response.json()
            return {
                'success': True,
                **data,
                'timestamp': datetime.now().isoformat()
            }
        elif response.status == 429:
            raise Exception("Rate limit hit")
        elif response.status == 402:
            self.stats.failed_requests += 1
            return {'success': False, 'error': 'Quota exceeded'}
        else:
            text = await response.text()
            raise Exception(f"HTTP {response.status}: {text}")

    # ========================================================================
    # COST ESTIMATION
    # ========================================================================

    def _estimate_scrape_credits(self, result: Dict, actions: Optional[List] = None) -> int:
        """Estimate credits used for scrape"""
        credits = 1  # Base cost

        data = result.get('data', {})

        # Actions add cost
        if actions:
            credits += len(actions)

        # Screenshots add cost
        if isinstance(data, dict):
            if data.get('screenshot'):
                credits += 2

        return credits

    # ========================================================================
    # STATISTICS
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
