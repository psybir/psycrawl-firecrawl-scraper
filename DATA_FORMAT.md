# Data Format Guide

This document explains the output structure, formats, and how to use scraped data from Firecrawl Scraper.

## 📁 Output Directory Structure

All scraped data is saved in the `data/` directory (configurable via `FIRECRAWL_OUTPUT_DIR`):

```
data/
├── [source-category-1]/
│   ├── [source-category-1]-complete-docs.md    # Combined markdown (all pages)
│   ├── metadata.json                           # Scraping metadata
│   └── pages/                                  # Individual page files
│       ├── page-001.md
│       ├── page-002.md
│       ├── page-003.md
│       └── ...
│
├── [source-category-2]/
│   ├── [source-category-2]-complete-docs.md
│   ├── metadata.json
│   └── pages/
│
└── _checkpoints/                               # Resume checkpoints
    └── [run-name]-checkpoint.json
```

### Example: Real Output

```
data/
├── langchain/
│   ├── langchain-complete-docs.md              # 1.3MB combined file
│   ├── metadata.json                           # Scraping stats
│   └── pages/
│       ├── page-001.md                         # Agents documentation
│       ├── page-002.md                         # Chains documentation
│       ├── ...
│       └── page-109.md                         # 109 pages total
│
├── langgraph/
│   ├── langgraph-complete-docs.md              # 2.5MB combined file
│   ├── metadata.json
│   └── pages/                                  # 128 individual pages
│
└── chromadb/
    ├── chromadb-complete-docs.md               # 226KB combined file
    ├── metadata.json
    └── pages/                                  # 36 individual pages
```

## 📄 metadata.json Schema

Each scraped source includes a `metadata.json` file with complete scraping information:

```json
{
  "source": "https://langchain-ai.github.io/langgraph/",
  "name": "LangGraph Official Documentation",
  "tier": "Tier 2",
  "scraped_at": "2025-11-17T04:25:11.594668",
  "pages_scraped": 128,
  "total_chars": 2510503,
  "strategy": "map",
  "file": "/absolute/path/to/langgraph-complete-docs.md",
  "file_size_bytes": 2528131
}
```

### Fields Explained

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Original URL that was scraped |
| `name` | string | Human-readable name for the source |
| `tier` | string | Optional categorization (e.g., "Tier 1", "Tier 2") |
| `scraped_at` | string | ISO 8601 timestamp of scraping |
| `pages_scraped` | integer | Number of successfully scraped pages |
| `total_chars` | integer | Total characters across all pages |
| `strategy` | string | Scraping strategy used (crawl, map, extract) |
| `file` | string | Absolute path to combined markdown file |
| `file_size_bytes` | integer | File size in bytes |

## 📝 Combined Markdown File Format

The `[source]-complete-docs.md` file contains all pages in a single file:

```markdown
# Source Name

Scraped from: https://original-url.com/
Date: 2025-11-17 04:17:28
Pages: 109
Tier: Tier 2

================================================================================

## Page 1

[Content of page 1...]

--------------------------------------------------------------------------------

## Page 2

[Content of page 2...]

--------------------------------------------------------------------------------

## Page 3

[Content of page 3...]

... (continues for all pages)
```

### Use Cases

- **Search**: Use grep/ripgrep to search across all content
- **Indexing**: Feed into vector databases (ChromaDB, Pinecone, etc.)
- **Analysis**: Count tokens, extract keywords, analyze content
- **Archiving**: Single-file backups of documentation

## 📑 Individual Page Files

Located in `pages/` directory with sequential naming:

- `page-001.md` - First page
- `page-002.md` - Second page
- `page-XXX.md` - Subsequent pages

Each file contains pure markdown content from a single page.

### Use Cases

- **Granular Access**: Access specific documentation pages
- **Parallel Processing**: Process pages individually
- **Selective Indexing**: Index only relevant pages
- **Version Control**: Track changes page by page

## 🎨 Supported Output Formats

Firecrawl supports multiple output formats (configure in scrape options):

### 1. Markdown (Default)

Clean content without HTML tags.

**Pros**: Easy to read, searchable, indexable
**Use for**: Documentation, knowledge bases, blogs

```python
result = await scraper.scrape_source({
    'url': 'https://example.com/',
    'strategy': 'crawl',
    'formats': ['markdown']  # Default
})
```

### 2. HTML

Full HTML content with tags.

**Pros**: Preserves structure, styling information
**Use for**: Archiving, visual replication

```python
result = await scraper.scrape_source({
    'url': 'https://example.com/',
    'strategy': 'crawl',
    'formats': ['html']
})
```

### 3. Raw HTML

Unprocessed HTML straight from the page.

**Pros**: Complete preservation
**Use for**: Deep analysis, debugging

```python
result = await scraper.scrape_source({
    'url': 'https://example.com/',
    'strategy': 'crawl',
    'formats': ['rawHtml']
})
```

### 4. Links

Extracted links from pages.

**Pros**: Discover relationships, build site maps
**Use for**: Link analysis, navigation mapping

```python
result = await scraper.scrape_source({
    'url': 'https://example.com/',
    'strategy': 'crawl',
    'formats': ['links']
})
```

### 5. Images

Image URLs from pages.

**Pros**: Collect assets
**Use for**: Image downloading, asset management

```python
result = await scraper.scrape_source({
    'url': 'https://example.com/',
    'strategy': 'crawl',
    'formats': ['images']
})
```

### 6. Screenshots

Full-page screenshots.

**Pros**: Visual archiving
**Use for**: Design analysis, visual documentation

```python
result = await scraper.scrape_source({
    'url': 'https://example.com/',
    'strategy': 'crawl',
    'formats': ['screenshot']
})
```

### 7. JSON (Structured Data)

Extracted structured data using schema.

**Pros**: Database-ready, type-safe
**Use for**: E-commerce, news aggregation, structured content

```python
result = await scraper.scrape_source({
    'url': 'https://example.com/products',
    'strategy': 'extract',
    'formats': ['json'],
    'schema': {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'price': {'type': 'number'}
        }
    }
})
```

## 🔄 Using Scraped Data

### Example 1: Search Across Documentation

```bash
# Search for "authentication" across all scraped docs
grep -r "authentication" data/*/pages/*.md

# Count occurrences
grep -r -c "authentication" data/*/pages/*.md
```

### Example 2: Index into Vector Database

```python
import chromadb
from pathlib import Path

client = chromadb.Client()
collection = client.create_collection("documentation")

# Load all scraped pages
for md_file in Path("data").rglob("page-*.md"):
    with open(md_file, 'r') as f:
        content = f.read()
        collection.add(
            documents=[content],
            ids=[str(md_file)]
        )

# Query the collection
results = collection.query(
    query_texts=["How do I use agents?"],
    n_results=5
)
```

### Example 3: Analyze Content Statistics

```python
import json
from pathlib import Path

total_pages = 0
total_chars = 0
sources = []

for metadata_file in Path("data").rglob("metadata.json"):
    with open(metadata_file, 'r') as f:
        meta = json.load(f)
        total_pages += meta['pages_scraped']
        total_chars += meta['total_chars']
        sources.append(meta['name'])

print(f"Total sources: {len(sources)}")
print(f"Total pages: {total_pages:,}")
print(f"Total characters: {total_chars:,}")
print(f"Average chars per page: {total_chars // total_pages:,}")
```

### Example 4: Export to JSON

```python
import json
from pathlib import Path

# Convert markdown files to JSON
pages_data = []

for md_file in sorted(Path("data/langchain/pages").glob("page-*.md")):
    with open(md_file, 'r') as f:
        pages_data.append({
            'page_number': md_file.stem.split('-')[1],
            'content': f.read()
        })

# Save as JSON
with open('langchain_docs.json', 'w') as f:
    json.dump(pages_data, f, indent=2)
```

### Example 5: Generate Summary Report

```python
import json
from pathlib import Path
from datetime import datetime

report = {
    'generated_at': datetime.now().isoformat(),
    'sources': []
}

for metadata_file in Path("data").rglob("metadata.json"):
    with open(metadata_file, 'r') as f:
        meta = json.load(f)
        report['sources'].append({
            'name': meta['name'],
            'url': meta['source'],
            'pages': meta['pages_scraped'],
            'size_mb': meta['file_size_bytes'] / (1024 * 1024),
            'scraped_date': meta['scraped_at']
        })

print(json.dumps(report, indent=2))
```

## 🗄️ Data Management

### Backup Recommendations

```bash
# Compress scraped data for backup
tar -czf scraped-data-$(date +%Y-%m-%d).tar.gz data/

# Exclude checkpoints (temporary files)
tar -czf scraped-data.tar.gz --exclude='data/_checkpoints' data/
```

### Cleanup Old Data

```bash
# Remove data older than 30 days
find data/ -name "*.md" -mtime +30 -delete
find data/ -name "metadata.json" -mtime +30 -delete
```

### Storage Estimates

| Pages | Avg Page Size | Total Size Estimate |
|-------|---------------|---------------------|
| 100 | 10 KB | ~1 MB |
| 500 | 10 KB | ~5 MB |
| 1,000 | 10 KB | ~10 MB |
| 5,000 | 10 KB | ~50 MB |

**Real-world example**: 568 pages = 9 MB (average 16 KB per page)

## 📊 Quality Indicators

### Content Length Thresholds

- **Excellent**: >10,000 characters
- **Good**: 5,000-10,000 characters
- **Fair**: 1,000-5,000 characters
- **Poor**: <1,000 characters (logged as warning)

### Validation Checks

- Minimum content length (default: 1000 chars)
- Page count validation (expected vs actual)
- Duplicate detection (SHA256 hashing)
- URL validation (pre-scraping HTTP checks)

---

## 💡 Tips

1. **Keep metadata.json**: Essential for understanding scraping context
2. **Use combined files**: Easier for full-text search and indexing
3. **Archive checkpoints**: Resume interrupted scrapes
4. **Monitor file sizes**: Large files may need splitting
5. **Regular backups**: Compress and backup data directory regularly

For more information, see [README.md](README.md) for usage examples.

---

## 🎯 Skills System Output (v4.0)

The Psybir Skills System generates decision-grade reports in both Markdown and JSON formats.

### Skills Output Directory Structure

```
data/skills/
├── competitor_intel/
│   ├── competitor_intel-20260127-1200.md
│   └── competitor_intel-20260127-1200.json
└── seo_audit/
    ├── seo_audit-20260127-1200.md
    └── seo_audit-20260127-1200.json
```

### Markdown Report Format

```markdown
# Skill Name Analysis

_Generated: 2026-01-27 12:00_

## Geo Context

```yaml
geo_scope: local_radius
geo_bucket: 0-10
location_cluster: "City Name"
confidence_score: 1.00
```

## Executive Summary (Decision-Grade)

> **Choose Option A if**: [condition]
> **Choose Option B if**: [condition]

## 3D Scoring (Psybir)

| Metric | Score | Evidence |
|--------|-------|----------|
| Local Pack Probability | X% | [evidence] |
| Organic Local Probability | X% | [evidence] |
| Domestic Organic Probability | X% | [evidence] |

## Prioritized Findings

### P1. Critical (Blocking Issues)
| Issue | Evidence | Impact | Fix | Priority |

### P2. High Impact
| Issue | Evidence | Impact | Fix | Priority |

## Recommended Actions (Psybir Pipeline)
1. **Evidence**: [what was found]
2. **Hypothesis**: [what to do about it]
3. **Design**: [specific implementation]
4. **Measure**: [how to track success]

## Related Skills
- `/seo_audit` - Run for deeper analysis
```

### JSON Output Schema

```json
{
  "skill_name": "competitor_intel",
  "executed_at": "2026-01-27T12:00:00",
  "geo_context": {
    "geo_scope": "local_radius",
    "geo_bucket": "0-10",
    "location_cluster": "City Name",
    "confidence_score": 1.0,
    "service_areas": ["Area 1", "Area 2"]
  },
  "three_d_score": {
    "local_pack_probability": 40,
    "local_pack_evidence": "Address visible, 2 service areas",
    "organic_local_probability": 60,
    "organic_local_evidence": "3 services listed, local testimonials",
    "domestic_organic_probability": 15,
    "domestic_organic_evidence": "3 differentiators"
  },
  "decision_statements": [
    {
      "choose_option": "Competitor A",
      "if_condition": "you need established credibility (878 reviews)"
    }
  ],
  "findings": [
    {
      "issue": "Missing LocalBusiness schema",
      "evidence": "Structured data analysis",
      "impact": "high",
      "fix": "Implement LocalBusiness JSON-LD with NAP",
      "priority": "P1",
      "category": "local_seo"
    }
  ],
  "raw_data": { ... },
  "related_skills": ["seo_audit", "local_seo"],
  "psybir_pipeline": {
    "evidence": "Analyzed competitor website",
    "hypothesis": "Weak on local SEO",
    "design": "Create location-specific pages",
    "measure": "Track local pack position"
  }
}
```

### 3D Scoring System

| Score | Local Pack | Organic Local | Domestic |
|-------|------------|---------------|----------|
| 0-20% | Minimal local signals | Needs optimization | Limited authority |
| 20-40% | Some local presence | Basic optimization | Building authority |
| 40-60% | Good local signals | Moderate optimization | Moderate authority |
| 60-80% | Strong local presence | Strong optimization | Good authority |
| 80-100% | Dominant local presence | Excellent optimization | Strong authority |

### Priority System

| Priority | Label | Typical Fix Time |
|----------|-------|------------------|
| P1 | Critical/Blocking | Immediate |
| P2 | High Impact | This week |
| P3 | Medium Priority | This month |
| P4 | Opportunities | Backlog |
| P5 | Nice-to-have | Future |

---

**Updated for v4.0** - See `docs/SKILLS_SYSTEM.md` for complete skills documentation.
