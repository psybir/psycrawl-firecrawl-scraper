"""
Centralized Configuration for Firecrawl Scraper v2.0

This module manages all environment variables and configuration settings
for the Firecrawl scraping system with API v2 support.

Features:
- Batch scraping configuration
- Actions support settings
- Change tracking options
- WebSocket monitoring config
- Media extraction settings

Usage:
    from firecrawl_scraper.config import Config

    # Access configuration
    api_key = Config.API_KEY
    output_dir = Config.OUTPUT_DIR
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env and .env.local files
# .env.local takes precedence for local development
BASE_DIR = Path(__file__).parent.parent.resolve()
load_dotenv(BASE_DIR / '.env')  # Load .env first
load_dotenv(BASE_DIR / '.env.local', override=True)  # .env.local overrides


class Config:
    """
    Centralized configuration class for Firecrawl Scraper v2.0.

    All settings are loaded from environment variables with sensible defaults.
    """

    # ========== Directory Configuration ==========
    BASE_DIR = Path(__file__).parent.parent.resolve()
    OUTPUT_DIR = Path(os.getenv('FIRECRAWL_OUTPUT_DIR', BASE_DIR / 'data')).resolve()
    CHECKPOINT_DIR = OUTPUT_DIR / '_checkpoints'
    CHANGE_TRACKING_DIR = OUTPUT_DIR / '_change_tracking'

    # ========== API Configuration ==========
    API_KEY = os.getenv('FIRECRAWL_API_KEY')
    BACKUP_KEY = os.getenv('FIRECRAWL_BACKUP_KEY')

    # API Version (v2 is default)
    API_VERSION = os.getenv('FIRECRAWL_API_VERSION', 'v2')
    API_BASE_URL = f"https://api.firecrawl.dev/{API_VERSION}"

    # Validate API key exists
    if not API_KEY:
        raise ValueError(
            "FIRECRAWL_API_KEY not found in environment variables. "
            "Please copy .env.example to .env and add your API key."
        )

    # ========== Proxy Configuration ==========
    PROXY_TYPE = os.getenv('FIRECRAWL_PROXY_TYPE', 'auto')
    LOCATIONS = os.getenv('FIRECRAWL_LOCATIONS', 'US,DE,GB,AU,FR').split(',')

    # Validate proxy type
    VALID_PROXY_TYPES = ['auto', 'basic', 'stealth']
    if PROXY_TYPE not in VALID_PROXY_TYPES:
        raise ValueError(
            f"Invalid FIRECRAWL_PROXY_TYPE: {PROXY_TYPE}. "
            f"Must be one of: {', '.join(VALID_PROXY_TYPES)}"
        )

    # ========== Retry Configuration ==========
    MAX_RETRIES = int(os.getenv('FIRECRAWL_MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('FIRECRAWL_RETRY_DELAY', '2000'))  # milliseconds

    # Validate retry settings
    if MAX_RETRIES < 0 or MAX_RETRIES > 10:
        raise ValueError(f"MAX_RETRIES must be between 0-10, got: {MAX_RETRIES}")

    if RETRY_DELAY < 0 or RETRY_DELAY > 10000:
        raise ValueError(f"RETRY_DELAY must be between 0-10000ms, got: {RETRY_DELAY}")

    # ========== Logging Configuration ==========
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Validate log level
    VALID_LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if LOG_LEVEL not in VALID_LOG_LEVELS:
        raise ValueError(
            f"Invalid LOG_LEVEL: {LOG_LEVEL}. "
            f"Must be one of: {', '.join(VALID_LOG_LEVELS)}"
        )

    # ========== Quality Validation Thresholds ==========
    MIN_CONTENT_LENGTH = int(os.getenv('MIN_CONTENT_LENGTH', '1000'))  # characters
    DUPLICATE_THRESHOLD = float(os.getenv('DUPLICATE_THRESHOLD', '0.95'))  # similarity

    # ========== Performance Settings ==========
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))  # seconds

    # ========== Default Scraping Options ==========
    DEFAULT_STRATEGY = os.getenv('DEFAULT_STRATEGY', 'map')
    DEFAULT_MAX_PAGES = int(os.getenv('DEFAULT_MAX_PAGES', '50'))
    DEFAULT_USE_STEALTH = os.getenv('DEFAULT_USE_STEALTH', 'false').lower() == 'true'

    # ========== Batch Scraping Configuration (NEW) ==========
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', '1000'))
    BATCH_POLL_INTERVAL = int(os.getenv('BATCH_POLL_INTERVAL', '5'))  # seconds
    BATCH_MAX_CONCURRENT = int(os.getenv('BATCH_MAX_CONCURRENT', '100'))

    # ========== Actions Configuration (NEW) ==========
    DEFAULT_WAIT_TIMEOUT = int(os.getenv('DEFAULT_WAIT_TIMEOUT', '30000'))  # ms
    DEFAULT_SCROLL_AMOUNT = int(os.getenv('DEFAULT_SCROLL_AMOUNT', '1000'))  # pixels
    ENABLE_SCREENSHOTS = os.getenv('ENABLE_SCREENSHOTS', 'false').lower() == 'true'
    ENABLE_MOBILE_EMULATION = os.getenv('ENABLE_MOBILE_EMULATION', 'false').lower() == 'true'

    # ========== Change Tracking Configuration (NEW) ==========
    CHANGE_TRACKING_ENABLED = os.getenv('CHANGE_TRACKING_ENABLED', 'false').lower() == 'true'
    CHANGE_TRACKING_INTERVAL = int(os.getenv('CHANGE_TRACKING_INTERVAL', '86400'))  # 24h in seconds
    CHANGE_TRACKING_NOTIFY_EMAIL = os.getenv('CHANGE_TRACKING_NOTIFY_EMAIL', '')
    CHANGE_TRACKING_WEBHOOK = os.getenv('CHANGE_TRACKING_WEBHOOK', '')

    # ========== WebSocket Configuration (NEW) ==========
    WEBSOCKET_ENABLED = os.getenv('WEBSOCKET_ENABLED', 'true').lower() == 'true'
    WEBSOCKET_RECONNECT_ATTEMPTS = int(os.getenv('WEBSOCKET_RECONNECT_ATTEMPTS', '3'))
    WEBSOCKET_PING_INTERVAL = int(os.getenv('WEBSOCKET_PING_INTERVAL', '30'))  # seconds

    # ========== Media Extraction Configuration (NEW) ==========
    MEDIA_EXTRACTION_ENABLED = os.getenv('MEDIA_EXTRACTION_ENABLED', 'false').lower() == 'true'
    PDF_EXTRACTION_ENABLED = os.getenv('PDF_EXTRACTION_ENABLED', 'false').lower() == 'true'
    DOCX_EXTRACTION_ENABLED = os.getenv('DOCX_EXTRACTION_ENABLED', 'false').lower() == 'true'
    IMAGE_OCR_ENABLED = os.getenv('IMAGE_OCR_ENABLED', 'false').lower() == 'true'
    MAX_MEDIA_SIZE_MB = int(os.getenv('MAX_MEDIA_SIZE_MB', '50'))

    # ========== LLM Extraction Configuration (Spark 1 Pro - Quality First) ==========
    # IMPORTANT: Always use Spark 1 Pro for maximum extraction quality
    # Available models: spark-1 (fast), spark-1-pro (quality), gpt-4o-mini
    LLM_EXTRACTION_MODEL = os.getenv('LLM_EXTRACTION_MODEL', 'spark-1-pro')
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '8192'))

    # Spark 1 Pro Configuration
    FIRECRAWL_LLM_MODEL = os.getenv('FIRECRAWL_LLM_MODEL', 'spark-1-pro')  # Always Pro
    SPARK_PRO_ENABLED = os.getenv('SPARK_PRO_ENABLED', 'true').lower() == 'true'

    # v2.7 Features Configuration
    FAST_MAPPING_ENABLED = os.getenv('FAST_MAPPING_ENABLED', 'true').lower() == 'true'  # 15x faster
    FAST_MAPPING_LIMIT = int(os.getenv('FAST_MAPPING_LIMIT', '100000'))  # 100k URL limit
    YOUTUBE_TRANSCRIPT_ENABLED = os.getenv('YOUTUBE_TRANSCRIPT_ENABLED', 'true').lower() == 'true'
    EXCEL_SCRAPING_ENABLED = os.getenv('EXCEL_SCRAPING_ENABLED', 'true').lower() == 'true'

    # Lead Generation Configuration
    LEAD_GEN_ENABLED = os.getenv('LEAD_GEN_ENABLED', 'true').lower() == 'true'
    LEAD_EXTRACTION_MODEL = os.getenv('LEAD_EXTRACTION_MODEL', 'spark-1-pro')  # Always Pro for leads
    LEAD_OUTPUT_DIR = Path(os.getenv('LEAD_OUTPUT_DIR', OUTPUT_DIR / 'leads')).resolve()

    # Credit Usage Strategy (burn those 93.5k credits!)
    CREDITS_MONTHLY_LIMIT = int(os.getenv('CREDITS_MONTHLY_LIMIT', '100000'))
    CREDITS_USED = int(os.getenv('CREDITS_USED', '6500'))
    CREDITS_AVAILABLE = CREDITS_MONTHLY_LIMIT - CREDITS_USED  # ~93,500
    DAILY_CREDIT_TARGET = int(os.getenv('DAILY_CREDIT_TARGET', '3100'))  # Use 93.5k in 30 days

    # ========== Skills System Configuration (Psybir Evidence Engine) ==========
    SKILLS_ENABLED = os.getenv('SKILLS_ENABLED', 'true').lower() == 'true'
    SKILLS_DIR = Path(os.getenv('SKILLS_DIR', Path(__file__).parent / 'skills')).resolve()
    SKILLS_CONTEXT_FILE = Path(os.getenv('SKILLS_CONTEXT_FILE', '.psycrawl/product-context.md'))
    SKILLS_DATA_DIR = Path(os.getenv('SKILLS_DATA_DIR', '.psycrawl/data'))
    SKILLS_OUTPUT_DIR = Path(os.getenv('SKILLS_OUTPUT_DIR', OUTPUT_DIR / 'skills')).resolve()

    # Psybir Geo-Tagging Defaults
    DEFAULT_GEO_SCOPE = os.getenv('DEFAULT_GEO_SCOPE', 'local_radius')  # local_radius | multi_location | domestic
    DEFAULT_GEO_BUCKET = os.getenv('DEFAULT_GEO_BUCKET', '0-10')  # 0-10 | 10-30 | 30-60 | 60-90 | 90+
    DEFAULT_LOCATION_CLUSTER = os.getenv('DEFAULT_LOCATION_CLUSTER', '')  # e.g., "Pittsburgh Metro"

    # Skills Caching
    SKILLS_CACHE_ENABLED = os.getenv('SKILLS_CACHE_ENABLED', 'true').lower() == 'true'
    SKILLS_CACHE_MAX_AGE_DAYS = int(os.getenv('SKILLS_CACHE_MAX_AGE_DAYS', '7'))

    # NL Routing
    SKILLS_NL_ROUTING_ENABLED = os.getenv('SKILLS_NL_ROUTING_ENABLED', 'true').lower() == 'true'
    SKILLS_MIN_CONFIDENCE = float(os.getenv('SKILLS_MIN_CONFIDENCE', '0.3'))  # Minimum routing confidence

    # ========== DataForSEO Configuration (NEW) ==========
    DATAFORSEO_LOGIN = os.getenv('DATAFORSEO_LOGIN')
    DATAFORSEO_PASSWORD = os.getenv('DATAFORSEO_PASSWORD')
    DATAFORSEO_ENABLED = os.getenv('DATAFORSEO_ENABLED', 'false').lower() == 'true'

    # DataForSEO Module Toggles
    SEO_SERP_ENABLED = os.getenv('SEO_SERP_ENABLED', 'true').lower() == 'true'
    SEO_KEYWORDS_ENABLED = os.getenv('SEO_KEYWORDS_ENABLED', 'true').lower() == 'true'
    SEO_BACKLINKS_ENABLED = os.getenv('SEO_BACKLINKS_ENABLED', 'true').lower() == 'true'
    SEO_ONPAGE_ENABLED = os.getenv('SEO_ONPAGE_ENABLED', 'true').lower() == 'true'
    SEO_LABS_ENABLED = os.getenv('SEO_LABS_ENABLED', 'true').lower() == 'true'

    # DataForSEO Default Settings
    SEO_DEFAULT_LOCATION = os.getenv('SEO_DEFAULT_LOCATION', 'United States')
    SEO_DEFAULT_LOCATION_CODE = int(os.getenv('SEO_DEFAULT_LOCATION_CODE', '2840'))  # US
    SEO_DEFAULT_LANGUAGE = os.getenv('SEO_DEFAULT_LANGUAGE', 'en')
    SEO_DEFAULT_LANGUAGE_CODE = os.getenv('SEO_DEFAULT_LANGUAGE_CODE', 'en')
    SEO_DEFAULT_DEVICE = os.getenv('SEO_DEFAULT_DEVICE', 'desktop')  # desktop, mobile, tablet

    # DataForSEO Rate Limiting
    SEO_MAX_CONCURRENT = int(os.getenv('SEO_MAX_CONCURRENT', '5'))
    SEO_REQUEST_DELAY = float(os.getenv('SEO_REQUEST_DELAY', '0.5'))  # seconds between requests

    # DataForSEO Output
    SEO_OUTPUT_DIR = Path(os.getenv('SEO_OUTPUT_DIR', OUTPUT_DIR / 'seo_reports')).resolve()

    # ========== Helper Methods ==========

    @classmethod
    def ensure_directories(cls):
        """
        Ensure all required directories exist.
        Creates OUTPUT_DIR, CHECKPOINT_DIR, CHANGE_TRACKING_DIR, SEO_OUTPUT_DIR, LEAD_OUTPUT_DIR, and SKILLS_OUTPUT_DIR if they don't exist.
        """
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHANGE_TRACKING_DIR.mkdir(parents=True, exist_ok=True)
        cls.SEO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.LEAD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.SKILLS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_output_path(cls, category: str) -> Path:
        """
        Get the output path for a specific category (source name).

        Args:
            category: Source category/name (e.g., 'bricks-academy')

        Returns:
            Path object for the category output directory
        """
        path = cls.OUTPUT_DIR / category
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_checkpoint_path(cls, run_name: str) -> Path:
        """
        Get the checkpoint file path for a specific run.

        Args:
            run_name: Name of the scraping run

        Returns:
            Path object for the checkpoint file
        """
        cls.CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        return cls.CHECKPOINT_DIR / f"{run_name}-checkpoint.json"

    @classmethod
    def get_change_tracking_path(cls, url_hash: str) -> Path:
        """
        Get the change tracking file path for a URL.

        Args:
            url_hash: Hash of the URL being tracked

        Returns:
            Path object for the change tracking file
        """
        cls.CHANGE_TRACKING_DIR.mkdir(parents=True, exist_ok=True)
        return cls.CHANGE_TRACKING_DIR / f"{url_hash}-history.json"

    @classmethod
    def validate_config(cls):
        """
        Validate all configuration settings.
        Raises ValueError if any settings are invalid.
        """
        # Additional validations for new settings
        if cls.MAX_BATCH_SIZE > 10000:
            raise ValueError(f"MAX_BATCH_SIZE cannot exceed 10000, got: {cls.MAX_BATCH_SIZE}")

        if cls.BATCH_POLL_INTERVAL < 1:
            raise ValueError(f"BATCH_POLL_INTERVAL must be at least 1 second, got: {cls.BATCH_POLL_INTERVAL}")

    @classmethod
    def print_config(cls):
        """
        Print current configuration (for debugging).
        Masks sensitive values like API keys.
        """
        print("\n" + "="*60)
        print("Firecrawl Scraper v2.0 Configuration")
        print("="*60)
        print(f"API Version: {cls.API_VERSION}")
        print(f"API Base URL: {cls.API_BASE_URL}")
        print(f"Output Directory: {cls.OUTPUT_DIR}")
        print(f"Checkpoint Directory: {cls.CHECKPOINT_DIR}")
        print(f"API Key: {'*' * 20}{cls.API_KEY[-8:] if cls.API_KEY else 'NOT SET'}")
        print(f"Proxy Type: {cls.PROXY_TYPE}")
        print(f"Locations: {', '.join(cls.LOCATIONS)}")
        print(f"Max Retries: {cls.MAX_RETRIES}")
        print(f"Retry Delay: {cls.RETRY_DELAY}ms")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print(f"Min Content Length: {cls.MIN_CONTENT_LENGTH} chars")
        print(f"Default Strategy: {cls.DEFAULT_STRATEGY}")
        print(f"Default Max Pages: {cls.DEFAULT_MAX_PAGES}")
        print("-" * 60)
        print("NEW v2.0 Settings:")
        print(f"Max Batch Size: {cls.MAX_BATCH_SIZE}")
        print(f"Batch Poll Interval: {cls.BATCH_POLL_INTERVAL}s")
        print(f"Actions Timeout: {cls.DEFAULT_WAIT_TIMEOUT}ms")
        print(f"Screenshots Enabled: {cls.ENABLE_SCREENSHOTS}")
        print(f"Change Tracking: {cls.CHANGE_TRACKING_ENABLED}")
        print(f"WebSocket Enabled: {cls.WEBSOCKET_ENABLED}")
        print(f"Media Extraction: {cls.MEDIA_EXTRACTION_ENABLED}")
        print("-" * 60)
        print("DataForSEO Settings:")
        print(f"DataForSEO Enabled: {cls.DATAFORSEO_ENABLED}")
        print(f"DataForSEO Login: {'*' * 10}{cls.DATAFORSEO_LOGIN[-10:] if cls.DATAFORSEO_LOGIN else 'NOT SET'}")
        print(f"SEO SERP Module: {cls.SEO_SERP_ENABLED}")
        print(f"SEO Keywords Module: {cls.SEO_KEYWORDS_ENABLED}")
        print(f"SEO Backlinks Module: {cls.SEO_BACKLINKS_ENABLED}")
        print(f"SEO OnPage Module: {cls.SEO_ONPAGE_ENABLED}")
        print(f"SEO Labs Module: {cls.SEO_LABS_ENABLED}")
        print(f"SEO Default Location: {cls.SEO_DEFAULT_LOCATION} ({cls.SEO_DEFAULT_LOCATION_CODE})")
        print(f"SEO Default Language: {cls.SEO_DEFAULT_LANGUAGE}")
        print(f"SEO Output Directory: {cls.SEO_OUTPUT_DIR}")
        print("-" * 60)
        print("Spark 1 Pro Settings:")
        print(f"LLM Model: {cls.FIRECRAWL_LLM_MODEL}")
        print(f"Spark Pro Enabled: {cls.SPARK_PRO_ENABLED}")
        print(f"Fast Mapping (15x): {cls.FAST_MAPPING_ENABLED}")
        print(f"Fast Mapping Limit: {cls.FAST_MAPPING_LIMIT:,} URLs")
        print(f"YouTube Transcripts: {cls.YOUTUBE_TRANSCRIPT_ENABLED}")
        print(f"Excel Scraping: {cls.EXCEL_SCRAPING_ENABLED}")
        print("-" * 60)
        print("Lead Generation Settings:")
        print(f"Lead Gen Enabled: {cls.LEAD_GEN_ENABLED}")
        print(f"Lead Extraction Model: {cls.LEAD_EXTRACTION_MODEL}")
        print(f"Lead Output Dir: {cls.LEAD_OUTPUT_DIR}")
        print("-" * 60)
        print("Credit Usage Strategy:")
        print(f"Monthly Limit: {cls.CREDITS_MONTHLY_LIMIT:,}")
        print(f"Credits Used: {cls.CREDITS_USED:,}")
        print(f"Credits Available: {cls.CREDITS_AVAILABLE:,}")
        print(f"Daily Target: {cls.DAILY_CREDIT_TARGET:,}")
        print("-" * 60)
        print("Skills System (Psybir Evidence Engine):")
        print(f"Skills Enabled: {cls.SKILLS_ENABLED}")
        print(f"Skills Directory: {cls.SKILLS_DIR}")
        print(f"Skills Output: {cls.SKILLS_OUTPUT_DIR}")
        print(f"Default Geo Scope: {cls.DEFAULT_GEO_SCOPE}")
        print(f"Default Geo Bucket: {cls.DEFAULT_GEO_BUCKET}")
        print(f"Default Location Cluster: {cls.DEFAULT_LOCATION_CLUSTER or '(not set)'}")
        print(f"Cache Enabled: {cls.SKILLS_CACHE_ENABLED}")
        print(f"NL Routing Enabled: {cls.SKILLS_NL_ROUTING_ENABLED}")
        print("="*60 + "\n")

    @classmethod
    def to_dict(cls) -> dict:
        """
        Export configuration as dictionary.

        Returns:
            Dictionary of all configuration values
        """
        return {
            'api_version': cls.API_VERSION,
            'api_base_url': cls.API_BASE_URL,
            'output_dir': str(cls.OUTPUT_DIR),
            'proxy_type': cls.PROXY_TYPE,
            'max_retries': cls.MAX_RETRIES,
            'retry_delay': cls.RETRY_DELAY,
            'log_level': cls.LOG_LEVEL,
            'default_strategy': cls.DEFAULT_STRATEGY,
            'default_max_pages': cls.DEFAULT_MAX_PAGES,
            'max_batch_size': cls.MAX_BATCH_SIZE,
            'batch_poll_interval': cls.BATCH_POLL_INTERVAL,
            'default_wait_timeout': cls.DEFAULT_WAIT_TIMEOUT,
            'enable_screenshots': cls.ENABLE_SCREENSHOTS,
            'change_tracking_enabled': cls.CHANGE_TRACKING_ENABLED,
            'websocket_enabled': cls.WEBSOCKET_ENABLED,
            'media_extraction_enabled': cls.MEDIA_EXTRACTION_ENABLED,
            # DataForSEO settings
            'dataforseo_enabled': cls.DATAFORSEO_ENABLED,
            'seo_serp_enabled': cls.SEO_SERP_ENABLED,
            'seo_keywords_enabled': cls.SEO_KEYWORDS_ENABLED,
            'seo_backlinks_enabled': cls.SEO_BACKLINKS_ENABLED,
            'seo_onpage_enabled': cls.SEO_ONPAGE_ENABLED,
            'seo_labs_enabled': cls.SEO_LABS_ENABLED,
            'seo_default_location': cls.SEO_DEFAULT_LOCATION,
            'seo_default_location_code': cls.SEO_DEFAULT_LOCATION_CODE,
            'seo_default_language': cls.SEO_DEFAULT_LANGUAGE,
            'seo_output_dir': str(cls.SEO_OUTPUT_DIR),
            # Spark 1 Pro settings
            'firecrawl_llm_model': cls.FIRECRAWL_LLM_MODEL,
            'spark_pro_enabled': cls.SPARK_PRO_ENABLED,
            'fast_mapping_enabled': cls.FAST_MAPPING_ENABLED,
            'fast_mapping_limit': cls.FAST_MAPPING_LIMIT,
            'youtube_transcript_enabled': cls.YOUTUBE_TRANSCRIPT_ENABLED,
            'excel_scraping_enabled': cls.EXCEL_SCRAPING_ENABLED,
            # Lead generation
            'lead_gen_enabled': cls.LEAD_GEN_ENABLED,
            'lead_extraction_model': cls.LEAD_EXTRACTION_MODEL,
            'lead_output_dir': str(cls.LEAD_OUTPUT_DIR),
            # Credit tracking
            'credits_monthly_limit': cls.CREDITS_MONTHLY_LIMIT,
            'credits_used': cls.CREDITS_USED,
            'credits_available': cls.CREDITS_AVAILABLE,
            'daily_credit_target': cls.DAILY_CREDIT_TARGET,
            # Skills system (Psybir Evidence Engine)
            'skills_enabled': cls.SKILLS_ENABLED,
            'skills_dir': str(cls.SKILLS_DIR),
            'skills_output_dir': str(cls.SKILLS_OUTPUT_DIR),
            'default_geo_scope': cls.DEFAULT_GEO_SCOPE,
            'default_geo_bucket': cls.DEFAULT_GEO_BUCKET,
            'default_location_cluster': cls.DEFAULT_LOCATION_CLUSTER,
            'skills_cache_enabled': cls.SKILLS_CACHE_ENABLED,
            'skills_cache_max_age_days': cls.SKILLS_CACHE_MAX_AGE_DAYS,
            'skills_nl_routing_enabled': cls.SKILLS_NL_ROUTING_ENABLED,
            'skills_min_confidence': cls.SKILLS_MIN_CONFIDENCE,
        }


# Auto-validate configuration on import
Config.validate_config()

# Ensure directories exist on import
Config.ensure_directories()
