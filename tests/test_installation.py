#!/usr/bin/env python3
"""
Installation Validation Test

This script tests that the Firecrawl Scraper package is correctly installed
and all components are accessible. Run this after installing the package to
verify everything works.

Usage:
    python tests/test_installation.py
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")

    try:
        from firecrawl_scraper import Config, UniversalScraper, EnhancedFirecrawlClient
        print("✅ Core imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test that Config class is properly configured."""
    print("\nTesting Config class...")

    try:
        from firecrawl_scraper import Config

        # Test that directories are created
        Config.ensure_directories()

        # Check that required directories exist
        if not Config.OUTPUT_DIR.exists():
            print(f"❌ OUTPUT_DIR does not exist: {Config.OUTPUT_DIR}")
            return False

        if not Config.CHECKPOINT_DIR.exists():
            print(f"❌ CHECKPOINT_DIR does not exist: {Config.CHECKPOINT_DIR}")
            return False

        # Test helper methods
        test_category = "test-validation"
        test_path = Config.get_output_path(test_category)

        if not test_path.exists():
            print(f"❌ get_output_path() failed to create directory: {test_path}")
            return False

        # Cleanup test directory
        test_path.rmdir()

        print(f"✅ Config class working correctly")
        print(f"   OUTPUT_DIR: {Config.OUTPUT_DIR}")
        print(f"   CHECKPOINT_DIR: {Config.CHECKPOINT_DIR}")
        return True

    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_api_key():
    """Test that API key is properly configured."""
    print("\nTesting API key configuration...")

    try:
        from firecrawl_scraper import Config

        if not Config.API_KEY:
            print("❌ FIRECRAWL_API_KEY not set in environment")
            print("   Please copy .env.example to .env and add your API key")
            return False

        if Config.API_KEY == "your_api_key_here":
            print("❌ FIRECRAWL_API_KEY still set to placeholder value")
            print("   Please add your real API key to .env")
            return False

        # Check key format (should start with 'fc-')
        if not Config.API_KEY.startswith('fc-'):
            print("⚠️  Warning: API key doesn't start with 'fc-' - this may not be a valid Firecrawl key")
            return True  # Still pass, might be a different format

        print("✅ API key configured correctly")
        print(f"   Key prefix: {Config.API_KEY[:8]}...")
        return True

    except ValueError as e:
        print(f"❌ API key validation failed: {e}")
        return False

def test_scraper_initialization():
    """Test that UniversalScraper can be initialized."""
    print("\nTesting UniversalScraper initialization...")

    try:
        from firecrawl_scraper import UniversalScraper, Config

        scraper = UniversalScraper(Config.API_KEY)

        if not scraper:
            print("❌ Failed to initialize UniversalScraper")
            return False

        print("✅ UniversalScraper initialized successfully")
        return True

    except Exception as e:
        print(f"❌ Scraper initialization failed: {e}")
        return False

def test_example_scripts():
    """Test that example scripts exist and are executable."""
    print("\nTesting example scripts...")

    examples_dir = Path(__file__).parent.parent / "examples"

    if not examples_dir.exists():
        print(f"❌ Examples directory not found: {examples_dir}")
        return False

    required_examples = [
        "quick_start.py",
        "batch_scraping.py",
        "advanced_use_cases.py"
    ]

    missing_examples = []
    for example in required_examples:
        example_path = examples_dir / example
        if not example_path.exists():
            missing_examples.append(example)

    if missing_examples:
        print(f"❌ Missing example scripts: {', '.join(missing_examples)}")
        return False

    print(f"✅ All {len(required_examples)} example scripts found")
    return True

def test_documentation():
    """Test that documentation files exist."""
    print("\nTesting documentation...")

    repo_dir = Path(__file__).parent.parent

    required_docs = [
        "README.md",
        "DATA_FORMAT.md",
        "USAGE.md",
        ".env.example"
    ]

    missing_docs = []
    for doc in required_docs:
        doc_path = repo_dir / doc
        if not doc_path.exists():
            missing_docs.append(doc)

    if missing_docs:
        print(f"❌ Missing documentation files: {', '.join(missing_docs)}")
        return False

    print(f"✅ All {len(required_docs)} documentation files found")
    return True

def main():
    """Run all validation tests."""
    print("=" * 80)
    print("FIRECRAWL SCRAPER - INSTALLATION VALIDATION TEST")
    print("=" * 80)
    print()

    tests = [
        ("Import Test", test_imports),
        ("Config Test", test_config),
        ("API Key Test", test_api_key),
        ("Scraper Initialization", test_scraper_initialization),
        ("Example Scripts", test_example_scripts),
        ("Documentation", test_documentation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} encountered an error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! The Firecrawl Scraper is ready to use.")
        print("\nNext steps:")
        print("  1. Run a quick test: python examples/quick_start.py")
        print("  2. Read the usage guide: cat USAGE.md")
        print("  3. Explore advanced examples: python examples/advanced_use_cases.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("  - Missing .env file: Copy .env.example to .env")
        print("  - Invalid API key: Add your Firecrawl API key to .env")
        print("  - Missing dependencies: Run 'pip install -r requirements.txt'")
        return 1

if __name__ == '__main__':
    sys.exit(main())
