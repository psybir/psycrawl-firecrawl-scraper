# Firecrawl Scraper

A professional, production-ready web scraping system built on Firecrawl API v2. Perfect for scraping documentation, building knowledge bases, data collection, and content aggregation.

## ✨ Features

- **3 Scraping Strategies**: CRAWL (comprehensive), MAP (selective), EXTRACT (structured data)
- **Smart URL Validation**: Pre-scraping validation to catch invalid URLs before spending credits
- **Stealth Mode**: Auto-enabled for anti-bot sites (difficulty-based detection)
- **Checkpoint/Resume System**: Automatic progress saving for interrupted scrapes
- **Batch Processing**: Scrape multiple sources with automated orchestration
- **Quality Validation**: Content length thresholds, deduplication, page count validation
- **Cost Management**: Credit estimation, budget enforcement, real-time cost tracking
- **Flexible Output**: Markdown, HTML, JSON, images, screenshots, and more
- **Production-Ready**: Used for collecting 9MB+ of documentation across 13 major sources

## 🚀 Quick Start (5 Minutes)

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd firecrawl-scraper

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your FIRECRAWL_API_KEY
```

### 2. Get Your API Key

1. Visit [https://www.firecrawl.dev/](https://www.firecrawl.dev/)
2. Sign up for a free account
3. Copy your API key
4. Add it to your `.env` file:
   ```
   FIRECRAWL_API_KEY=your_api_key_here
   ```

### 3. Run Your First Scrape

```python
import asyncio
import os
from firecrawl_scraper.extraction.universal_scraper import UniversalScraper

async def main():
    api_key = os.getenv('FIRECRAWL_API_KEY')
    scraper = UniversalScraper(api_key)

    result = await scraper.scrape_source({
        'url': 'https://docs.python.org/3/tutorial/',
        'strategy': 'map',
        'max_pages': 10
    })

    if result['success']:
        print(f"✅ Scraped {len(result['data'])} pages!")
        print(f"Total characters: {result['total_chars']:,}")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == '__main__':
    asyncio.run(main())
```

**That's it!** You've just scraped your first website.

## 📋 Requirements

- Python 3.7 or higher
- Firecrawl API key (free tier available)
- Dependencies listed in `requirements.txt`

## 🔧 Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
# Required
FIRECRAWL_API_KEY=your_api_key_here

# Optional - Advanced Configuration
FIRECRAWL_PROXY_TYPE=auto          # auto, basic, or stealth
FIRECRAWL_LOCATIONS=US,DE,GB,AU,FR # Proxy locations
FIRECRAWL_MAX_RETRIES=3            # Retry attempts
FIRECRAWL_RETRY_DELAY=2000         # Delay in milliseconds
FIRECRAWL_OUTPUT_DIR=./data        # Output directory
LOG_LEVEL=INFO                     # Logging level
```

## 📖 Usage

### Strategy 1: CRAWL (Comprehensive Site Scraping)

Best for: Documentation sites, blogs, knowledge bases

```python
result = await scraper.scrape_source({
    'url': 'https://academy.bricksbuilder.io/',
    'strategy': 'crawl',
    'max_pages': 50,
    'use_stealth': False  # Auto-enabled for difficult sites
})
```

**Cost**: 1 credit per page (5 credits with stealth mode)

### Strategy 2: MAP (Selective URL Discovery)

Best for: Large sites with keyword filtering

```python
result = await scraper.scrape_source({
    'url': 'https://python.langchain.com/docs/',
    'strategy': 'map',
    'max_pages': 100,
    'filter_keywords': ['agents', 'chains', 'tools', 'memory']
})
```

**Cost**: 5 credits for sitemap discovery + 1 credit per page

**How it works**:
1. Discovers ALL URLs from sitemap (252 URLs discovered)
2. Filters by keywords (15 URLs matched)
3. Scrapes only matched URLs (saves credits)

### Strategy 3: EXTRACT (Structured Data)

Best for: E-commerce products, news articles, structured content

```python
result = await scraper.scrape_source({
    'url': 'https://www.example.com/products',
    'strategy': 'extract',
    'schema': {
        'type': 'object',
        'properties': {
            'product_name': {'type': 'string'},
            'price': {'type': 'number'},
            'description': {'type': 'string'}
        }
    }
})
```

**Cost**: 15 credits per extraction (token-based billing)

### Batch Scraping

```python
sources = [
    {
        'url': 'https://docs.site1.com/',
        'strategy': 'crawl',
        'max_pages': 50,
        'category': 'site1-docs'
    },
    {
        'url': 'https://docs.site2.com/',
        'strategy': 'map',
        'filter_keywords': ['tutorial', 'guide'],
        'category': 'site2-docs'
    }
]

report = await scraper.scrape_batch(sources, run_name='my-batch-scrape')
print(f"Scraped {report['total_pages']} pages from {report['successful']}/{len(sources)} sources")
```

## 📁 Output Structure

Scraped data is organized in the `data/` directory:

```
data/
└── [source-name]/
    ├── metadata.json                 # Scraping metadata
    ├── [source]-complete-docs.md     # Combined markdown file
    └── pages/                        # Individual pages
        ├── page-001.md
        ├── page-002.md
        └── ...
```

### metadata.json Format

```json
{
  "source": "https://langchain-ai.github.io/langgraph/",
  "name": "LangGraph Official Documentation",
  "scraped_at": "2025-11-17T04:25:11.594668",
  "pages_scraped": 128,
  "total_chars": 2510503,
  "strategy": "map",
  "file": "/path/to/langgraph-complete-docs.md",
  "file_size_bytes": 2528131
}
```

## 🎨 Output Formats

Firecrawl supports multiple output formats:

- `markdown` (default) - Clean content without HTML tags
- `html` - Full HTML content
- `rawHtml` - Unprocessed HTML
- `links` - Extracted links
- `images` - Image URLs
- `screenshot` - Page screenshots
- `json` - Structured data with custom schema

Configure in scrape options:

```python
result = await scraper.scrape_source({
    'url': 'https://example.com/',
    'strategy': 'crawl',
    'formats': ['markdown', 'html', 'screenshot']
})
```

## 💡 Advanced Features

### Auto Stealth Mode

Automatically enables stealth mode for high-difficulty sites:

```python
# Stealth mode auto-enabled based on site characteristics
# No manual configuration needed!
result = await scraper.scrape_source({
    'url': 'https://difficult-site.com/',
    'strategy': 'crawl'
})
# System detects difficulty and uses stealth (5 credits vs 1 credit)
```

### Checkpoint/Resume

Automatically saves progress every source:

```python
# If scraping fails midway, resume from checkpoint
result = await scraper.scrape_batch(
    sources,
    run_name='my-scrape',
    resume_from_checkpoint=True  # Automatically resumes if available
)
```

### Credit Estimation

Estimate costs before running:

```python
estimate = await scraper.estimate_credits(sources)
print(f"Estimated cost: {estimate['total_credits']} credits")
print(f"Breakdown: {estimate['by_strategy']}")
```

## 🔍 Monitoring & Logging

Enable detailed logging in `.env`:

```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Monitor progress in real-time:

```python
# Logs automatically include:
# - URL validation status
# - Pages discovered/filtered
# - Content quality assessment
# - Success/failure status
# - Timing information
```

## 🛠️ Troubleshooting

### Issue: "URL validation failed: HTTP 403 error"

**Solution**: Site has anti-bot protection. Enable stealth mode:
```python
result = await scraper.scrape_source({
    'url': 'https://protected-site.com/',
    'strategy': 'crawl',
    'use_stealth': True  # Force stealth mode
})
```

### Issue: "CRAWL strategy discovered 0 URLs"

**Solution**: Site doesn't support standard crawling. Try MAP strategy with manually discovered URLs or use a different starting URL.

### Issue: "Low content (<1000 chars)"

**Solution**: This is a warning, not an error. Some pages naturally have less content. Adjust quality thresholds if needed.

### Issue: "API key not found"

**Solution**: Ensure `.env` file exists in project root with correct format:
```bash
FIRECRAWL_API_KEY=fc-your-key-here
```

## 📊 Real-World Example

**Comprehensive Documentation Collection** (Actual production run):

```python
sources = [
    {'url': 'https://python.langchain.com/docs/', 'strategy': 'map', 'max_pages': 500},
    {'url': 'https://langchain-ai.github.io/langgraph/', 'strategy': 'map', 'max_pages': 200},
    {'url': 'https://docs.trychroma.com/', 'strategy': 'map', 'max_pages': 150},
]

report = await scraper.scrape_batch(sources, run_name='ai-docs')
```

**Results**:
- 273 pages scraped
- 4.2MB of documentation
- 100% success rate
- ~45 minutes execution time

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- Built on [Firecrawl API v2](https://www.firecrawl.dev/)
- Tested with 13+ documentation sources
- Production-validated with 9MB+ scraped data

## 📞 Support

- **Issues**: [GitHub Issues](link-to-issues)
- **Documentation**: See `/docs` directory for detailed guides
- **Firecrawl Docs**: [https://docs.firecrawl.dev/](https://docs.firecrawl.dev/)

---

**Made with ❤️ for the web scraping community**
