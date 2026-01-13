#!/usr/bin/env python3
"""
Media Extraction Example - PDF/DOCX/Image Processing

Demonstrates media extraction capabilities:
- PDF document parsing
- DOCX document extraction
- Image metadata
- Batch media processing

Usage:
    python examples/media_extraction_example.py

Note: Requires optional dependencies:
    pip install pypdf python-docx pillow
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from firecrawl_scraper.core.media_extractor import MediaExtractor


async def pdf_extraction_demo():
    """
    Extract content from PDF documents.
    """

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      PDF EXTRACTION DEMO                                      ║
║               Extract Text and Metadata from PDFs                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    extractor = MediaExtractor(max_size_mb=50)

    # Example PDF URLs (public documents)
    pdf_urls = [
        'https://www.w3.org/WAI/WCAG21/Techniques/pdf/img/table-word.pdf',
        # Add more PDF URLs here
    ]

    print(f"📄 PDFs to process: {len(pdf_urls)}")
    print("-" * 60)

    for url in pdf_urls:
        print(f"\n📄 Extracting: {url}")

        result = await extractor.extract_pdf(url)

        if result.success:
            print(f"   ✅ Success!")
            print(f"   Pages: {result.page_count}")
            print(f"   Words: {result.word_count:,}")
            print(f"   Time:  {result.extraction_time:.2f}s")

            if result.metadata:
                print(f"   Title: {result.metadata.get('title', 'N/A')}")
                print(f"   Author: {result.metadata.get('author', 'N/A')}")

            print(f"\n   Content preview:")
            print(f"   {result.content[:300]}...")
        else:
            print(f"   ❌ Failed: {result.error}")

    print("-" * 60)


async def image_extraction_demo():
    """
    Extract metadata from images.
    """

    print("\n" + "=" * 60)
    print("🖼️  IMAGE METADATA EXTRACTION")
    print("=" * 60)

    extractor = MediaExtractor()

    # Example image URLs
    image_urls = [
        'https://httpbin.org/image/png',
        'https://httpbin.org/image/jpeg',
    ]

    print(f"\n🖼️  Images to process: {len(image_urls)}")
    print("-" * 40)

    for url in image_urls:
        print(f"\n🖼️  Processing: {url}")

        result = await extractor.extract_image(url)

        if result.success:
            print(f"   ✅ Success!")
            print(f"   Format: {result.metadata.get('format', 'Unknown')}")
            print(f"   Size: {result.metadata.get('size', 'Unknown')}")
            print(f"   Mode: {result.metadata.get('mode', 'Unknown')}")
            print(f"   Time: {result.extraction_time:.2f}s")
        else:
            print(f"   ❌ Failed: {result.error}")

    print("-" * 40)


async def auto_detect_demo():
    """
    Auto-detect media type and extract.
    """

    print("\n" + "=" * 60)
    print("🔍 AUTO-DETECT MEDIA TYPE")
    print("=" * 60)

    extractor = MediaExtractor()

    # Mixed URLs
    urls = [
        'https://httpbin.org/image/png',
        'https://www.w3.org/WAI/WCAG21/Techniques/pdf/img/table-word.pdf',
    ]

    print(f"\n📋 URLs to process: {len(urls)}")
    print("-" * 40)

    for url in urls:
        detected = extractor.detect_media_type(url)
        print(f"\n🔍 URL: {url}")
        print(f"   Detected type: {detected or 'Unknown'}")

        if detected:
            result = await extractor.extract(url)
            if result.success:
                print(f"   ✅ Extracted: {result.word_count} words")
            else:
                print(f"   ❌ Failed: {result.error}")

    print("-" * 40)


async def batch_extraction_demo():
    """
    Extract from multiple media files in parallel.
    """

    print("\n" + "=" * 60)
    print("📦 BATCH MEDIA EXTRACTION")
    print("=" * 60)

    extractor = MediaExtractor()

    urls = [
        'https://httpbin.org/image/png',
        'https://httpbin.org/image/jpeg',
        'https://httpbin.org/image/webp',
    ]

    print(f"\n📋 Media files to process: {len(urls)}")
    print("-" * 40)

    results = await extractor.extract_batch(urls, max_concurrent=3)

    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    print(f"\n📊 BATCH RESULTS:")
    print(f"   Total: {len(results)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total time: {sum(r.extraction_time for r in results):.2f}s")

    print("-" * 40)


async def check_dependencies():
    """
    Check which media extraction dependencies are available.
    """

    print("\n" + "=" * 60)
    print("📦 DEPENDENCY CHECK")
    print("=" * 60 + "\n")

    dependencies = {
        'pypdf': 'PDF extraction',
        'python-docx': 'DOCX extraction',
        'pillow': 'Image processing'
    }

    for package, purpose in dependencies.items():
        try:
            if package == 'pypdf':
                from pypdf import PdfReader
                status = "✅ Installed"
            elif package == 'python-docx':
                from docx import Document
                status = "✅ Installed"
            elif package == 'pillow':
                from PIL import Image
                status = "✅ Installed"
        except ImportError:
            status = "❌ Not installed"

        print(f"   {package}: {status}")
        print(f"      Purpose: {purpose}")
        print()

    print("-" * 40)
    print("Install missing dependencies:")
    print("   pip install pypdf python-docx pillow")
    print("-" * 40)


async def main():
    """Run media extraction examples"""

    print("Choose an example:")
    print("1. PDF extraction")
    print("2. Image metadata extraction")
    print("3. Auto-detect media type")
    print("4. Batch extraction")
    print("5. Check dependencies")
    print("6. Run all")
    print()

    choice = input("Enter choice (1-6): ").strip()

    if choice == '1':
        await pdf_extraction_demo()
    elif choice == '2':
        await image_extraction_demo()
    elif choice == '3':
        await auto_detect_demo()
    elif choice == '4':
        await batch_extraction_demo()
    elif choice == '5':
        await check_dependencies()
    elif choice == '6':
        await check_dependencies()
        await image_extraction_demo()
        await batch_extraction_demo()
        await auto_detect_demo()
        # Skip PDF demo by default as it requires actual PDFs
    else:
        print("Invalid choice. Checking dependencies...")
        await check_dependencies()


if __name__ == '__main__':
    asyncio.run(main())
