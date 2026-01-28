---
name: competitor_intel
version: 1.0.0
description: |
  When the user wants to analyze competitors, understand market positioning,
  or research competitive landscape. Also use when they mention "competitor",
  "competition", "market analysis", "SWOT", "positioning", "local competitors",
  "competitors in [city/region]", "competitive landscape", or "market research".
  For SEO-specific competitor analysis, see seo_audit.
  For pricing focus, see pricing_intel.
  For local optimization, see local_seo.
---

# Competitor Intelligence Skill

Extract **decision-grade competitive intelligence** with geo-context for local lead generation.

## Initial Assessment

**Check `.psycrawl/product-context.md` FIRST** for existing context.

Before analysis, gather:

### 1. Target Context
- Competitor URL(s) to analyze
- Your business/product (for comparison baseline)
- Industry vertical

### 2. Geographic Scope (Psybir Geo-Tagging)
- **geo_scope**: local_radius | multi_location | domestic
- **geo_bucket**: 0-10 | 10-30 | 30-60 | 60-90 | 90+ miles
- **location_cluster**: Named market area (e.g., "Pittsburgh Metro")

### 3. Analysis Focus
- Positioning & messaging
- Pricing & packaging
- Features & capabilities
- Local presence & trust signals
- Comprehensive (all of above)

### 4. Decision Context
- What decision will this inform?
- Who will act on this analysis?

## Analysis Framework (Priority Order)

### 1. Local Presence Analysis (Highest Impact for Local Lead-Gen)
- Google Business Profile completeness
- NAP consistency (Name, Address, Phone)
- Local reviews count + sentiment
- Service area coverage
- Local schema markup

### 2. Trust Stack Analysis (Psybir Psychology)
> Visitor's 3-second test: "Are you legit and local?"
- Trust signals inventory
- Social proof elements
- Certifications/credentials
- Local testimonials
- Before/after galleries

### 3. Positioning & Messaging
- Core value proposition
- Target audience messaging
- Key differentiators claimed
- Unique selling points
- Messaging themes

### 4. Pricing Intelligence
See [references/pricing-matrix.md](references/pricing-matrix.md) for framework.
- Pricing model (per-project, hourly, package)
- Tier structure
- Hidden costs / add-ons
- Competitor price positioning

### 5. Feature/Service Comparison
- Service inventory
- Unique capabilities
- Service gaps (opportunities for you)
- Technical approach

## Output Format (Decision-Grade)

### Geo Context Block
```yaml
geo_scope: [local_radius | multi_location | domestic]
geo_bucket: [0-10 | 10-30 | 30-60 | 60-90 | 90+]
location_cluster: "[Market Name]"
confidence_score: [0.0-1.0]
last_verified: [YYYY-MM-DD]
```

### Executive Summary (Decision Statements)
> **Choose [Competitor] if**: [specific criteria]
> **Choose [You] if**: [specific criteria]

### 3D Scoring (Psybir)
| Metric | Score | Evidence |
|--------|-------|----------|
| Local Pack Probability | X% | [how determined] |
| Organic Local Probability | X% | [how determined] |
| Domestic Organic Probability | X% | [how determined] |

### Prioritized Findings Table
| Issue/Insight | Evidence | Impact | Recommendation | Priority |
|---------------|----------|--------|----------------|----------|
| [specific] | [how found] | [H/M/L] | [actionable] | [P1-P5] |

### SWOT Summary
See [references/swot-template.yaml](references/swot-template.yaml) for structure.

### Recommended Actions (Psybir Pipeline)
1. **Evidence**: What we discovered
2. **Hypothesis**: What we predict will happen
3. **Design**: What to build/change
4. **Measure**: How to track success

## Related Skills
- `/seo_audit` - For SEO-specific competitor analysis
- `/pricing_intel` - For deep pricing research using Van Westendorp
- `/local_seo` - For local pack optimization
- `/content_gap` - For content strategy gaps
