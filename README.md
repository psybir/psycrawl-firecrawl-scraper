# PsyCrawl v4.0 - Psybir Skills System

A battle-tested, professional web scraping and competitive intelligence system combining **Firecrawl API v2**, **DataForSEO API v3**, and the new **Psybir Skills System** for decision-grade analysis with geo-context.

## What's New in v4.0 - Psybir Skills System

- **Skills System** - Modular analysis skills for competitive intelligence
- **`/competitor_intel`** - SWOT analysis, pricing, trust signals, positioning
- **`/seo_audit`** - 5-tier prioritized SEO analysis
- **3D Scoring** - Local Pack, Organic Local, Domestic Organic probabilities
- **Geo-Tagging** - All findings tagged with geographic context
- **Natural Language Routing** - Query in plain English
- **CLI Interface** - Run skills from command line

### Quick Start (v4.0)

```bash
# Install
pip install -e .

# Configure
cp .env.example .env
# Add your FIRECRAWL_API_KEY to .env

# Run skills
python -m firecrawl_scraper.cli skill list
python -m firecrawl_scraper.cli skill run competitor_intel https://competitor.com --geo "Your City"
python -m firecrawl_scraper.cli nlp "analyze competitor in my market"
```

See `docs/SKILLS_SYSTEM.md` for complete skills documentation.

---

## What's in v2.1 - Ultimate SEO Machine

- **DataForSEO Integration** - Full SERP, keywords, backlinks, on-page analysis
- **SEO Orchestrator** - Comprehensive audits with one function call
- **Competitor Analysis** - Auto-discover competitors, content gaps, keyword opportunities
- **Keyword Research** - Search volume, CPC, difficulty, and keyword ideas
- **6 Strategies** - CRAWL, MAP, EXTRACT, BATCH, DYNAMIC, and SEO

## What's in v2.0

- **Batch Scraping** - Scrape 1000+ URLs in parallel with async processing
- **Actions Support** - Click, scroll, wait, screenshot for dynamic JavaScript sites
- **Real-Time Monitoring** - Live progress updates with WebSocket/polling
- **Change Tracking** - Monitor websites for content changes over time
- **Media Extraction** - Extract content from PDFs, DOCX, and images

---

## Original Battle-Testing

Extensively stress-tested over one week with 100+ production scraping operations, handling everything from small documentation sites to massive multi-source data collection.

## 🔥 Real-World Battle Testing

This system has been **extensively stress-tested** in production environments:

- **Week-Long Continuous Testing**: 7+ days of non-stop scraping operations
- **100+ Scraping Operations**: From single-page tests to massive overnight batch jobs
- **568+ Pages Scraped**: Across 13+ major documentation sources
- **Government Websites**: Tested on .gov domains (excellent for training data)
- **Anti-Bot Bypassing**: Successfully scraped sites with Cloudflare protection
- **Overnight Batch Jobs**: Unattended 8-12 hour scraping operations
- **100% Reliability**: Checkpoint/resume system never lost progress

## 💻 Development Environment

This system was developed and tested using:

- **Primary Interface**: [Claude Code](https://code.claude.ai/) - Anthropic's official VS Code extension
- **IDE**: Cursor / Visual Studio Code
- **Workflow**: AI-assisted development with Claude Code as the primary interface for code generation, testing, and debugging
- **Python Version**: 3.7+
- **Testing Approach**: Iterative testing with real-world scraping operations

**Note for Your Team**: This entire system was built using Claude Code in VS Code/Cursor, making it easy to extend and modify with AI assistance. The code is well-documented and structured for AI-assisted development workflows.

## 💡 What Can Firecrawl API v2.60 Do?

Firecrawl API v2.60 is a powerful web scraping API that can:

### Turn Any Website Into Clean Data

**Simple Example - Scrape a Blog:**
```
Input:  https://example.com/blog
Output: Clean markdown of all blog posts, no ads, no navigation clutter
```

**What You Get:**
- Clean markdown text (perfect for AI training)
- Raw HTML (if you need it)
- All images extracted
- All links preserved
- Page screenshots
- Structured JSON data

### Real Use Cases (Simple Text Examples)

**1. Documentation Scraping**
```
Task: "Scrape all Python documentation"
Input: https://docs.python.org/3/tutorial/
Strategy: MAP (sitemap + keyword filter)
Output: 50-100 pages of clean markdown, organized by topic
Use For: Building AI training datasets, offline documentation, knowledge bases
```

**2. WordPress Design Extraction**
```
Task: "Extract design patterns from professional WordPress sites"
Input: https://bricks.academy/tutorials/
Strategy: CRAWL (comprehensive site crawl)
Output: HTML structure, CSS classes, design tokens, images
Use For: Learning design patterns, building component libraries
```

**3. Government Data Collection**
```
Task: "Collect public health data from .gov sites"
Input: https://www.cdc.gov/data/
Strategy: MAP (structured, targeted scraping)
Output: Clean data tables, reports, official documents
Use For: Research, data analysis, public datasets
```

**4. E-commerce Product Data**
```
Task: "Extract product information for price comparison"
Input: https://example-store.com/products
Strategy: EXTRACT (structured data with custom schema)
Output: JSON with product names, prices, descriptions, images
Use For: Price monitoring, market research, inventory management
```

**5. News Article Collection**
```
Task: "Archive all articles from a news site"
Input: https://news-site.com/articles
Strategy: CRAWL + keyword filtering
Output: Clean article text, publication dates, authors, images
Use For: Content analysis, trend monitoring, research
```

## ✨ Key Features

### 6 Intelligent Scraping Strategies

**SEO** (NEW in v2.1) - Ultimate SEO Machine
- Combines Firecrawl content scraping with DataForSEO analysis
- Full SEO audits: backlinks, keywords, SERP rankings, technical SEO
- Competitor analysis and content gap detection
- Cost: Varies by modules (see DataForSEO pricing)
- Best for: SEO audits, competitive intelligence, keyword research

**BATCH** (NEW in v2.0) - Large-Scale Parallel Scraping
- Scrape 1000+ URLs simultaneously
- Async processing with progress callbacks
- Cost: 1 credit/URL (same as sequential, but 10x faster)
- Best for: Known URL lists, large-scale data collection

**DYNAMIC** (NEW in v2.0) - JavaScript-Heavy Sites
- Browser automation with Actions (click, scroll, wait)
- Pre-built presets for common scenarios
- Screenshot capture support
- Mobile device emulation
- Cost: 1 credit base + 1 per action
- Best for: SPAs, lazy-loaded content, "Load More" buttons

**CRAWL** - Comprehensive Site Exploration
- Discovers and scrapes all pages automatically
- Follows internal links intelligently
- Cost: 1 credit/page (5 with stealth mode)
- Best for: Complete site backups, design extraction

**MAP** - Selective URL Discovery
- Uses sitemap.xml for URL discovery
- Keyword filtering before scraping
- Cost: 5 credits for map + 1/page scraped
- Best for: Documentation, targeted content collection

**EXTRACT** - Structured Data Extraction
- Custom JSON schemas for data extraction
- Perfect for product catalogs, listings
- Cost: 15 credits/page
- Best for: E-commerce, structured databases

### Production-Ready Features

- **Stealth Mode**: Automatically bypasses Cloudflare and anti-bot protection
- **Checkpoint/Resume**: Never lose progress on interrupted scrapes
- **Batch Processing**: Scrape 10+ sources overnight, unattended
- **Quality Validation**: Automatic content length checks, deduplication
- **Cost Management**: Budget enforcement, credit estimation, real-time tracking
- **Smart URL Validation**: Catches invalid URLs before wasting credits
- **Multiple Output Formats**: Markdown, HTML, JSON, images, screenshots

### NEW v2.1 SEO Features

- **DataForSEO Client**: Complete API v3 integration (SERP, Keywords, Backlinks, OnPage, Labs)
- **SEO Orchestrator**: Full audits, competitor analysis, keyword research with one call
- **SEO Strategy**: Combine scraping with SEO analysis in unified workflow
- **Comprehensive Reports**: Auto-generated Markdown and JSON SEO reports

### v2.0 Features

- **Actions Support**: Browser automation (click, scroll, wait, screenshot)
- **Batch Scraping**: Async API for 1000+ URL parallel processing
- **Real-Time Monitoring**: Live progress with callbacks and progress bars
- **Change Tracking**: Monitor websites for content updates
- **Media Extraction**: PDF, DOCX, and image content extraction

## 🚀 Quick Start (5 Minutes)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/psybir/psycrawl-firecrawl-scraper.git
cd psycrawl-firecrawl-scraper

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your FIRECRAWL_API_KEY
```

### 2. Get Your API Keys

**Firecrawl (Required for scraping):**
1. Visit [https://www.firecrawl.dev/](https://www.firecrawl.dev/)
2. Sign up for a free account (500 credits free)
3. Copy your API key from dashboard
4. Add it to your `.env` file as `FIRECRAWL_API_KEY`

**DataForSEO (Required for SEO features):**
1. Visit [https://app.dataforseo.com/](https://app.dataforseo.com/)
2. Sign up for an account
3. Get your credentials from API Access page
4. Add to `.env`:
   - `DATAFORSEO_LOGIN=your_email@example.com`
   - `DATAFORSEO_PASSWORD=your_api_password`
   - `DATAFORSEO_ENABLED=true`

### 3. Run Your First Scrape

**Option A: Use Pre-Built Examples**

```bash
# Simple quick start (scrapes 10 pages)
python examples/quick_start.py

# Advanced examples (stealth mode, design extraction, structured data)
python examples/advanced_use_cases.py

# Batch scraping (multiple sources)
python examples/batch_scraping.py
```

**Option B: Write Your Own Script**

```python
import asyncio
from firecrawl_scraper import UniversalScraper, Config

async def main():
    # Initialize scraper
    scraper = UniversalScraper(Config.API_KEY)

    # Define what to scrape
    source_config = {
        'url': 'https://docs.python.org/3/tutorial/',
        'strategy': 'map',  # Use sitemap for discovery
        'max_pages': 20,
        'filter_keywords': ['tutorial', 'introduction'],
        'category': 'python-docs'
    }

    # Run the scrape
    result = await scraper.scrape_source(source_config)

    # Check results
    if result['success']:
        print(f"✅ Scraped {len(result['data'])} pages!")
        print(f"📁 Data saved to: {Config.OUTPUT_DIR}/python-docs/")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

# Run it
asyncio.run(main())
```

### 4. SEO Machine Quick Start (NEW in v2.1)

```python
import asyncio
from firecrawl_scraper import SEOOrchestrator

async def main():
    # Initialize SEO Orchestrator
    seo = SEOOrchestrator()

    # Quick domain audit
    result = await seo.quick_audit('example.com')
    print(f"Domain Rank: {result['domain_rank']}")
    print(f"Backlinks: {result['backlinks']:,}")
    print(f"Referring Domains: {result['referring_domains']}")

    # Full SEO audit with content analysis
    report = await seo.full_seo_audit(
        domain='example.com',
        keywords=['seo tools', 'keyword research'],
        max_pages=50
    )
    print(report.generate_summary())

    # Competitor analysis
    competitors = await seo.competitor_analysis(
        domain='mysite.com',
        find_competitors=True  # Auto-discover competitors
    )

    # Keyword research
    keywords = await seo.keyword_research(
        seed_keywords=['python tutorial', 'learn python']
    )
    for idea in keywords['keyword_ideas'][:10]:
        print(f"{idea.keyword}: {idea.search_volume:,} searches/mo")

asyncio.run(main())
```

**Run SEO Examples:**
```bash
# SEO audit demo
python examples/seo_audit_example.py

# Competitor analysis
python examples/competitor_analysis_example.py

# Keyword research
python examples/keyword_research_example.py
```

### 5. Local SEO Research (NEW)

Complete local business market analysis with grid-based competitor discovery:

```python
import asyncio
from firecrawl_scraper import EnhancedFirecrawlClient, Config
from firecrawl_scraper.core.dataforseo_client import DataForSEOClient

async def main():
    # Initialize clients
    firecrawl = EnhancedFirecrawlClient(Config.API_KEY)
    dataforseo = DataForSEOClient(Config.DATAFORSEO_LOGIN, Config.DATAFORSEO_PASSWORD)

    # 1. Scrape target website
    result = await firecrawl.batch_scrape(
        urls=['https://example.com'],
        formats=['markdown', 'html']
    )

    # 2. Get Google Business Profile
    gbp = await dataforseo.business_data_google_my_business_info(
        keyword="Business Name City State",
        location_name="City,State,United States"
    )

    # 3. Run local search grid analysis (100 geographic points)
    grid = dataforseo.build_geo_grid(
        center_lat=40.6259,
        center_lng=-75.3705,
        grid_size=10,       # 10x10 = 100 points
        spacing_miles=6.0   # ~60 mile coverage
    )

    grid_results = await dataforseo.query_local_search_grid(
        keyword="your service near me",
        grid_coords=grid,
        depth=20
    )

    print(f"Competitors found: {grid_results['total_competitors_found']}")

asyncio.run(main())
```

**Run Local SEO Research:**
```bash
# Full local SEO research for a business
python examples/escape_exe_research.py

# Or run specific modules only
python examples/escape_exe_research.py --module scrape
python examples/escape_exe_research.py --module gbp
python examples/escape_exe_research.py --module grid
python examples/escape_exe_research.py --module keywords
python examples/escape_exe_research.py --module design    # v2.0 UI/UX analysis
```

**Output Structure:**
```
data/your_research/
├── site_content/           # Scraped website pages
│   ├── pages/              # Markdown content
│   ├── structure.json      # Site structure
│   └── media_inventory.json
├── local_seo/
│   ├── gbp_profile.json    # Google Business Profile
│   ├── reviews.json        # Customer reviews
│   ├── grid_results.json   # Geographic visibility data
│   └── grid_heatmap.json   # Visualization-ready heatmap
├── competitors/
│   ├── competitor_list.json
│   └── competitor_profiles/
├── keywords/
│   ├── target_keywords.json
│   └── keyword_ideas.json
├── visual_design/          # NEW in v2.0
│   ├── target/
│   │   ├── screenshots/    # Desktop + mobile screenshots
│   │   ├── design_system.json
│   │   ├── components.json
│   │   ├── ctas.json
│   │   └── psychology.json
│   ├── competitors/        # Competitor design analysis
│   └── design_brief.md
└── reports/
    ├── full_report.json
    ├── executive_summary.md
    ├── seo_strategy.md
    └── website_redesign_brief.md
```

### 6. Design/UI/UX Analysis (v2.0)

Capture comprehensive visual design data for website redesigns:

```python
from firecrawl_scraper.extraction.design_analyzer import DesignAnalyzer
from firecrawl_scraper import EnhancedFirecrawlClient, Config

async def analyze_design():
    client = EnhancedFirecrawlClient(Config.API_KEY)
    analyzer = DesignAnalyzer(client)

    # Full design analysis with screenshots
    analysis = await analyzer.analyze_full_design(
        url="https://example.com",
        output_dir=Path("./design_output"),
        include_screenshots=True,
        include_mobile=True
    )

    # Returns: design_system, components, ctas, psychology, animations
    print(f"Colors: {analysis['design_system']['color_palette']}")
    print(f"Typography: {analysis['design_system']['typography']}")
    print(f"CTAs found: {len(analysis['ctas']['ctas'])}")

    # Compare competitor designs
    comparison = await analyzer.compare_competitor_designs(
        urls=["https://competitor1.com", "https://competitor2.com"],
        output_dir=Path("./competitor_analysis")
    )

    print(f"Common patterns: {comparison['common_patterns']}")
    print(f"Differentiation opportunities: {comparison['differentiation_opportunities']}")

asyncio.run(analyze_design())
```

**Design Analysis Captures:**
- Full-page screenshots (desktop + mobile viewports)
- Color palette extraction (primary, secondary, accent, backgrounds)
- Typography analysis (fonts, sizes, weights)
- Component patterns (navigation, hero, sections, footer)
- CTA analysis (placement, style, conversion elements)
- Psychology insights (trust signals, social proof, urgency elements)
- Animation patterns (scroll effects, hover states, 3D elements)
- Competitor design comparison with differentiation opportunities

## 📊 Real Production Results

### Proven Performance

| Source | Pages | Size | Time | Success Rate |
|--------|-------|------|------|--------------|
| LangChain Docs | 109 | 1.3MB | 45 min | 100% |
| LangGraph Docs | 128 | 2.5MB | 1.5 hrs | 100% |
| ChromaDB Docs | 36 | 226KB | 15 min | 100% |
| Bricks Builder | 33 | 54KB | 12 min | 100% |
| BricksForge Docs | 33 | 317KB | 18 min | 100% |
| **TOTAL** | **568+** | **9MB+** | **~4 hrs** | **100%** |

### Stress Test Results

- **Longest Single Run**: 8+ hours overnight (unattended)
- **Largest Batch Job**: 13 sources scraped consecutively
- **Most Complex Site**: Multi-level WordPress documentation with anti-bot protection
- **Stealth Mode Success**: 100% success rate bypassing Cloudflare
- **Checkpoint Recovery**: 100% success rate resuming interrupted scrapes

## 🎯 Common Use Cases

### 1. **AI Training Data Collection**

Collect clean, structured text for training AI models:

```python
# Scrape technical documentation for AI training
config = {
    'url': 'https://docs.example.com/',
    'strategy': 'map',
    'max_pages': 500,
    'output_formats': ['markdown'],  # Clean text for training
    'category': 'ai-training-data'
}
```

### 2. **Design System Extraction**

Extract design patterns from professional websites:

```python
# Extract WordPress/Bricks Builder patterns
config = {
    'url': 'https://bricks.academy/tutorials/',
    'strategy': 'crawl',
    'output_formats': ['html', 'rawHtml', 'screenshot'],
    'category': 'design-patterns'
}
```

### 3. **Content Archival**

Archive websites for offline access or backup:

```python
# Complete site backup
config = {
    'url': 'https://blog.example.com/',
    'strategy': 'crawl',
    'output_formats': ['markdown', 'html', 'images'],
    'category': 'content-archive'
}
```

### 4. **Competitive Analysis**

Monitor competitor websites and pricing:

```python
# Extract structured product data
config = {
    'url': 'https://competitor.com/products',
    'strategy': 'extract',
    'extract_schema': {
        'name': 'string',
        'price': 'number',
        'description': 'string'
    },
    'category': 'competitive-intel'
}
```

### 5. **Research Data Collection**

Collect data from government, academic, or public sources:

```python
# Government data collection (.gov sites have no anti-bot)
config = {
    'url': 'https://www.cdc.gov/data/',
    'strategy': 'map',
    'filter_keywords': ['statistics', 'report', 'data'],
    'category': 'research-data'
}
```

## 📖 Output Formats

Firecrawl API v2.60 provides multiple output formats:

### Available Formats

- **markdown**: Clean, formatted text (best for AI training, reading)
- **html**: Cleaned HTML without clutter
- **rawHtml**: Original HTML with all elements
- **links**: All links found on the page
- **images**: All image URLs extracted
- **screenshot**: Full-page screenshot URL
- **json**: Structured data (when using EXTRACT strategy)

### Where Data is Saved

```
data/
├── category-name/           # Your category name
│   ├── metadata.json       # Scraping statistics and summary
│   ├── page-1.md          # Page content in markdown
│   ├── page-2.md
│   └── ...
└── _checkpoints/          # Automatic progress saves
```

## 🛡️ Anti-Bot Bypass (Stealth Mode)

This system automatically enables stealth mode for protected sites:

**Sites Successfully Bypassed:**
- Cloudflare-protected sites
- ACF Pro documentation (anti-scraping measures)
- GoHighLevel marketplace (Cloudflare + rate limiting)
- BricksForge documentation (rate limiting)

**How It Works:**
- Automatic difficulty detection
- Stealth mode auto-enabled for hard sites
- Increased delays and retry logic
- Success rate: 100% in production testing

## 💰 Cost Management

### Credit Costs (Firecrawl API v2.60)

- **CRAWL Strategy**: 1 credit/page (5 with stealth)
- **MAP Strategy**: 5 credits for sitemap + 1 credit/page
- **EXTRACT Strategy**: 15 credits/page

### Budget Enforcement

```python
# Set maximum credits to spend
config = {
    'url': 'https://large-site.com/',
    'strategy': 'map',
    'max_pages': 100,  # Stop at 100 pages
    'budget': 150      # Stop at 150 credits
}
```

### Production Cost Examples

- **LangChain Docs (109 pages)**: ~109 credits
- **With Stealth Mode**: ~545 credits (5x)
- **Large Site (500 pages)**: ~500-505 credits (MAP)

## 📚 Documentation

- **[USAGE.md](USAGE.md)** - Comprehensive usage guide with production findings
- **[DATA_FORMAT.md](DATA_FORMAT.md)** - Complete output format documentation
- **[REPOSITORY_SUMMARY.md](REPOSITORY_SUMMARY.md)** - Full system overview

## 🔧 Advanced Features

### Checkpoint/Resume System

Never lose progress on interrupted scrapes:

```python
# Scraping automatically saves progress
# If interrupted, just run again - it resumes automatically
result = await scraper.scrape_source(config)
```

### Batch Processing

Scrape multiple sources overnight:

```python
sources = [
    {'url': 'https://site1.com/', 'strategy': 'map'},
    {'url': 'https://site2.com/', 'strategy': 'crawl'},
    {'url': 'https://site3.com/', 'strategy': 'map'}
]

for source in sources:
    result = await scraper.scrape_source(source)
```

### Quality Validation

Automatic content quality checks:

- Minimum content length thresholds
- Duplicate page detection (SHA256 hashing)
- Invalid URL filtering
- Empty page detection

## 🧪 Testing

Validate installation:

```bash
# Run all 6 installation tests
python tests/test_installation.py

# Tests verify:
# - ✅ Core imports working
# - ✅ Configuration system
# - ✅ API key validation
# - ✅ Scraper initialization
# - ✅ Example scripts present
# - ✅ Documentation complete
```

## 🤝 Contributing

Contributions welcome! This is an MIT-licensed open-source project.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Credits

Built with [Firecrawl API v2.60](https://www.firecrawl.dev/) - The best web scraping API for developers.

## 🆘 Support

- **Documentation**: See USAGE.md and DATA_FORMAT.md
- **Issues**: Open a GitHub issue
- **Firecrawl Support**: https://www.firecrawl.dev/docs

---

**Ready to start scraping?** Install, configure your API key, and run `python examples/quick_start.py` to see it in action!
