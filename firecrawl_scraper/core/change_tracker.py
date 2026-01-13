#!/usr/bin/env python3
"""
Change Tracker - Website Content Monitoring System

Track changes to websites over time with:
- Content hash comparison for change detection
- Diff generation for modified content
- Change history persistence
- Webhook/email notifications
- Scheduled monitoring support

Usage:
    from firecrawl_scraper.core.change_tracker import ChangeTracker

    tracker = ChangeTracker(api_key)
    tracker.track_url("https://example.com/docs/")
    changes = await tracker.check_all_tracked()
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

# Try to import diff library
try:
    from diff_match_patch import diff_match_patch
    HAS_DIFF_LIB = True
except ImportError:
    HAS_DIFF_LIB = False
    logger.warning("diff-match-patch not installed. Diff generation disabled.")


@dataclass
class ContentSnapshot:
    """Snapshot of URL content at a point in time"""
    url: str
    content_hash: str
    content_length: int
    timestamp: str
    markdown_preview: str = ""  # First 500 chars

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ChangeRecord:
    """Record of a detected change"""
    url: str
    detected_at: str
    previous_hash: str
    current_hash: str
    content_length_change: int
    diff_summary: str = ""
    full_diff: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TrackedURL:
    """Configuration for a tracked URL"""
    url: str
    check_interval: int = 86400  # Default 24 hours
    last_checked: Optional[str] = None
    last_hash: Optional[str] = None
    last_content_length: int = 0
    change_count: int = 0
    snapshots: List[Dict] = field(default_factory=list)
    changes: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


class ChangeTracker:
    """
    Website change tracking system.

    Features:
    - Track content changes for multiple URLs
    - Generate diffs showing what changed
    - Persist change history to disk
    - Support for notifications via webhook
    - Scheduled monitoring support
    """

    def __init__(
        self,
        api_key: str,
        storage_dir: Optional[Path] = None,
        on_change: Optional[Callable[[ChangeRecord], None]] = None
    ):
        """
        Initialize change tracker.

        Args:
            api_key: Firecrawl API key
            storage_dir: Directory for persisting tracking data
            on_change: Callback function when changes are detected
        """
        # Import here to avoid circular imports
        from firecrawl_scraper.core.firecrawl_client import EnhancedFirecrawlClient
        from firecrawl_scraper.config import Config

        self.client = EnhancedFirecrawlClient(api_key=api_key)
        self.storage_dir = storage_dir or Config.CHANGE_TRACKING_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.on_change = on_change
        self.tracked_urls: Dict[str, TrackedURL] = {}

        # Load existing tracking data
        self._load_tracking_data()

        # Diff generator
        if HAS_DIFF_LIB:
            self.differ = diff_match_patch()

    def _url_hash(self, url: str) -> str:
        """Generate hash for URL (used as filename)"""
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _get_storage_path(self, url: str) -> Path:
        """Get storage path for URL tracking data"""
        return self.storage_dir / f"{self._url_hash(url)}.json"

    def _load_tracking_data(self):
        """Load existing tracking data from disk"""
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    if 'url' in data:
                        self.tracked_urls[data['url']] = TrackedURL(**data)
            except Exception as e:
                logger.warning(f"Failed to load tracking data from {file_path}: {e}")

    def _save_tracking_data(self, url: str):
        """Save tracking data for URL to disk"""
        if url not in self.tracked_urls:
            return

        tracked = self.tracked_urls[url]
        file_path = self._get_storage_path(url)

        with open(file_path, 'w') as f:
            json.dump(tracked.to_dict(), f, indent=2)

    def track_url(
        self,
        url: str,
        check_interval: int = 86400
    ) -> TrackedURL:
        """
        Add URL to tracking list.

        Args:
            url: URL to track for changes
            check_interval: Check interval in seconds (default: 24h)

        Returns:
            TrackedURL configuration object
        """
        if url not in self.tracked_urls:
            self.tracked_urls[url] = TrackedURL(
                url=url,
                check_interval=check_interval
            )
            self._save_tracking_data(url)
            logger.info(f"Now tracking: {url}")
        else:
            logger.info(f"Already tracking: {url}")

        return self.tracked_urls[url]

    def untrack_url(self, url: str) -> bool:
        """
        Remove URL from tracking list.

        Args:
            url: URL to stop tracking

        Returns:
            True if URL was being tracked
        """
        if url in self.tracked_urls:
            del self.tracked_urls[url]
            file_path = self._get_storage_path(url)
            if file_path.exists():
                file_path.unlink()
            logger.info(f"Stopped tracking: {url}")
            return True
        return False

    def get_tracked_urls(self) -> List[str]:
        """Get list of all tracked URLs"""
        return list(self.tracked_urls.keys())

    async def check_url(
        self,
        url: str,
        force: bool = False
    ) -> Optional[ChangeRecord]:
        """
        Check a URL for changes.

        Args:
            url: URL to check
            force: Check even if interval hasn't passed

        Returns:
            ChangeRecord if changes detected, None otherwise
        """
        if url not in self.tracked_urls:
            self.track_url(url)

        tracked = self.tracked_urls[url]

        # Check if enough time has passed
        if not force and tracked.last_checked:
            last_check = datetime.fromisoformat(tracked.last_checked)
            elapsed = (datetime.now() - last_check).total_seconds()
            if elapsed < tracked.check_interval:
                logger.debug(f"Skipping {url} - checked {elapsed:.0f}s ago")
                return None

        # Scrape current content
        logger.info(f"Checking for changes: {url}")
        result = await self.client.scrape(url=url, formats=['markdown'])

        if not result.get('success'):
            logger.error(f"Failed to scrape {url}: {result.get('error')}")
            return None

        # Extract content
        data = result.get('data', {})
        if isinstance(data, dict):
            content = data.get('markdown', '')
        else:
            content = str(data)

        # Compute hash
        current_hash = hashlib.sha256(content.encode()).hexdigest()
        current_length = len(content)
        now = datetime.now().isoformat()

        # Create snapshot
        snapshot = ContentSnapshot(
            url=url,
            content_hash=current_hash,
            content_length=current_length,
            timestamp=now,
            markdown_preview=content[:500]
        )

        # Check for changes
        change_record = None
        if tracked.last_hash and tracked.last_hash != current_hash:
            # Change detected!
            length_change = current_length - tracked.last_content_length

            # Generate diff summary
            diff_summary = f"Content length changed by {length_change:+d} characters"

            # Generate full diff if library available and we have previous content
            full_diff = ""
            if HAS_DIFF_LIB and tracked.snapshots:
                try:
                    prev_content = tracked.snapshots[-1].get('markdown_preview', '')
                    diffs = self.differ.diff_main(prev_content, snapshot.markdown_preview)
                    self.differ.diff_cleanupSemantic(diffs)
                    full_diff = self.differ.diff_prettyHtml(diffs)
                except Exception as e:
                    logger.warning(f"Failed to generate diff: {e}")

            change_record = ChangeRecord(
                url=url,
                detected_at=now,
                previous_hash=tracked.last_hash,
                current_hash=current_hash,
                content_length_change=length_change,
                diff_summary=diff_summary,
                full_diff=full_diff
            )

            # Store change record
            tracked.changes.append(change_record.to_dict())
            tracked.change_count += 1

            logger.info(f"Change detected at {url}: {diff_summary}")

            # Call callback
            if self.on_change:
                self.on_change(change_record)

        # Update tracking data
        tracked.last_checked = now
        tracked.last_hash = current_hash
        tracked.last_content_length = current_length

        # Store snapshot (keep last 10)
        tracked.snapshots.append(snapshot.to_dict())
        if len(tracked.snapshots) > 10:
            tracked.snapshots = tracked.snapshots[-10:]

        # Persist to disk
        self._save_tracking_data(url)

        return change_record

    async def check_all_tracked(
        self,
        force: bool = False
    ) -> List[ChangeRecord]:
        """
        Check all tracked URLs for changes.

        Args:
            force: Check all URLs regardless of interval

        Returns:
            List of detected changes
        """
        changes = []

        for url in self.tracked_urls.keys():
            try:
                change = await self.check_url(url, force=force)
                if change:
                    changes.append(change)
            except Exception as e:
                logger.error(f"Error checking {url}: {e}")

        logger.info(f"Checked {len(self.tracked_urls)} URLs, found {len(changes)} changes")
        return changes

    def get_change_history(
        self,
        url: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get change history for a URL.

        Args:
            url: URL to get history for
            limit: Maximum number of changes to return

        Returns:
            List of change records (newest first)
        """
        if url not in self.tracked_urls:
            return []

        changes = self.tracked_urls[url].changes
        return list(reversed(changes[-limit:]))

    def get_snapshots(
        self,
        url: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get content snapshots for a URL.

        Args:
            url: URL to get snapshots for
            limit: Maximum number of snapshots to return

        Returns:
            List of snapshots (newest first)
        """
        if url not in self.tracked_urls:
            return []

        snapshots = self.tracked_urls[url].snapshots
        return list(reversed(snapshots[-limit:]))

    def get_tracking_stats(self) -> Dict:
        """Get statistics about tracked URLs"""
        total_changes = sum(t.change_count for t in self.tracked_urls.values())
        urls_with_changes = sum(1 for t in self.tracked_urls.values() if t.change_count > 0)

        return {
            'total_tracked': len(self.tracked_urls),
            'total_changes_detected': total_changes,
            'urls_with_changes': urls_with_changes,
            'tracked_urls': [
                {
                    'url': t.url,
                    'last_checked': t.last_checked,
                    'change_count': t.change_count
                }
                for t in self.tracked_urls.values()
            ]
        }

    async def monitor_continuously(
        self,
        interval: int = 3600,
        max_iterations: Optional[int] = None
    ):
        """
        Continuously monitor tracked URLs.

        Args:
            interval: Check interval in seconds
            max_iterations: Maximum number of check cycles (None = infinite)
        """
        iteration = 0

        while max_iterations is None or iteration < max_iterations:
            logger.info(f"Starting monitoring cycle {iteration + 1}")

            changes = await self.check_all_tracked()

            if changes:
                logger.info(f"Detected {len(changes)} changes in cycle {iteration + 1}")

            iteration += 1

            if max_iterations is None or iteration < max_iterations:
                logger.info(f"Next check in {interval} seconds")
                await asyncio.sleep(interval)

        logger.info("Monitoring complete")
