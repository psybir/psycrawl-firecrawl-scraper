# Firecrawl + DataForSEO Examples

Quick start guide for the three operational modes of the Local SEO Research System.

## Setup

1. Create `.env.local` in the project root:

```bash
# Firecrawl (Required for Modes 1 & 3)
FIRECRAWL_API_KEY=fc-your-api-key

# DataForSEO (Required for Modes 2 & 3)
DATAFORSEO_LOGIN=your@email.com
DATAFORSEO_PASSWORD=your_api_key
DATAFORSEO_ENABLED=true
```

2. Install dependencies:

```bash
pip install -e .
```

---

## Mode 1: Firecrawl Only (Website Scraping)

**File:** `firecrawl_only_example.py`

**Cost:** ~1 credit per page

```python
import asyncio
from firecrawl_scraper import Config, EnhancedFirecrawlClient

async def main():
    client = EnhancedFirecrawlClient(Config.API_KEY)

    # Scrape a single page
    result = await client.scrape(
        url="https://example.com",
        formats=['markdown', 'html']
    )

    if result.get('success'):
        print(f"Title: {result.get('metadata', {}).get('title')}")
        print(f"Content: {result.get('markdown', '')[:500]}...")

    # Map all URLs on a site
    map_result = await client.map(url="https://example.com", limit=50)
    urls = [link.get('url') if isinstance(link, dict) else link
            for link in map_result.get('links', [])]
    print(f"Found {len(urls)} URLs")

    # Batch scrape multiple pages
    if urls:
        batch_result = await client.batch_scrape(
            urls=urls[:10],  # First 10 only
            formats=['markdown']
        )
        print(f"Scraped {len(batch_result.get('data', []))} pages")

asyncio.run(main())
```

---

## Mode 2: DataForSEO Only (SEO Research)

**File:** `dataforseo_only_example.py`

**Cost:** ~$0.03-0.10 per query

```python
import asyncio
from firecrawl_scraper.core.dataforseo_client import DataForSEOClient

async def main():
    client = DataForSEOClient(
        login="your@email.com",
        password="your_api_key"
    )

    # 1. Keyword Search Volumes
    keywords = await client.keywords_google_ads(
        keywords=["paintless dent repair", "PDR near me", "dent removal"],
        location_code=2840,
        language_code="en"
    )
    print("Keyword volumes:", keywords.get('success'))

    # 2. Backlinks Analysis
    backlinks = await client.backlinks_summary(target="competitor.com")
    if backlinks.get('success'):
        for task in backlinks.get('data', []):
            for res in task.get('result') or []:
                print(f"Backlinks: {res.get('backlinks', 0)}")
                print(f"Referring domains: {res.get('referring_domains', 0)}")

    # 3. Local Search Grid
    grid = client.build_geo_grid(
        center_lat=40.6259,
        center_lng=-75.3705,
        grid_size=3,        # 3x3 = 9 points (small for testing)
        spacing_miles=2.0
    )

    grid_results = await client.query_local_search_grid(
        keyword="dent repair near me",
        grid_coords=grid,
        depth=10
    )
    print(f"Competitors found: {grid_results.get('total_competitors_found', 0)}")

    # 4. Google Business Profile
    gbp = await client.business_data_google_my_business_info(
        keyword="Dent Sorcery Bethlehem PA",
        location_name="Bethlehem,Pennsylvania,United States"
    )
    print("GBP data:", gbp.get('success'))

    # Print cost stats
    print("\nAPI Usage:")
    print(client.get_stats())

asyncio.run(main())
```

---

## Mode 3: Combined (Full Local SEO Research)

**File:** `local_seo_research.py`

**Cost:** ~$3-5 DataForSEO + 50 Firecrawl credits

### Full Analysis

```bash
python examples/local_seo_research.py
```

### Run Specific Modules

```bash
# Website scraping only
python examples/local_seo_research.py --module scrape

# Grid analysis only
python examples/local_seo_research.py --module grid

# Competitor analysis only
python examples/local_seo_research.py --module competitors

# Keyword research only
python examples/local_seo_research.py --module keywords
```

### Customize for Your Business

Edit the configuration at the top of `local_seo_research.py`:

```python
TARGET_BUSINESS = {
    "name": "Your Business Name",
    "domain": "yourdomain.com",
    "url": "https://yourdomain.com/",
    "address": "123 Main St, City, ST 12345",
    "phone": "555-123-4567"
}

GRID_CONFIG = {
    "center_lat": 40.0000,    # Your latitude
    "center_lng": -75.0000,   # Your longitude
    "grid_size": 8,           # 8x8 = 64 grid points
    "spacing_miles": 2.0      # Miles between points
}

SERVICES = ["your", "service", "keywords"]
LOCATIONS = ["City 1", "City 2", "near me"]
```

---

## Template Script

**File:** `local_seo_template.py`

A parameterized version for easy reuse across projects:

```bash
python examples/local_seo_template.py \
    --name "My Business" \
    --domain "mybusiness.com" \
    --lat 40.0000 \
    --lng -75.0000 \
    --keywords "service 1" "service 2" \
    --output ./data/my_research
```

---

## Output Location

All outputs are saved to:
```
data/{business_name}_research/
├── site_content/       # Scraped pages
├── local_seo/          # GBP, reviews, grid results
├── competitors/        # Competitor profiles
├── keywords/           # Keyword data
└── reports/            # Summary reports
```

---

## Example Scripts Index

| Script | Mode | Description |
|--------|------|-------------|
| `firecrawl_only_example.py` | 1 | Website scraping basics |
| `dataforseo_only_example.py` | 2 | SEO research without scraping |
| `local_seo_research.py` | 3 | Full local SEO analysis |
| `local_seo_template.py` | 3 | Reusable template |
| `quick_start.py` | 1 | Simple Firecrawl intro |
| `batch_scraping.py` | 1 | Batch scraping patterns |
| `keyword_research_example.py` | 2 | Keyword research focus |
| `competitor_analysis_example.py` | 2/3 | Competitor deep-dive |

---

## Troubleshooting

**"FIRECRAWL_API_KEY not found"**
- Create `.env.local` with your API key

**"DataForSEO credentials required"**
- Add `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` to `.env.local`

**Empty results from grid analysis**
- Verify coordinates are correct
- Try a more common search term first
- Check if the location has businesses for that keyword

**High costs**
- Reduce grid_size (5 instead of 8)
- Limit keywords for grid analysis to 3-5
- Run modules separately with --module flag
