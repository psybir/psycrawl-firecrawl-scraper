#!/usr/bin/env python3
"""
Universal Firecrawl Scraper - Dynamic scraping system for any use case
Supports 3 strategies: CRAWL, EXTRACT, and MAP with proper v2.6.0 parameters
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import aiohttp
from urllib.parse import urlparse

# Import centralized configuration
from firecrawl_scraper.config import Config

# Import Enhanced Firecrawl Client (has async wrappers)
sys.path.insert(0, str(Path(__file__).parent.parent))
from firecrawl_scraper.core.firecrawl_client import EnhancedFirecrawlClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.OUTPUT_DIR / 'universal-scraper.log'),
        logging.StreamHandler()
    ]
)


class ScrapingStrategy:
    """Base class for scraping strategies"""

    def __init__(self, client: EnhancedFirecrawlClient):
        self.client = client
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scraping strategy - override in subclasses"""
        raise NotImplementedError


class CrawlStrategy(ScrapingStrategy):
    """Strategy for multi-page documentation sites"""

    async def execute(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Crawl entire domain for comprehensive content"""
        url = source['url']
        self.logger.info(f"🔄 CRAWL strategy: {url}")

        # Determine if stealth mode should be used
        use_stealth = source.get('use_stealth', False)
        difficulty = source.get('difficulty', 'low')

        # Auto-enable stealth for high difficulty sites
        if difficulty in ['high', 'very_high']:
            use_stealth = True
            self.logger.info(f"🕶️  Stealth mode enabled (difficulty: {difficulty})")

        try:
            # Step 1: Map URLs to discover all pages
            map_result = await self.client.map(url=url, limit=source.get('max_pages', 50))

            # Extract links from the Pydantic MapData object
            map_data = map_result.get('data')
            if hasattr(map_data, 'links'):
                # MapData Pydantic model - access attributes directly
                links = map_data.links or []
                discovered_urls = [link.url if hasattr(link, 'url') else link for link in links][:source.get('max_pages', 50)]
            elif isinstance(map_data, dict):
                # Dictionary response - use .get()
                discovered_urls = map_data.get('links', [])[:source.get('max_pages', 50)]
            else:
                discovered_urls = []

            self.logger.info(f"📍 Discovered {len(discovered_urls)} URLs")

            # Step 2: Scrape each discovered URL with optional stealth mode
            scrape_results = []
            for page_url in discovered_urls:
                try:
                    result = await self.client.scrape(
                        url=page_url,
                        formats=['markdown', 'html', 'links'],
                        only_main_content=True,
                        timeout=60000,
                        proxy='stealth' if use_stealth else None  # Enable stealth mode
                    )

                    if result.get('success'):
                        data = result.get('data', {})
                        # Handle Pydantic Document object or dict
                        if hasattr(data, 'markdown'):
                            # Pydantic Document object
                            scrape_results.append({
                                'markdown': data.markdown or '',
                                'html': getattr(data, 'html', ''),
                                'links': getattr(data, 'links', [])
                            })
                        elif isinstance(data, dict):
                            # Dictionary response
                            scrape_results.append(data)

                except Exception as e:
                    self.logger.warning(f"⚠️  Failed to scrape {page_url}: {e}")

            # Validate content
            total_content = sum(len(page.get('markdown', '')) for page in scrape_results)

            return {
                'success': True,
                'strategy': 'crawl',
                'pages_discovered': len(discovered_urls),
                'total_chars': total_content,
                'data': scrape_results,
                'credits_used': 5 + len(discovered_urls)  # v2.6.0: 5 for map + 1 per page
            }

        except Exception as e:
            self.logger.error(f"❌ CRAWL failed for {url}: {e}")
            return {
                'success': False,
                'strategy': 'crawl',
                'error': str(e)
            }


class ExtractStrategy(ScrapingStrategy):
    """Strategy for structured data extraction from showcase sites"""

    async def execute(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data using schema"""
        url = source['url']
        schema = source.get('schema', self._get_default_schema())

        self.logger.info(f"🎯 EXTRACT strategy: {url}")

        # Determine if stealth mode should be used
        use_stealth = source.get('use_stealth', False)
        difficulty = source.get('difficulty', 'low')

        # Auto-enable stealth for high difficulty sites
        if difficulty in ['high', 'very_high']:
            use_stealth = True
            self.logger.info(f"🕶️  Stealth mode enabled (difficulty: {difficulty})")

        try:
            # Use regular scraping with optional stealth mode
            # TODO: Update when EnhancedFirecrawlClient supports extract parameter properly
            result = await self.client.scrape(
                url=url,
                formats=['markdown', 'html'],
                only_main_content=True,
                timeout=60000,
                proxy='stealth' if use_stealth else None  # Enable stealth mode
            )

            # Extract data from result (using markdown/html instead of extract format)
            if result.get('success'):
                data = result.get('data', {})
                # Handle Pydantic Document object or dict
                if hasattr(data, 'markdown'):
                    # Pydantic Document object
                    extracted_data = {
                        'markdown': data.markdown or '',
                        'html': getattr(data, 'html', ''),
                        'content_length': len(data.markdown or '')
                    }
                elif isinstance(data, dict):
                    # Dictionary response
                    extracted_data = {
                        'markdown': data.get('markdown', ''),
                        'html': data.get('html', ''),
                        'content_length': len(data.get('markdown', ''))
                    }
                else:
                    extracted_data = {}
            else:
                extracted_data = {}

            return {
                'success': result.get('success', False),
                'strategy': 'extract',
                'extracted_fields': len(extracted_data),
                'data': extracted_data,
                'credits_used': 1  # v2.6.0: regular scrape costs 1 credit
            }

        except Exception as e:
            self.logger.error(f"❌ EXTRACT failed for {url}: {e}")
            return {
                'success': False,
                'strategy': 'extract',
                'error': str(e)
            }

    def _get_default_schema(self) -> Dict:
        """Default extraction schema for design quality sites"""
        return {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'description': {'type': 'string'},
                'design_principles': {
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                'code_examples': {
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                'best_practices': {
                    'type': 'array',
                    'items': {'type': 'string'}
                }
            }
        }


class MapStrategy(ScrapingStrategy):
    """Strategy for selective URL discovery and targeted scraping"""

    async def execute(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Map URLs then selectively scrape"""
        url = source['url']
        self.logger.info(f"🗺️  MAP strategy: {url}")

        # Determine if stealth mode should be used
        use_stealth = source.get('use_stealth', False)
        difficulty = source.get('difficulty', 'low')

        # Auto-enable stealth for high difficulty sites
        if difficulty in ['high', 'very_high']:
            use_stealth = True
            self.logger.info(f"🕶️  Stealth mode enabled (difficulty: {difficulty})")

        try:
            # Step 1: Map URLs (5 credits)
            map_result = await self.client.map(url=url, limit=source.get('max_pages', 100))

            # Extract links from the Pydantic MapData object
            map_data = map_result.get('data')
            if hasattr(map_data, 'links'):
                # MapData Pydantic model - access attributes directly
                links = map_data.links or []
                discovered_urls = [link.url if hasattr(link, 'url') else link for link in links]
            elif isinstance(map_data, dict):
                # Dictionary response - use .get()
                discovered_urls = map_data.get('links', [])
            else:
                discovered_urls = []

            self.logger.info(f"📍 Discovered {len(discovered_urls)} URLs")

            # Step 2: Filter URLs based on keywords
            keywords = source.get('filter_keywords', [])
            filtered_urls = self._filter_urls(discovered_urls, keywords) if keywords else discovered_urls[:source.get('max_pages', 20)]

            self.logger.info(f"🎯 Filtered to {len(filtered_urls)} URLs")

            # Step 3: Batch scrape filtered URLs with optional stealth mode
            scrape_results = []
            for batch_url in filtered_urls:
                try:
                    result = await self.client.scrape(
                        url=batch_url,
                        proxy='stealth' if use_stealth else None,  # Enable stealth mode
                        formats=['markdown', 'html', 'links'],
                        only_main_content=True,
                        timeout=60000
                    )

                    # Validate content
                    if result.get('success'):
                        data = result.get('data', {})
                        # Handle Pydantic Document object or dict
                        if hasattr(data, 'markdown'):
                            # Pydantic Document object
                            markdown_content = data.markdown or ''
                            if len(markdown_content) > 1000:
                                scrape_results.append({
                                    'markdown': markdown_content,
                                    'html': getattr(data, 'html', ''),
                                    'links': getattr(data, 'links', [])
                                })
                            else:
                                self.logger.warning(f"⚠️  Low content ({len(markdown_content)} chars): {batch_url}")
                        elif isinstance(data, dict):
                            # Dictionary response
                            if len(data.get('markdown', '')) > 1000:
                                scrape_results.append(data)
                            else:
                                self.logger.warning(f"⚠️  Low content ({len(data.get('markdown', ''))} chars): {batch_url}")

                except Exception as e:
                    self.logger.error(f"❌ Failed to scrape {batch_url}: {e}")

            total_content = sum(len(page.get('markdown', '')) for page in scrape_results)

            return {
                'success': True,
                'strategy': 'map',
                'urls_discovered': len(discovered_urls),
                'urls_scraped': len(scrape_results),
                'total_chars': total_content,
                'data': scrape_results,
                'credits_used': 5 + len(filtered_urls)  # v2.6.0: 5 for map + 1 per page
            }

        except Exception as e:
            self.logger.error(f"❌ MAP failed for {url}: {e}")
            return {
                'success': False,
                'strategy': 'map',
                'error': str(e)
            }

    def _filter_urls(self, urls: List[str], keywords: List[str]) -> List[str]:
        """Filter URLs containing specific keywords"""
        filtered = []
        for url in urls:
            if any(keyword.lower() in url.lower() for keyword in keywords):
                filtered.append(url)
        return filtered


class UniversalScraper:
    """
    Universal web scraping system with strategy-based routing.

    Supports 3 strategies:
    - CRAWL: Multi-page documentation sites
    - EXTRACT: Structured data from showcase sites
    - MAP: Selective URL discovery and targeted scraping
    """

    def __init__(self, api_key: str, output_dir: str = '/Volumes/Samsung 990 Pro/WordPress AI/wordpress-ai-factory/data/scraping-runs'):
        self.client = EnhancedFirecrawlClient(api_key=api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('UniversalScraper')

        # Initialize strategies
        self.strategies = {
            'crawl': CrawlStrategy(self.client),
            'extract': ExtractStrategy(self.client),
            'map': MapStrategy(self.client)
        }

        # Checkpoint management
        self.checkpoint_dir = self.output_dir / 'checkpoints'
        self.checkpoint_dir.mkdir(exist_ok=True)

    def auto_detect_strategy(self, source: Dict[str, Any]) -> str:
        """
        Automatically detect best scraping strategy based on source characteristics.

        Logic:
        - CRAWL: Documentation sites, developer resources (needs comprehensive crawling)
        - EXTRACT: Showcase sites, award sites (needs structured extraction)
        - MAP: Blogs, articles (needs selective scraping)
        """
        url = source['url'].lower()
        category = source.get('category', '').lower()

        # Documentation sites → CRAWL
        if 'docs' in url or 'documentation' in url or 'academy' in category:
            return 'crawl'

        # Showcase/award sites → EXTRACT
        if 'showcase' in category or 'award' in category or 'design' in category:
            return 'extract'

        # Blogs/articles → MAP
        if 'blog' in url or 'article' in url or 'tutorial' in category:
            return 'map'

        # Default to MAP (safest, most flexible)
        return 'map'

    async def validate_url(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Validate URL is reachable before attempting to scrape.

        Args:
            url: URL to validate
            timeout: Timeout in seconds for HTTP request

        Returns:
            Dict with 'valid' bool and optional 'error' message
        """
        try:
            # Parse URL to validate format
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {
                    'valid': False,
                    'error': 'Invalid URL format (missing scheme or domain)',
                    'details': f'scheme={parsed.scheme}, netloc={parsed.netloc}'
                }

            # Attempt HEAD request to check if URL is reachable
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.head(url, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True) as response:
                        if response.status >= 400:
                            return {
                                'valid': False,
                                'error': f'HTTP {response.status} error',
                                'status_code': response.status
                            }
                        return {
                            'valid': True,
                            'status_code': response.status,
                            'final_url': str(response.url)
                        }
                except aiohttp.ClientConnectorError as e:
                    return {
                        'valid': False,
                        'error': 'Cannot connect to domain (domain does not exist or is unreachable)',
                        'details': str(e)
                    }
                except asyncio.TimeoutError:
                    return {
                        'valid': False,
                        'error': f'Connection timeout after {timeout} seconds',
                        'details': 'Server did not respond in time'
                    }
                except Exception as e:
                    return {
                        'valid': False,
                        'error': f'Network error: {type(e).__name__}',
                        'details': str(e)
                    }

        except Exception as e:
            return {
                'valid': False,
                'error': f'URL validation error: {type(e).__name__}',
                'details': str(e)
            }

    async def scrape_source(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scrape a single source using appropriate strategy.

        Args:
            source: Dict with 'url', optional 'strategy', 'category', 'max_pages', etc.

        Returns:
            Dict with scraping results and metadata
        """
        url = source['url']
        difficulty = source.get('difficulty', 'low')

        # Skip URL validation for high-difficulty sites (they often block HEAD requests)
        # Stealth mode will handle the anti-bot protection during actual scraping
        skip_validation = source.get('skip_validation', False) or difficulty in ['high', 'very_high']

        # Validate URL before scraping (optional - can be disabled with skip_validation=True)
        if not skip_validation:
            self.logger.info(f"🔍 Validating URL: {url}")
            url_validation = await self.validate_url(url)

            if not url_validation['valid']:
                self.logger.error(f"❌ URL validation failed: {url_validation['error']}")
                return {
                    'success': False,
                    'url': url,
                    'error': url_validation['error'],
                    'error_type': 'url_validation_failed',
                    'validation_details': url_validation,
                    'timestamp': datetime.now().isoformat()
                }

            self.logger.info(f"✅ URL validated (HTTP {url_validation.get('status_code', 'OK')})")
        else:
            self.logger.info(f"⏭️  Skipping URL validation (difficulty: {difficulty}) - will use stealth mode")

        # Determine strategy (auto-detect or use specified)
        strategy_name = source.get('strategy', self.auto_detect_strategy(source))

        self.logger.info(f"🎯 Scraping {url} with {strategy_name.upper()} strategy")

        # Execute strategy
        strategy = self.strategies.get(strategy_name)
        if not strategy:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        result = await strategy.execute(source)

        # Add metadata
        result['url'] = url
        result['category'] = source.get('category', 'general')
        result['timestamp'] = datetime.now().isoformat()
        result['source_metadata'] = source

        # Validate result
        validation = self._validate_result(result)
        result['validation'] = validation

        # Log quality metrics
        if validation['passed']:
            self.logger.info(f"✅ {url}: {validation['quality_level']} quality ({validation.get('total_chars', 0):,} chars)")
        else:
            self.logger.warning(f"⚠️  {url}: Validation issues - {', '.join(validation.get('issues', []))}")

        return result

    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate scraping result quality.

        Returns validation report with quality level.
        """
        validation = {
            'passed': False,
            'quality_level': 'poor',
            'issues': []
        }

        if not result.get('success'):
            validation['issues'].append('Scraping failed')
            return validation

        # Get total content
        if result['strategy'] == 'extract':
            total_chars = sum(len(str(v)) for v in result.get('data', {}).values())
        else:
            total_chars = result.get('total_chars', 0)

        validation['total_chars'] = total_chars

        # Quality thresholds
        if total_chars < 1000:
            validation['issues'].append('Low content (<1000 chars)')
            validation['quality_level'] = 'poor'
        elif total_chars < 5000:
            validation['quality_level'] = 'fair'
            validation['passed'] = True
        elif total_chars < 20000:
            validation['quality_level'] = 'good'
            validation['passed'] = True
        else:
            validation['quality_level'] = 'excellent'
            validation['passed'] = True

        # Check for data presence
        if result['strategy'] in ['crawl', 'map']:
            pages = result.get('data', [])
            urls_discovered = result.get('urls_discovered', 0)

            # Allow single-page URLs (0 pages discovered is valid for single articles)
            # Only fail if both conditions are true:
            # 1. No pages scraped AND
            # 2. No content extracted (total_chars < 1000)
            if len(pages) == 0 and total_chars < 1000:
                validation['issues'].append('No pages scraped and no content extracted')
                validation['passed'] = False
            elif len(pages) == 0 and urls_discovered == 0 and total_chars > 0:
                # Single-page URL with content - this is valid
                validation['issues'].append('Single-page URL (no sub-pages discovered)')
                # Don't mark as failed - single pages are valid use cases

        elif result['strategy'] == 'extract':
            extracted_fields = result.get('extracted_fields', 0)
            if extracted_fields == 0 and total_chars < 500:
                validation['issues'].append('No fields extracted and minimal content')
                validation['passed'] = False

        return validation

    async def scrape_batch(self, sources: List[Dict[str, Any]], run_name: str = None) -> Dict[str, Any]:
        """
        Scrape multiple sources with checkpoint recovery.

        Args:
            sources: List of source dicts
            run_name: Optional run name for organizing outputs

        Returns:
            Complete run report with statistics
        """
        run_name = run_name or f"scraping-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        run_dir = self.output_dir / run_name
        run_dir.mkdir(exist_ok=True)

        results_dir = run_dir / 'results'
        results_dir.mkdir(exist_ok=True)

        self.logger.info(f"🚀 Starting scraping run: {run_name}")
        self.logger.info(f"📊 Total sources: {len(sources)}")

        # Load checkpoint if exists
        checkpoint_file = self.checkpoint_dir / f"{run_name}.json"
        processed_urls = set()

        if checkpoint_file.exists():
            with open(checkpoint_file) as f:
                checkpoint = json.load(f)
                processed_urls = set(checkpoint.get('processed_urls', []))
                self.logger.info(f"🔄 Resuming from checkpoint: {len(processed_urls)} sources already processed")

        # Track statistics
        stats = {
            'total_sources': len(sources),
            'processed': len(processed_urls),
            'successful': 0,
            'failed': 0,
            'total_credits': 0,
            'total_chars': 0,
            'strategy_usage': {'crawl': 0, 'extract': 0, 'map': 0},
            'quality_distribution': {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        }

        # Process sources
        for idx, source in enumerate(sources, 1):
            url = source['url']

            # Skip if already processed
            if url in processed_urls:
                continue

            self.logger.info(f"\n[{idx}/{len(sources)}] Processing: {source.get('name', url)}")

            try:
                # Scrape source
                result = await self.scrape_source(source)

                # Update stats
                stats['processed'] += 1
                stats['strategy_usage'][result['strategy']] += 1

                if result.get('success'):
                    stats['successful'] += 1
                    stats['total_credits'] += result.get('credits_used', 0)
                    stats['total_chars'] += result['validation'].get('total_chars', 0)

                    quality_level = result['validation'].get('quality_level', 'poor')
                    stats['quality_distribution'][quality_level] += 1
                else:
                    stats['failed'] += 1

                # Save result
                result_file = results_dir / f"{self._sanitize_filename(url)}.json"
                with open(result_file, 'w') as f:
                    json.dump(result, f, indent=2)

                # Update checkpoint
                processed_urls.add(url)
                self._save_checkpoint(checkpoint_file, processed_urls, stats)

                # Rate limiting (be respectful)
                await asyncio.sleep(2)

            except Exception as e:
                self.logger.error(f"❌ Error processing {url}: {e}")
                stats['failed'] += 1

        # Generate final report
        report = {
            'run_name': run_name,
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'output_directory': str(run_dir)
        }

        report_file = run_dir / 'run-report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"\n✅ Scraping run complete!")
        self.logger.info(f"📊 Statistics:")
        self.logger.info(f"   Total sources: {stats['total_sources']}")
        self.logger.info(f"   Successful: {stats['successful']}")
        self.logger.info(f"   Failed: {stats['failed']}")
        self.logger.info(f"   Total credits: {stats['total_credits']}")
        self.logger.info(f"   Total content: {stats['total_chars']:,} characters")
        self.logger.info(f"   Strategy usage: {stats['strategy_usage']}")
        self.logger.info(f"   Quality distribution: {stats['quality_distribution']}")

        return report

    def _save_checkpoint(self, checkpoint_file: Path, processed_urls: set, stats: Dict):
        """Save checkpoint for recovery"""
        with open(checkpoint_file, 'w') as f:
            json.dump({
                'processed_urls': list(processed_urls),
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

    def _sanitize_filename(self, url: str) -> str:
        """Convert URL to safe filename"""
        return hashlib.sha256(url.encode()).hexdigest()[:16]


async def main():
    """Example usage of Universal Scraper"""
    import os

    # Initialize scraper
    api_key = os.getenv('FIRECRAWL_API_KEY')
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")

    scraper = UniversalScraper(api_key)

    # Example sources with different strategies
    sources = [
        {
            'name': 'Bricks Academy Documentation',
            'url': 'https://academy.bricksbuilder.io/',
            'category': 'documentation',
            'strategy': 'crawl',  # Override auto-detection
            'max_pages': 50
        },
        {
            'name': 'Awwwards Site of the Day',
            'url': 'https://www.awwwards.com/websites/site-of-the-day/',
            'category': 'award-winning-designs',
            'strategy': 'extract',  # Structured extraction
            'schema': {
                'type': 'object',
                'properties': {
                    'site_name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'design_elements': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        },
        {
            'name': 'GSAP Documentation',
            'url': 'https://gsap.com/docs/v3/',
            'category': 'gsap-animations',
            # No strategy specified - will auto-detect as 'crawl'
            'max_pages': 30
        }
    ]

    # Run scraper
    report = await scraper.scrape_batch(sources, run_name='example-scraping-run')

    print("\n" + "="*70)
    print("✅ Scraping Complete!")
    print(f"📂 Results saved to: {report['output_directory']}")
    print("="*70)


if __name__ == '__main__':
    asyncio.run(main())
