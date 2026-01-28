# PsyCrawl Skills System

> **Psybir Evidence Engine** - Decision-grade intelligence with geo-context for local lead generation.

## Overview

The PsyCrawl Skills System provides modular, LLM-powered analysis capabilities built on top of Firecrawl's extraction API. Each skill produces structured, actionable output following the Psybir methodology:

- **3D Scoring**: Local Pack, Organic Local, and Domestic Organic probability scores
- **Geo-Tagging**: All findings tagged with geographic context
- **Decision Statements**: Clear "Choose X if Y" recommendations
- **Evidence-Based**: Every finding includes supporting evidence

## Installation

```bash
# Install psycrawl with skills support
pip install -e .

# Verify installation
python -m firecrawl_scraper.cli skill list
```

## Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Required
FIRECRAWL_API_KEY=fc-your-api-key-here

# Optional - DataForSEO integration
DATAFORSEO_LOGIN=your_email@example.com
DATAFORSEO_PASSWORD=your_api_password
DATAFORSEO_ENABLED=true
```

### Product Context (Optional)

Create `.psycrawl/product-context.md` to persist context across analyses:

```bash
mkdir -p .psycrawl
cp docs/templates/product-context.template.md .psycrawl/product-context.md
```

Edit with your business information for context-aware analysis.

## Available Skills

### `/competitor_intel`

Analyzes competitor websites for competitive intelligence.

**Triggers**: "competitor", "competition", "SWOT", "market analysis", "positioning"

**Output**:
- Company positioning and value proposition
- Pricing information
- Trust signals (testimonials, certifications, awards)
- Local presence signals (address, service areas, reviews)
- Key differentiators and weaknesses
- 3D scoring for competitive position

**Usage**:
```bash
# Direct skill invocation
python -m firecrawl_scraper.cli skill run competitor_intel https://example.com --geo "City Name"

# Natural language
python -m firecrawl_scraper.cli nlp "analyze competitor example.com in Chicago"
```

### `/seo_audit`

Performs 5-tier prioritized SEO analysis.

**Triggers**: "SEO audit", "SEO issues", "meta tags", "on-page SEO", "technical SEO"

**Tiers**:
1. **Crawlability & Indexation** (P1 - Blocking)
   - robots.txt check
   - XML sitemap verification
   - noindex/canonical analysis

2. **Technical Foundations** (P1-P2)
   - HTTPS verification
   - Viewport meta tag
   - Structured data detection

3. **On-Page Optimization** (P2-P3)
   - Title tag analysis
   - Meta description check
   - H1/heading structure
   - Local SEO signals

4. **Content Quality** (P3)
   - Content depth
   - E-E-A-T signals
   - Topic coverage

5. **Authority & Links** (P4-P5)
   - Social proof elements
   - External authority links

**Usage**:
```bash
# Standard audit (Tiers 1-3)
python -m firecrawl_scraper.cli skill run seo_audit https://example.com --geo "Miami"

# Comprehensive audit (all tiers)
python -m firecrawl_scraper.cli skill run seo_audit https://example.com --depth comprehensive
```

## CLI Commands

### List Skills
```bash
python -m firecrawl_scraper.cli skill list
```

### Skill Info
```bash
python -m firecrawl_scraper.cli skill info competitor_intel
python -m firecrawl_scraper.cli skill info seo_audit
```

### Run Skill
```bash
python -m firecrawl_scraper.cli skill run <skill-name> <url> [--geo <location>]
```

### Natural Language Routing
```bash
python -m firecrawl_scraper.cli nlp "<natural language query>"
```

Examples:
```bash
python -m firecrawl_scraper.cli nlp "analyze my competitor acme.com in Dallas"
python -m firecrawl_scraper.cli nlp "SEO audit for plumber website in Phoenix"
python -m firecrawl_scraper.cli nlp "competitor research escape rooms in Lehigh Valley"
```

## Output Format

### Markdown Report

Each skill generates a markdown report with:

```markdown
# Skill Name Analysis

## Geo Context
geo_scope: local_radius
location_cluster: "City Name"

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
...

## Recommended Actions (Psybir Pipeline)
1. **Evidence**: [what was found]
2. **Hypothesis**: [what to do about it]
3. **Design**: [specific implementation]
4. **Measure**: [how to track success]
```

### JSON Output

Structured JSON with full data:

```json
{
  "skill_name": "competitor_intel",
  "executed_at": "2026-01-27T12:00:00",
  "geo_context": {
    "geo_scope": "local_radius",
    "geo_bucket": "0-10",
    "location_cluster": "City Name"
  },
  "three_d_score": {
    "local_pack_probability": 40,
    "local_pack_evidence": "...",
    "organic_local_probability": 60,
    "organic_local_evidence": "...",
    "domestic_organic_probability": 15,
    "domestic_organic_evidence": "..."
  },
  "findings": [...],
  "raw_data": {...}
}
```

## 3D Scoring System

The Psybir 3D scoring system evaluates three dimensions:

### Local Pack Probability (0-100%)
Likelihood of ranking in Google's Local Pack (map results).

**Factors**:
- Google Business Profile signals
- Address visibility on website
- Phone number visibility
- Service areas defined
- Local testimonials
- Review count and rating

### Organic Local Probability (0-100%)
Likelihood of ranking in organic results for local searches.

**Factors**:
- Service listings
- Location pages
- Local content
- Local schema markup
- NAP consistency

### Domestic Organic Probability (0-100%)
Likelihood of ranking for non-local, national searches.

**Factors**:
- Case studies
- Differentiators
- Certifications
- Authority signals
- Content depth

## Priority System

Findings are categorized by priority:

| Priority | Label | Action Timeline |
|----------|-------|-----------------|
| P1 | Critical/Blocking | Immediate (blocks ranking) |
| P2 | High Impact | This week |
| P3 | Medium Priority | This month |
| P4 | Opportunities | Backlog |
| P5 | Nice-to-have | Future |

## Context Persistence

The system persists context in `.psycrawl/product-context.md`:

- **Business info**: Name, type, differentiators
- **Geography**: Primary market, service areas
- **Competitors**: Known competitors with URLs
- **Analysis history**: Previous skill runs

This enables:
- Skipping redundant questions
- Comparative analysis over time
- Context-aware recommendations

## Creating Custom Skills

See `firecrawl_scraper/skills/base.py` for the `BaseSkill` class.

Each skill must implement:

```python
class Skill(BaseSkill):
    @property
    def name(self) -> str:
        return "skill_name"

    def get_assessment_questions(self, existing_context: Dict) -> List[AssessmentQuestion]:
        """Return questions to ask if context is missing"""
        pass

    async def execute(self, context: Dict, answers: Dict) -> Dict[str, Any]:
        """Run the skill's main logic using Firecrawl"""
        pass

    def synthesize(self, data: Dict, geo_context: GeoContext) -> SkillResult:
        """Convert raw data into decision-grade output"""
        pass
```

## File Locations

```
firecrawl_scraper/
├── skills/
│   ├── __init__.py          # Skill loader and discovery
│   ├── base.py              # BaseSkill, GeoContext, 3D Scoring
│   ├── router.py            # Natural language intent detection
│   ├── competitor_intel/
│   │   ├── skill.py         # Competitor analysis skill
│   │   └── SKILL.md         # Skill documentation
│   └── seo_audit/
│       ├── skill.py         # SEO audit skill
│       └── SKILL.md         # Skill documentation
├── cli.py                   # CLI with skill commands

data/skills/                 # Output directory (gitignored)
├── competitor_intel/
│   ├── analysis-YYYYMMDD-HHMM.md
│   └── analysis-YYYYMMDD-HHMM.json
└── seo_audit/
    ├── audit-YYYYMMDD-HHMM.md
    └── audit-YYYYMMDD-HHMM.json

.psycrawl/                   # User context (gitignored)
└── product-context.md
```

## Troubleshooting

### "FIRECRAWL_API_KEY not found"
Create `.env` file with your API key.

### Extraction returns empty data
- Check URL is accessible
- Ensure Firecrawl API key has credits
- Try with `--depth quick` for faster results

### NL routing picks wrong skill
- Be more specific in query
- Use skill name directly: `skill run <name> <url>`

### Scores are all 0%
- Extraction may have failed
- Check raw_data in JSON output
- Verify URL is accessible
