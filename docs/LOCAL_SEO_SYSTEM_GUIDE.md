# Firecrawl + DataForSEO Local SEO System Guide

## Overview

This system combines Firecrawl (web scraping) and DataForSEO (SEO research) APIs for comprehensive local SEO analysis. It supports three operational modes for flexibility across different use cases.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Local SEO Research System                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  Firecrawl   │     │  DataForSEO  │     │   Combined   │    │
│  │   (Mode 1)   │     │   (Mode 2)   │     │   (Mode 3)   │    │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘    │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Unified Output (JSON + Markdown)             │  │
│  │                                                           │  │
│  │  • Metadata-wrapped JSON for LLM analysis                 │  │
│  │  • Standardized error structures                          │  │
│  │  • Markdown reports for human review                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- Firecrawl API key (for Modes 1 & 3)
- DataForSEO credentials (for Modes 2 & 3)

### 1. Install Dependencies

```bash
cd psycrawl-firecrawl-scraper
pip install -e .
```

### 2. Configure Environment

Create a `.env.local` file in the project root:

```bash
# Firecrawl Configuration (Required for Modes 1 & 3)
FIRECRAWL_API_KEY=fc-your-api-key-here
FIRECRAWL_OUTPUT_DIR=./data

# DataForSEO Configuration (Required for Modes 2 & 3)
DATAFORSEO_LOGIN=your@email.com
DATAFORSEO_PASSWORD=your_api_password
DATAFORSEO_ENABLED=true

# Optional Performance Settings
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=60
```

### 3. Verify Installation

```bash
python -c "from firecrawl_scraper import Config; Config.print_config()"
```

---

## Three Operational Modes

### Mode 1: Firecrawl Only

**Use Case:** Website scraping, content extraction, competitive website analysis

**Cost:** ~1 credit per page

**When to Use:**
- Scraping website content for analysis
- Extracting structured data from competitors
- Building content inventories
- Monitoring website changes

**Example:**

```python
import asyncio
from firecrawl_scraper import Config, EnhancedFirecrawlClient

async def scrape_website():
    client = EnhancedFirecrawlClient(Config.API_KEY)

    # Single page scrape
    result = await client.scrape(
        url="https://example.com",
        formats=['markdown', 'html']
    )

    # Get all URLs from a site
    map_result = await client.map(
        url="https://example.com",
        limit=50
    )

    # Batch scrape multiple URLs
    urls = [link.get('url') for link in map_result.get('links', [])]
    batch_result = await client.batch_scrape(
        urls=urls,
        formats=['markdown']
    )

    return batch_result

asyncio.run(scrape_website())
```

---

### Mode 2: DataForSEO Only

**Use Case:** Keyword research, backlink analysis, SERP tracking, local search grid

**Cost:** ~$0.03-0.10 per query (varies by endpoint)

**When to Use:**
- Keyword research and search volume data
- Competitor backlink analysis
- Local search visibility mapping
- Google Business Profile data extraction

**Example:**

```python
import asyncio
from firecrawl_scraper.core.dataforseo_client import DataForSEOClient

async def seo_research():
    client = DataForSEOClient(
        login="your@email.com",
        password="your_api_password"
    )

    # Get keyword search volumes
    keywords_result = await client.keywords_google_ads(
        keywords=["paintless dent repair", "PDR near me"],
        location_code=2840,  # USA
        language_code="en"
    )

    # Get backlinks summary
    backlinks = await client.backlinks_summary(target="competitor.com")

    # Local search grid analysis
    grid = client.build_geo_grid(
        center_lat=40.6259,
        center_lng=-75.3705,
        grid_size=5,       # 5x5 = 25 points
        spacing_miles=2.0
    )

    grid_results = await client.query_local_search_grid(
        keyword="dent repair near me",
        grid_coords=grid,
        depth=20
    )

    # Print API usage stats
    print(client.get_stats())

    return grid_results

asyncio.run(seo_research())
```

---

### Mode 3: Combined (Full Local SEO Research)

**Use Case:** Complete local business SEO analysis

**Cost:** ~$3-5 per business (DataForSEO) + Firecrawl credits

**What It Does:**
1. Scrapes target website (all pages)
2. Gets Google Business Profile data
3. Retrieves reviews and Q&A
4. Runs local search grid analysis
5. Discovers and analyzes competitors
6. Performs keyword research
7. Generates comprehensive reports

**Example:**

```bash
python examples/local_seo_research.py
```

Or run specific modules:

```bash
python examples/local_seo_research.py --module scrape      # Website only
python examples/local_seo_research.py --module grid        # Grid analysis only
python examples/local_seo_research.py --module competitors # Competitor analysis
python examples/local_seo_research.py --module keywords    # Keyword research
```

---

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FIRECRAWL_API_KEY` | Mode 1/3 | - | Firecrawl API key |
| `DATAFORSEO_LOGIN` | Mode 2/3 | - | DataForSEO email |
| `DATAFORSEO_PASSWORD` | Mode 2/3 | - | DataForSEO API key |
| `DATAFORSEO_ENABLED` | Mode 2/3 | false | Enable DataForSEO |
| `FIRECRAWL_OUTPUT_DIR` | No | ./data | Output directory |
| `MAX_CONCURRENT_REQUESTS` | No | 5 | Concurrent request limit |
| `REQUEST_TIMEOUT` | No | 60 | Request timeout (seconds) |
| `SEO_DEFAULT_LOCATION` | No | United States | Default search location |
| `SEO_DEFAULT_LOCATION_CODE` | No | 2840 | Location code (2840=US) |

### Business Configuration (in script)

```python
TARGET_BUSINESS = {
    "name": "Your Business Name",
    "domain": "yourdomain.com",
    "url": "https://yourdomain.com/",
    "address": "123 Main St, City, ST 12345",
    "phone": "555-123-4567"
}

GRID_CONFIG = {
    "center_lat": 40.0000,    # Business latitude
    "center_lng": -75.0000,   # Business longitude
    "grid_size": 8,           # 8x8 = 64 points
    "spacing_miles": 2.0      # Distance between points
}

SERVICES = ["your", "service", "keywords"]
LOCATIONS = ["City 1", "City 2", "near me"]
```

---

## API Cost Reference

### Firecrawl Pricing

| Endpoint | Cost | Notes |
|----------|------|-------|
| `/scrape` | 1 credit/page | Single page |
| `/batch/scrape` | 1 credit/URL | Up to 1000 URLs |
| `/map` | 5 credits | Site URL discovery |
| `/crawl` | 1 credit/page | Full site crawl |

### DataForSEO Pricing (Approximate)

| Endpoint | Cost | Notes |
|----------|------|-------|
| SERP (organic) | ~$0.002/query | Google search results |
| SERP (maps) | ~$0.004/query | Google Maps results |
| Keywords (Google Ads) | ~$0.05/100 kw | Search volume data |
| GBP Profile | ~$0.10/business | Business profile |
| Reviews | ~$0.05/business | Up to 4500 reviews |
| Backlinks Summary | ~$0.20/domain | Link metrics |
| Backlinks List | ~$0.50/domain | Detailed backlinks |
| Labs (keyword ideas) | ~$0.05/query | Keyword suggestions |

### Estimated Costs by Use Case

| Use Case | DataForSEO | Firecrawl | Total |
|----------|------------|-----------|-------|
| Single website scrape (20 pages) | $0 | 25 credits | 25 credits |
| Keyword research (50 keywords) | ~$0.03 | 0 | ~$0.03 |
| Local grid (5x5, 3 keywords) | ~$0.30 | 0 | ~$0.30 |
| Full local SEO analysis | ~$3-5 | ~50 credits | ~$5 + credits |

---

## Output Structure

### Directory Layout

```
data/
└── {project}_research/
    ├── site_content/
    │   ├── pages/
    │   │   └── *.md
    │   ├── blog/
    │   │   └── *.md
    │   └── structure.json
    ├── local_seo/
    │   ├── gbp_profile.json
    │   ├── reviews.json
    │   ├── qa.json
    │   ├── grid_results.json
    │   └── grid_heatmap.json
    ├── competitors/
    │   ├── competitor_profiles/
    │   │   └── *.json
    │   ├── competitor_list.json
    │   └── comparison.json
    ├── keywords/
    │   ├── target_keywords.json
    │   └── keyword_ideas.json
    └── reports/
        ├── full_report.json
        ├── full_report.md
        └── executive_summary.md
```

### JSON Output Format (with Metadata)

All JSON outputs are wrapped with metadata for LLM analysis:

```json
{
  "_meta": {
    "version": "1.0",
    "generated_at": "2024-01-15T10:30:00.000Z",
    "schema": "local_seo_full_report_v1",
    "source": "psycrawl-firecrawl-scraper",
    "generator": "local_seo_research.py"
  },
  "data": {
    // actual data here
  }
}
```

### Error Response Format

All errors follow a standardized structure:

```json
{
  "success": false,
  "error": "Error message here",
  "error_type": "ExceptionClassName",
  "context": "function_name",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## Bug Fixes Applied (v1.0.1)

### 1. Null-Safety Pattern

**Problem:** `dict.get('key', [])` returns `None` when key exists with null value.

**Solution:** Use `(dict.get('key') or [])` pattern throughout.

```python
# Before (broken)
results = task.get('result', [])  # Returns None if result=null

# After (fixed)
task_results = task.get('result') or []  # Always returns list
```

### 2. Nested Null-Safety

**Problem:** Chained `.get()` calls fail when intermediate values are null.

```python
# Before (broken)
rating = item.get('rating', {}).get('value')  # Fails if rating=null

# After (fixed)
rating_data = item.get('rating') or {}
rating = rating_data.get('value')
```

### 3. Division by Zero

**Problem:** Average calculations can divide by zero or sum None values.

```python
# Before (broken)
avg = sum(p['position'] for p in positions) / len(positions)

# After (fixed)
valid_positions = [p.get('position', 0) for p in positions
                   if p.get('position') is not None]
avg = sum(valid_positions) / len(valid_positions) if valid_positions else 0
```

### 4. JSON Decode Error Handling

**Problem:** Malformed API responses caused unhandled exceptions.

```python
# Now wrapped with try/except
try:
    data = await response.json()
except (aiohttp.ContentTypeError, json.JSONDecodeError) as e:
    return {'success': False, 'error': f'Invalid JSON: {str(e)}'}
```

### 5. Map API URL Format

**Problem:** Map API returns `{'url': '...'}` dicts, not strings.

```python
# Fixed extraction
for link in raw_links:
    if isinstance(link, dict):
        url = link.get('url', '')
    else:
        url = str(link)
```

---

## Troubleshooting

### Common Issues

**1. "DataForSEO credentials required" error**

Ensure `.env.local` has:
```
DATAFORSEO_LOGIN=your@email.com
DATAFORSEO_PASSWORD=your_api_key
DATAFORSEO_ENABLED=true
```

**2. "FIRECRAWL_API_KEY not found" error**

Add to `.env.local`:
```
FIRECRAWL_API_KEY=fc-your-key-here
```

**3. Empty grid results**

- Check coordinates are valid
- Verify keyword has local search results
- Try increasing `depth` parameter

**4. Rate limiting errors**

Increase delays between requests:
```python
delay_between_requests=0.5  # seconds
```

**5. High API costs**

- Reduce grid size (5x5 instead of 8x8)
- Limit keywords for grid analysis
- Use `--module` flag to run specific sections

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Extending the System

### Adding New Data Sources

1. Create client in `firecrawl_scraper/core/`
2. Follow the pattern in `dataforseo_client.py`
3. Add configuration to `config.py`
4. Create example script in `examples/`

### Customizing Reports

Modify these functions in `local_seo_research.py`:
- `generate_markdown_report()` - Full report
- `generate_executive_summary()` - Summary report
- `generate_heatmap_data()` - Visualization data

### Adding Metadata Schemas

Use `wrap_with_metadata()` for new outputs:

```python
from local_seo_research import wrap_with_metadata

my_data = {"key": "value"}
wrapped = wrap_with_metadata(my_data, "my_custom_schema_v1")
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.1 | 2024-01 | Bug fixes: null-safety, JSON errors, heatmap calc |
| 1.0.0 | 2024-01 | Initial release with 3 operational modes |
