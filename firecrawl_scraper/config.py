"""
Centralized Configuration for Firecrawl Scraper

This module manages all environment variables and configuration settings
for the Firecrawl scraping system. All paths and credentials are loaded
from environment variables (.env file) to ensure no hardcoded values.

Usage:
    from firecrawl_scraper.config import Config

    # Access configuration
    api_key = Config.API_KEY
    output_dir = Config.OUTPUT_DIR
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Centralized configuration class for Firecrawl Scraper.

    All settings are loaded from environment variables with sensible defaults.
    """

    # ========== Directory Configuration ==========
    BASE_DIR = Path(__file__).parent.parent.resolve()
    OUTPUT_DIR = Path(os.getenv('FIRECRAWL_OUTPUT_DIR', BASE_DIR / 'data')).resolve()
    CHECKPOINT_DIR = OUTPUT_DIR / '_checkpoints'

    # ========== API Configuration ==========
    API_KEY = os.getenv('FIRECRAWL_API_KEY')
    BACKUP_KEY = os.getenv('FIRECRAWL_BACKUP_KEY')

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
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))  # seconds

    # ========== Default Scraping Options ==========
    DEFAULT_STRATEGY = os.getenv('DEFAULT_STRATEGY', 'map')
    DEFAULT_MAX_PAGES = int(os.getenv('DEFAULT_MAX_PAGES', '50'))
    DEFAULT_USE_STEALTH = os.getenv('DEFAULT_USE_STEALTH', 'false').lower() == 'true'

    # ========== Helper Methods ==========

    @classmethod
    def ensure_directories(cls):
        """
        Ensure all required directories exist.
        Creates OUTPUT_DIR and CHECKPOINT_DIR if they don't exist.
        """
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

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
    def validate_config(cls):
        """
        Validate all configuration settings.
        Raises ValueError if any settings are invalid.
        """
        # This runs automatically during class initialization
        # but can be called explicitly for re-validation
        pass

    @classmethod
    def print_config(cls):
        """
        Print current configuration (for debugging).
        Masks sensitive values like API keys.
        """
        print("\n" + "="*60)
        print("Firecrawl Scraper Configuration")
        print("="*60)
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
        print("="*60 + "\n")


# Auto-validate configuration on import
Config.validate_config()

# Ensure directories exist on import
Config.ensure_directories()
