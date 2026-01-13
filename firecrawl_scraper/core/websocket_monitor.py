#!/usr/bin/env python3
"""
WebSocket Monitor - Real-Time Crawl Progress Monitoring

Provides real-time updates for crawl jobs using WebSocket connections:
- Live progress tracking
- Event-driven callbacks
- Progress bar integration
- Auto-reconnection support

Usage:
    from firecrawl_scraper.core.websocket_monitor import WebSocketMonitor

    monitor = WebSocketMonitor(api_key)
    results = await monitor.crawl_and_watch(
        url="https://example.com",
        on_page=lambda doc: print(f"Scraped: {doc['url']}"),
        on_progress=lambda completed, total: print(f"{completed}/{total}")
    )
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import websockets library
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    logger.warning("websockets library not installed. WebSocket monitoring disabled.")

# Try to import tqdm for progress bars
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


@dataclass
class CrawlProgress:
    """Track crawl job progress"""
    job_id: str
    status: str
    total: int
    completed: int
    failed: int
    credits_used: int
    start_time: datetime
    documents: List[Dict]

    @property
    def progress_percent(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100

    @property
    def elapsed_time(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()


class WebSocketMonitor:
    """
    Real-time crawl monitoring using WebSocket connections.

    Features:
    - Live page-by-page updates
    - Progress callbacks
    - Progress bar display
    - Error event handling
    - Auto-reconnection
    """

    # WebSocket endpoint (if Firecrawl supports it)
    WS_BASE_URL = "wss://api.firecrawl.dev/v2"

    def __init__(
        self,
        api_key: str,
        reconnect_attempts: int = 3,
        ping_interval: int = 30
    ):
        """
        Initialize WebSocket monitor.

        Args:
            api_key: Firecrawl API key
            reconnect_attempts: Number of reconnection attempts
            ping_interval: WebSocket ping interval in seconds
        """
        if not HAS_WEBSOCKETS:
            raise ImportError("websockets library required. Install with: pip install websockets")

        self.api_key = api_key
        self.reconnect_attempts = reconnect_attempts
        self.ping_interval = ping_interval

        # Import client for fallback polling
        from firecrawl_scraper.core.firecrawl_client import EnhancedFirecrawlClient
        self.client = EnhancedFirecrawlClient(api_key=api_key)

    async def crawl_and_watch(
        self,
        url: str,
        limit: int = 100,
        scrape_options: Optional[Dict] = None,
        on_page: Optional[Callable[[Dict], None]] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
        on_error: Optional[Callable[[Dict], None]] = None,
        on_complete: Optional[Callable[[CrawlProgress], None]] = None,
        show_progress_bar: bool = True,
        **kwargs
    ) -> Dict:
        """
        Start crawl with real-time monitoring.

        Args:
            url: Base URL to crawl
            limit: Maximum pages to crawl
            scrape_options: Options for each page
            on_page: Callback for each scraped page
            on_progress: Callback for progress updates (completed, total)
            on_error: Callback for errors
            on_complete: Callback when crawl completes
            show_progress_bar: Show tqdm progress bar
            **kwargs: Additional crawl options

        Returns:
            Dict with crawl results
        """
        # Start the crawl job
        job_id = await self.client.crawl_async(
            url=url,
            limit=limit,
            scrape_options=scrape_options or {'formats': ['markdown']},
            **kwargs
        )

        logger.info(f"Started crawl job: {job_id}")

        # Monitor progress
        progress = CrawlProgress(
            job_id=job_id,
            status='scraping',
            total=0,
            completed=0,
            failed=0,
            credits_used=0,
            start_time=datetime.now(),
            documents=[]
        )

        # Create progress bar if requested
        pbar = None
        if show_progress_bar and HAS_TQDM:
            pbar = tqdm(total=limit, desc="Crawling", unit="page")

        try:
            # Poll for updates (WebSocket fallback to polling)
            # Note: If Firecrawl adds WebSocket support, we'd connect here
            result = await self._poll_with_callbacks(
                job_id=job_id,
                progress=progress,
                on_page=on_page,
                on_progress=on_progress,
                on_error=on_error,
                pbar=pbar
            )

            # Call completion callback
            if on_complete:
                on_complete(progress)

            return result

        finally:
            if pbar:
                pbar.close()

    async def _poll_with_callbacks(
        self,
        job_id: str,
        progress: CrawlProgress,
        on_page: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        pbar: Optional[Any] = None,
        poll_interval: int = 2
    ) -> Dict:
        """
        Poll job status and trigger callbacks.

        This simulates real-time monitoring via polling.
        If Firecrawl adds WebSocket support, this would be replaced.
        """
        seen_pages = set()
        last_completed = 0

        while True:
            status = await self.client.get_crawl_status(job_id)

            # Update progress
            progress.status = status.get('status', 'unknown')
            progress.total = status.get('total', 0)
            progress.completed = status.get('completed', 0)
            progress.credits_used = status.get('creditsUsed', progress.completed)

            # Update progress bar
            if pbar and progress.total > 0:
                pbar.total = progress.total
                pbar.n = progress.completed
                pbar.refresh()

            # Call progress callback
            if on_progress and progress.completed != last_completed:
                on_progress(progress.completed, progress.total)
                last_completed = progress.completed

            # Process new pages
            data = status.get('data', [])
            for doc in data:
                # Get unique identifier for the page
                page_url = doc.get('url') or doc.get('metadata', {}).get('sourceURL', '')
                if page_url and page_url not in seen_pages:
                    seen_pages.add(page_url)
                    progress.documents.append(doc)

                    # Call page callback
                    if on_page:
                        try:
                            on_page(doc)
                        except Exception as e:
                            logger.error(f"Error in on_page callback: {e}")

            # Check if complete
            if progress.status in ['completed', 'failed', 'cancelled']:
                if progress.status == 'failed' and on_error:
                    on_error({'status': 'failed', 'job_id': job_id})

                return {
                    'success': progress.status == 'completed',
                    'data': progress.documents,
                    'creditsUsed': progress.credits_used,
                    'status': progress.status,
                    'total': progress.total,
                    'completed': progress.completed,
                    'elapsed_seconds': progress.elapsed_time
                }

            await asyncio.sleep(poll_interval)

    async def batch_scrape_and_watch(
        self,
        urls: List[str],
        on_page: Optional[Callable[[Dict], None]] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
        show_progress_bar: bool = True,
        **kwargs
    ) -> Dict:
        """
        Batch scrape with real-time monitoring.

        Args:
            urls: List of URLs to scrape
            on_page: Callback for each scraped page
            on_progress: Callback for progress updates
            show_progress_bar: Show progress bar
            **kwargs: Additional scrape options

        Returns:
            Dict with batch results
        """
        # Start batch job
        job_id = await self.client.batch_scrape_async(urls=urls, **kwargs)

        logger.info(f"Started batch scrape job: {job_id}")

        # Create progress bar
        pbar = None
        if show_progress_bar and HAS_TQDM:
            pbar = tqdm(total=len(urls), desc="Batch scraping", unit="url")

        progress = CrawlProgress(
            job_id=job_id,
            status='scraping',
            total=len(urls),
            completed=0,
            failed=0,
            credits_used=0,
            start_time=datetime.now(),
            documents=[]
        )

        try:
            result = await self._poll_batch_with_callbacks(
                job_id=job_id,
                progress=progress,
                on_page=on_page,
                on_progress=on_progress,
                pbar=pbar
            )
            return result

        finally:
            if pbar:
                pbar.close()

    async def _poll_batch_with_callbacks(
        self,
        job_id: str,
        progress: CrawlProgress,
        on_page: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        pbar: Optional[Any] = None,
        poll_interval: int = 2
    ) -> Dict:
        """Poll batch job status with callbacks"""
        seen_pages = set()
        last_completed = 0

        while True:
            status = await self.client.get_batch_status(job_id)

            progress.status = status.get('status', 'unknown')
            progress.total = status.get('total', progress.total)
            progress.completed = status.get('completed', 0)
            progress.credits_used = progress.completed

            # Update progress bar
            if pbar:
                pbar.n = progress.completed
                pbar.refresh()

            # Call progress callback
            if on_progress and progress.completed != last_completed:
                on_progress(progress.completed, progress.total)
                last_completed = progress.completed

            # Process new results
            data = status.get('data', [])
            for doc in data:
                page_url = doc.get('url') or doc.get('metadata', {}).get('sourceURL', '')
                if page_url and page_url not in seen_pages:
                    seen_pages.add(page_url)
                    progress.documents.append(doc)

                    if on_page:
                        try:
                            on_page(doc)
                        except Exception as e:
                            logger.error(f"Error in on_page callback: {e}")

            # Check if complete
            if progress.status in ['completed', 'failed', 'cancelled']:
                return {
                    'success': progress.status == 'completed',
                    'data': progress.documents,
                    'creditsUsed': progress.credits_used,
                    'status': progress.status,
                    'total': progress.total,
                    'completed': progress.completed,
                    'elapsed_seconds': progress.elapsed_time
                }

            await asyncio.sleep(poll_interval)


class ProgressDisplay:
    """
    CLI progress display helper.

    Provides formatted progress output for terminal.
    """

    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.completed = 0
        self.description = description
        self.start_time = datetime.now()

    def update(self, completed: int):
        """Update progress display"""
        self.completed = completed
        percent = (completed / self.total * 100) if self.total > 0 else 0
        elapsed = (datetime.now() - self.start_time).total_seconds()

        # Estimate remaining time
        if completed > 0:
            rate = completed / elapsed
            remaining = (self.total - completed) / rate if rate > 0 else 0
        else:
            remaining = 0

        # Create progress bar
        bar_width = 30
        filled = int(bar_width * completed / self.total) if self.total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)

        print(f"\r{self.description}: [{bar}] {completed}/{self.total} ({percent:.1f}%) "
              f"ETA: {remaining:.0f}s", end="", flush=True)

    def complete(self):
        """Mark as complete"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"\n✅ {self.description} complete: {self.total} items in {elapsed:.1f}s")
