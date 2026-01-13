#!/usr/bin/env python3
"""
DataForSEO API v3 Client

Comprehensive client for DataForSEO API with all major modules:
- SERP API: Search engine rankings
- Keywords Data: Search volume, CPC, competition
- Backlinks API: Link analysis, domain authority
- OnPage API: Technical SEO crawling
- DataForSEO Labs: Competitor intelligence, keyword research

Authentication: HTTP Basic Auth with login (email) and password (API key)
Base URL: https://api.dataforseo.com/v3

Usage:
    from firecrawl_scraper.core.dataforseo_client import DataForSEOClient

    client = DataForSEOClient(login='email', password='api_key')
    result = await client.backlinks_summary('example.com')
"""

import os
import base64
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class DataForSEOStats:
    """Track DataForSEO API usage"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cost: float = 0.0
    endpoint_usage: Dict[str, int] = field(default_factory=dict)
    endpoint_costs: Dict[str, float] = field(default_factory=dict)


class DataForSEOClient:
    """
    DataForSEO API v3 Client

    Features:
    - All major API modules (SERP, Keywords, Backlinks, OnPage, Labs)
    - Async/await support
    - Automatic retry with exponential backoff
    - Cost tracking
    - Task-based API support (POST task, GET results)
    """

    BASE_URL = "https://api.dataforseo.com/v3"

    # API cost estimates (approximate, varies by endpoint)
    COSTS = {
        'serp_google_organic': 0.002,
        'serp_google_maps': 0.004,
        'keywords_google_ads': 0.05,
        'keywords_for_site': 0.05,
        'backlinks_summary': 0.2,
        'backlinks_backlinks': 0.5,
        'backlinks_referring_domains': 0.5,
        'onpage_task_post': 0.01,
        'labs_domain_metrics': 0.02,
        'labs_competitors': 0.05,
        'labs_keyword_ideas': 0.05,
    }

    def __init__(
        self,
        login: Optional[str] = None,
        password: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: int = 120
    ):
        """
        Initialize DataForSEO client.

        Args:
            login: DataForSEO login (email). Defaults to DATAFORSEO_LOGIN env var.
            password: DataForSEO API password. Defaults to DATAFORSEO_PASSWORD env var.
            max_retries: Maximum retry attempts
            retry_delay: Base delay for exponential backoff (seconds)
            timeout: Request timeout (seconds)
        """
        self.login = login or os.getenv('DATAFORSEO_LOGIN')
        self.password = password or os.getenv('DATAFORSEO_PASSWORD')

        if not self.login or not self.password:
            raise ValueError(
                "DataForSEO credentials required. "
                "Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD environment variables."
            )

        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout

        # Create auth header (HTTP Basic Auth)
        credentials = f"{self.login}:{self.password}"
        self._auth_header = base64.b64encode(credentials.encode()).decode()

        self.stats = DataForSEOStats()

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication"""
        return {
            'Authorization': f'Basic {self._auth_header}',
            'Content-Type': 'application/json'
        }

    # ========================================================================
    # CORE REQUEST METHOD
    # ========================================================================

    async def _request(
        self,
        endpoint: str,
        method: str = 'POST',
        data: Optional[List[Dict]] = None,
        cost_key: Optional[str] = None
    ) -> Dict:
        """
        Make authenticated request to DataForSEO API.

        Args:
            endpoint: API endpoint path (e.g., '/serp/google/organic/live/advanced')
            method: HTTP method (GET or POST)
            data: Request payload (list of task objects for POST)
            cost_key: Key for cost tracking

        Returns:
            Dict with 'success', 'data', 'cost' keys
        """
        url = f"{self.BASE_URL}{endpoint}"
        self.stats.total_requests += 1

        if cost_key:
            self.stats.endpoint_usage[cost_key] = self.stats.endpoint_usage.get(cost_key, 0) + 1

        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    timeout = aiohttp.ClientTimeout(total=self.timeout)

                    if method == 'GET':
                        async with session.get(url, headers=self._get_headers(), timeout=timeout) as response:
                            return await self._handle_response(response, cost_key)
                    else:
                        async with session.post(url, headers=self._get_headers(), json=data, timeout=timeout) as response:
                            return await self._handle_response(response, cost_key)

            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Request failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    self.stats.failed_requests += 1
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
                    return {'success': False, 'error': str(e)}

        return {'success': False, 'error': 'Max retries exceeded'}

    async def _handle_response(self, response, cost_key: Optional[str] = None) -> Dict:
        """Handle API response"""
        data = await response.json()

        if response.status == 200:
            self.stats.successful_requests += 1

            # Track costs
            cost = data.get('cost', 0)
            if cost_key and cost_key in self.COSTS:
                estimated_cost = self.COSTS[cost_key]
                cost = cost or estimated_cost

            self.stats.total_cost += cost
            if cost_key:
                self.stats.endpoint_costs[cost_key] = self.stats.endpoint_costs.get(cost_key, 0) + cost

            return {
                'success': True,
                'data': data.get('tasks', []),
                'cost': cost,
                'status_code': data.get('status_code'),
                'status_message': data.get('status_message'),
                'time': data.get('time'),
                'version': data.get('version')
            }
        else:
            self.stats.failed_requests += 1
            return {
                'success': False,
                'error': data.get('status_message', f'HTTP {response.status}'),
                'status_code': response.status
            }

    # ========================================================================
    # SERP API - Search Engine Results
    # ========================================================================

    async def serp_google_organic(
        self,
        keyword: str,
        location_name: str = "United States",
        language_code: str = "en",
        device: str = "desktop",
        depth: int = 100
    ) -> Dict:
        """
        Get Google organic search results for a keyword.

        Args:
            keyword: Search keyword
            location_name: Target location (e.g., "United States", "New York,New York,United States")
            language_code: Language code (e.g., "en", "es", "de")
            device: Device type ("desktop" or "mobile")
            depth: Number of results to return (10-700)

        Returns:
            Dict with SERP data including rankings, snippets, URLs
        """
        data = [{
            "keyword": keyword,
            "location_name": location_name,
            "language_code": language_code,
            "device": device,
            "depth": depth
        }]

        return await self._request(
            '/serp/google/organic/live/advanced',
            data=data,
            cost_key='serp_google_organic'
        )

    async def serp_google_maps(
        self,
        keyword: str,
        location_name: str = "United States",
        language_code: str = "en"
    ) -> Dict:
        """Get Google Maps/Local results"""
        data = [{
            "keyword": keyword,
            "location_name": location_name,
            "language_code": language_code
        }]

        return await self._request(
            '/serp/google/maps/live/advanced',
            data=data,
            cost_key='serp_google_maps'
        )

    async def serp_bing_organic(
        self,
        keyword: str,
        location_name: str = "United States",
        language_code: str = "en"
    ) -> Dict:
        """Get Bing organic search results"""
        data = [{
            "keyword": keyword,
            "location_name": location_name,
            "language_code": language_code
        }]

        return await self._request(
            '/serp/bing/organic/live/advanced',
            data=data,
            cost_key='serp_bing_organic'
        )

    # ========================================================================
    # KEYWORDS DATA API
    # ========================================================================

    async def keywords_google_ads(
        self,
        keywords: List[str],
        location_code: int = 2840,  # USA
        language_code: str = "en"
    ) -> Dict:
        """
        Get keyword data from Google Ads.

        Args:
            keywords: List of keywords (max 1000)
            location_code: Location code (2840 = USA)
            language_code: Language code

        Returns:
            Dict with search volume, CPC, competition for each keyword
        """
        data = [{
            "keywords": keywords[:1000],
            "location_code": location_code,
            "language_code": language_code
        }]

        return await self._request(
            '/keywords_data/google_ads/search_volume/live',
            data=data,
            cost_key='keywords_google_ads'
        )

    async def keywords_for_site(
        self,
        target: str,
        location_code: int = 2840,
        language_code: str = "en",
        include_serp_info: bool = True
    ) -> Dict:
        """
        Get keywords that a domain ranks for.

        Args:
            target: Domain to analyze (e.g., "example.com")
            location_code: Location code
            language_code: Language code
            include_serp_info: Include SERP position data

        Returns:
            Dict with keywords, positions, search volumes
        """
        data = [{
            "target": target,
            "location_code": location_code,
            "language_code": language_code,
            "include_serp_info": include_serp_info
        }]

        return await self._request(
            '/keywords_data/google_ads/keywords_for_site/live',
            data=data,
            cost_key='keywords_for_site'
        )

    # ========================================================================
    # BACKLINKS API
    # ========================================================================

    async def backlinks_summary(self, target: str) -> Dict:
        """
        Get backlink summary for a domain.

        Args:
            target: Domain to analyze (e.g., "example.com")

        Returns:
            Dict with total backlinks, referring domains, domain rank, etc.
        """
        data = [{
            "target": target,
            "internal_list_limit": 10,
            "backlinks_status_type": "live"
        }]

        return await self._request(
            '/backlinks/summary/live',
            data=data,
            cost_key='backlinks_summary'
        )

    async def backlinks_backlinks(
        self,
        target: str,
        limit: int = 100,
        order_by: str = "rank,desc"
    ) -> Dict:
        """
        Get list of backlinks for a domain.

        Args:
            target: Domain to analyze
            limit: Number of backlinks to return
            order_by: Sort order (e.g., "rank,desc", "page_from_rank,desc")

        Returns:
            Dict with backlink details (source URL, anchor text, etc.)
        """
        data = [{
            "target": target,
            "limit": limit,
            "order_by": [order_by],
            "backlinks_status_type": "live"
        }]

        return await self._request(
            '/backlinks/backlinks/live',
            data=data,
            cost_key='backlinks_backlinks'
        )

    async def backlinks_referring_domains(
        self,
        target: str,
        limit: int = 100
    ) -> Dict:
        """
        Get referring domains for a target.

        Args:
            target: Domain to analyze
            limit: Number of referring domains to return

        Returns:
            Dict with referring domain details
        """
        data = [{
            "target": target,
            "limit": limit,
            "backlinks_status_type": "live"
        }]

        return await self._request(
            '/backlinks/referring_domains/live',
            data=data,
            cost_key='backlinks_referring_domains'
        )

    async def backlinks_domain_pages(
        self,
        target: str,
        limit: int = 100
    ) -> Dict:
        """Get pages with most backlinks on a domain"""
        data = [{
            "target": target,
            "limit": limit
        }]

        return await self._request(
            '/backlinks/domain_pages/live',
            data=data,
            cost_key='backlinks_domain_pages'
        )

    # ========================================================================
    # ONPAGE API - Technical SEO
    # ========================================================================

    async def onpage_task_post(
        self,
        target: str,
        max_crawl_pages: int = 100,
        enable_javascript: bool = False
    ) -> Dict:
        """
        Create OnPage crawl task.

        Args:
            target: Domain to crawl (e.g., "https://example.com")
            max_crawl_pages: Maximum pages to crawl
            enable_javascript: Enable JavaScript rendering

        Returns:
            Dict with task_id for checking results
        """
        data = [{
            "target": target,
            "max_crawl_pages": max_crawl_pages,
            "enable_javascript": enable_javascript,
            "load_resources": enable_javascript,
            "enable_browser_rendering": enable_javascript
        }]

        return await self._request(
            '/on_page/task_post',
            data=data,
            cost_key='onpage_task_post'
        )

    async def onpage_summary(self, task_id: str) -> Dict:
        """
        Get OnPage crawl summary.

        Args:
            task_id: Task ID from task_post

        Returns:
            Dict with crawl summary (errors, warnings, notices)
        """
        return await self._request(
            f'/on_page/summary/{task_id}',
            method='GET',
            cost_key='onpage_summary'
        )

    async def onpage_pages(
        self,
        task_id: str,
        limit: int = 100
    ) -> Dict:
        """
        Get OnPage crawled pages.

        Args:
            task_id: Task ID from task_post
            limit: Number of pages to return

        Returns:
            Dict with page-level SEO data
        """
        data = [{
            "id": task_id,
            "limit": limit
        }]

        return await self._request(
            '/on_page/pages',
            data=data,
            cost_key='onpage_pages'
        )

    async def onpage_pages_by_resource(
        self,
        task_id: str,
        resource_type: str = "broken"
    ) -> Dict:
        """
        Get pages filtered by resource type.

        Args:
            task_id: Task ID from task_post
            resource_type: Filter type ("broken", "redirect", "duplicate_content", etc.)
        """
        data = [{
            "id": task_id,
            "filters": [["resource_type", "=", resource_type]]
        }]

        return await self._request(
            '/on_page/pages',
            data=data,
            cost_key='onpage_pages_filtered'
        )

    # ========================================================================
    # DATAFORSEO LABS API - Competitor Intelligence
    # ========================================================================

    async def labs_domain_metrics_by_categories(
        self,
        target: str,
        location_code: int = 2840,
        language_code: str = "en"
    ) -> Dict:
        """
        Get domain metrics and category rankings.

        Args:
            target: Domain to analyze
            location_code: Location code
            language_code: Language code

        Returns:
            Dict with organic/paid traffic, keywords, categories
        """
        data = [{
            "target": target,
            "location_code": location_code,
            "language_code": language_code
        }]

        return await self._request(
            '/dataforseo_labs/google/domain_metrics_by_categories/live',
            data=data,
            cost_key='labs_domain_metrics'
        )

    async def labs_competitors_domain(
        self,
        target: str,
        location_code: int = 2840,
        language_code: str = "en",
        limit: int = 20
    ) -> Dict:
        """
        Find competitors for a domain.

        Args:
            target: Domain to analyze
            location_code: Location code
            language_code: Language code
            limit: Number of competitors to return

        Returns:
            Dict with competitor domains and overlap metrics
        """
        data = [{
            "target": target,
            "location_code": location_code,
            "language_code": language_code,
            "limit": limit
        }]

        return await self._request(
            '/dataforseo_labs/google/competitors_domain/live',
            data=data,
            cost_key='labs_competitors'
        )

    async def labs_keyword_ideas(
        self,
        keyword: str,
        location_code: int = 2840,
        language_code: str = "en",
        limit: int = 100
    ) -> Dict:
        """
        Get keyword ideas/suggestions.

        Args:
            keyword: Seed keyword
            location_code: Location code
            language_code: Language code
            limit: Number of ideas to return

        Returns:
            Dict with related keywords, search volumes, difficulty
        """
        data = [{
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "limit": limit
        }]

        return await self._request(
            '/dataforseo_labs/google/keyword_ideas/live',
            data=data,
            cost_key='labs_keyword_ideas'
        )

    async def labs_ranked_keywords(
        self,
        target: str,
        location_code: int = 2840,
        language_code: str = "en",
        limit: int = 100
    ) -> Dict:
        """
        Get keywords a domain ranks for with positions.

        Args:
            target: Domain to analyze
            location_code: Location code
            language_code: Language code
            limit: Number of keywords to return

        Returns:
            Dict with keywords, positions, search volumes
        """
        data = [{
            "target": target,
            "location_code": location_code,
            "language_code": language_code,
            "limit": limit,
            "order_by": ["keyword_data.keyword_info.search_volume,desc"]
        }]

        return await self._request(
            '/dataforseo_labs/google/ranked_keywords/live',
            data=data,
            cost_key='labs_ranked_keywords'
        )

    async def labs_domain_intersection(
        self,
        targets: List[str],
        location_code: int = 2840,
        language_code: str = "en",
        limit: int = 100
    ) -> Dict:
        """
        Find common keywords between domains.

        Args:
            targets: List of domains to compare (2-20)
            location_code: Location code
            language_code: Language code
            limit: Number of keywords to return

        Returns:
            Dict with shared keywords and positions for each domain
        """
        # Build targets dict
        targets_dict = {}
        for i, target in enumerate(targets[:20], 1):
            targets_dict[f"target{i}"] = target

        data = [{
            **targets_dict,
            "location_code": location_code,
            "language_code": language_code,
            "limit": limit
        }]

        return await self._request(
            '/dataforseo_labs/google/domain_intersection/live',
            data=data,
            cost_key='labs_domain_intersection'
        )

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            'total_requests': self.stats.total_requests,
            'successful_requests': self.stats.successful_requests,
            'failed_requests': self.stats.failed_requests,
            'success_rate': f"{(self.stats.successful_requests / max(1, self.stats.total_requests) * 100):.2f}%",
            'total_cost': f"${self.stats.total_cost:.4f}",
            'endpoint_usage': self.stats.endpoint_usage,
            'endpoint_costs': {k: f"${v:.4f}" for k, v in self.stats.endpoint_costs.items()}
        }

    def reset_stats(self):
        """Reset usage statistics"""
        self.stats = DataForSEOStats()

    async def check_balance(self) -> Dict:
        """Check account balance"""
        return await self._request('/appendix/user_data', method='GET')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_serp_results(response: Dict) -> List[Dict]:
    """
    Extract SERP results from API response.

    Args:
        response: Raw API response

    Returns:
        List of result dicts with url, title, position, etc.
    """
    results = []

    if not response.get('success'):
        return results

    for task in response.get('data', []):
        task_result = task.get('result', [])
        for result_set in task_result:
            items = result_set.get('items', [])
            for item in items:
                if item.get('type') == 'organic':
                    results.append({
                        'position': item.get('rank_absolute'),
                        'url': item.get('url'),
                        'title': item.get('title'),
                        'description': item.get('description'),
                        'domain': item.get('domain'),
                        'breadcrumb': item.get('breadcrumb')
                    })

    return results


def extract_backlinks_summary(response: Dict) -> Dict:
    """
    Extract backlinks summary from API response.

    Args:
        response: Raw API response

    Returns:
        Dict with backlinks metrics
    """
    if not response.get('success'):
        return {}

    for task in response.get('data', []):
        task_result = task.get('result', [])
        for result in task_result:
            return {
                'total_backlinks': result.get('backlinks'),
                'referring_domains': result.get('referring_domains'),
                'referring_main_domains': result.get('referring_main_domains'),
                'rank': result.get('rank'),
                'backlinks_spam_score': result.get('backlinks_spam_score'),
                'referring_ips': result.get('referring_ips'),
                'referring_subnets': result.get('referring_subnets'),
                'broken_backlinks': result.get('broken_backlinks'),
                'broken_pages': result.get('broken_pages'),
                'referring_pages': result.get('referring_pages'),
                'referring_links_tld': result.get('referring_links_tld'),
                'referring_links_types': result.get('referring_links_types'),
                'referring_links_attributes': result.get('referring_links_attributes')
            }

    return {}
