# PsyCrawl Firecrawl Scraper - Repository Summary

## Repository Status: v4.0 PRODUCTION READY

**PsyCrawl** is a professional web scraping and competitive intelligence system built on Firecrawl API v2, featuring the **Psybir Skills System** for decision-grade analysis with geo-context.

## What's New in v4.0

### Psybir Skills System
- **`/competitor_intel`** - Competitor analysis with SWOT, pricing, trust signals
- **`/seo_audit`** - 5-tier prioritized SEO analysis
- **3D Scoring** - Local Pack, Organic Local, Domestic Organic probabilities
- **Geo-Tagging** - All findings tagged with geographic context
- **Natural Language Routing** - Query in plain English

### CLI Interface
```bash
# List available skills
psycrawl skill list

# Run competitor analysis
psycrawl skill run competitor_intel https://competitor.com --geo "City Name"

# Run SEO audit
psycrawl skill run seo_audit https://yoursite.com --geo "City Name"

# Natural language query
psycrawl nlp "analyze my competitor in Chicago"
```

## Repository Structure

```
psycrawl-firecrawl-scraper/
├── README.md                           # Quick start guide
├── USAGE.md                            # Comprehensive usage guide
├── DATA_FORMAT.md                      # Output format documentation
├── LICENSE                             # MIT License
├── .env.example                        # Environment template
├── .gitignore                          # Exclusions (data/, .env, .psycrawl/)
├── requirements.txt                    # Python dependencies
├── setup.py                            # Package installation
│
├── firecrawl_scraper/                  # Main package
│   ├── __init__.py                     # Public API exports
│   ├── config.py                       # Centralized configuration
│   ├── cli.py                          # CLI with skill commands (NEW)
│   │
│   ├── core/
│   │   └── firecrawl_client.py        # Enhanced Firecrawl API client
│   │
│   ├── extraction/
│   │   └── universal_scraper.py       # Universal scraper (3 strategies)
│   │
│   ├── skills/                         # Psybir Skills System (NEW)
│   │   ├── __init__.py                # Skill loader & discovery
│   │   ├── base.py                    # BaseSkill, 3D Scoring, GeoContext
│   │   ├── router.py                  # NL intent detection
│   │   ├── context.py                 # Persistent context management
│   │   ├── output.py                  # Report generation
│   │   │
│   │   ├── competitor_intel/          # Competitor analysis skill
│   │   │   ├── skill.py
│   │   │   └── SKILL.md
│   │   │
│   │   └── seo_audit/                 # SEO audit skill
│   │       ├── skill.py
│   │       └── SKILL.md
│   │
│   ├── exports/                        # Export formatters
│   ├── models/                         # Data models
│   ├── pipelines/                      # Processing pipelines (NEW)
│   ├── loaders/                        # Data loaders (NEW)
│   └── integrations/                   # External integrations (NEW)
│
├── docs/                               # Documentation
│   ├── SKILLS_SYSTEM.md               # Skills system guide (NEW)
│   ├── LOCAL_SEO_SYSTEM_GUIDE.md
│   └── templates/
│       └── product-context.template.md
│
├── examples/                           # Production-tested examples
│   ├── quick_start.py
│   ├── batch_scraping.py
│   └── advanced_use_cases.py
│
└── tests/                              # Test framework
    └── test_installation.py
```

## Key Features

### 1. Psybir Skills System (v4.0)
- Modular skill architecture
- Decision-grade output with evidence
- Geo-tagged findings for local SEO
- 3D scoring (Local Pack, Organic, Domestic)
- Natural language routing

### 2. Web Scraping (v1.0-v3.0)
- Three strategies: CRAWL, MAP, EXTRACT
- Stealth mode for anti-bot bypass
- Checkpoint/resume system
- Batch processing with progress tracking

### 3. SEO & Research
- DataForSEO integration
- Local SEO research system
- Competitor intelligence
- Technical SEO audits

### 4. Export Formats
- Markdown reports
- JSON structured data
- Client briefs
- SEO strategy documents

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/psybir/psycrawl-firecrawl-scraper
cd psycrawl-firecrawl-scraper

# 2. Install
pip install -e .

# 3. Configure
cp .env.example .env
# Edit .env with your FIRECRAWL_API_KEY

# 4. Run
psycrawl skill list
psycrawl skill run competitor_intel https://competitor.com --geo "Your City"
```

## Configuration

All configuration via `.env` file:

```bash
# Required
FIRECRAWL_API_KEY=fc-your-api-key

# Optional - DataForSEO
DATAFORSEO_LOGIN=your_email
DATAFORSEO_PASSWORD=your_password
DATAFORSEO_ENABLED=true

# Skills System
SKILLS_ENABLED=true
DEFAULT_GEO_SCOPE=local_radius
```

## Production Results

| Feature | Status | Notes |
|---------|--------|-------|
| Scraping (568+ pages) | Proven | 100% success rate |
| Skills System | v4.0 | competitor_intel, seo_audit |
| 3D Scoring | Working | Local Pack, Organic, Domestic |
| NL Routing | Working | 72-100% confidence |
| Context Persistence | Working | Cross-session context |

## Version History

| Version | Features |
|---------|----------|
| v4.0 | Psybir Skills System, CLI, 3D Scoring, Geo-Tagging |
| v3.0 | Vertical-aware pipeline, markdown exports |
| v2.1 | Multi-page design analysis |
| v2.0 | UI/UX Design Analyzer |
| v1.0 | Core scraping, Local SEO system |

## Security

- All API keys from environment variables
- `.env` excluded from git
- `.psycrawl/` (user context) excluded
- `data/` (outputs) excluded
- No hardcoded credentials

## Documentation

- `README.md` - Quick start
- `USAGE.md` - Comprehensive guide
- `DATA_FORMAT.md` - Output formats
- `docs/SKILLS_SYSTEM.md` - Skills system guide

---

**Version**: 4.0.0
**License**: MIT
**Status**: Production Ready
