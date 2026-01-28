---
name: seo_audit
version: 1.0.0
description: |
  When the user wants to audit, review, or diagnose SEO issues on a site.
  Also use when they mention "SEO audit", "technical SEO", "why am I not ranking",
  "SEO issues", "on-page SEO", "meta tags review", "SEO health check",
  "local SEO audit", "crawlability", "indexation", or "Core Web Vitals".
  For building pages at scale, see programmatic_seo.
  For adding structured data, see schema_markup.
  For competitor SEO analysis, see competitor_intel.
---

# SEO Audit Skill

Perform **5-tier prioritized SEO audit** with geo-context for local businesses.

## Initial Assessment

**Check `.psycrawl/product-context.md` FIRST** for existing context.

Before audit, gather:

### 1. Target Context
- Website URL to audit
- Is this your site or a competitor?
- Current ranking concerns (if any)

### 2. Geographic Scope (Psybir Geo-Tagging)
- **geo_scope**: local_radius | multi_location | domestic
- **geo_bucket**: 0-10 | 10-30 | 30-60 | 60-90 | 90+ miles
- **location_cluster**: Named market area

### 3. Audit Depth
- **Quick scan** (Tier 1-2 only): Crawlability + Technical
- **Standard** (Tier 1-3): + On-page optimization
- **Comprehensive** (Tier 1-5): Full audit with authority analysis

### 4. Focus Areas
- Technical issues (speed, crawlability)
- Local SEO signals
- Content optimization
- AEO/GEO (AI search optimization)

## 5-Tier Audit Framework (Priority Order)

### Tier 1: Crawlability & Indexation (BLOCKING)
> "Can Google find and index your content?"

- [ ] Robots.txt analysis
- [ ] XML sitemap presence and validity
- [ ] Index coverage (via site: query)
- [ ] Canonical tag implementation
- [ ] Redirect chains (max 2 hops)
- [ ] HTTP status codes
- [ ] Mobile-first indexing readiness

**Blocking Issues** (P1):
- Accidental noindex tags
- Robots.txt blocking important content
- Missing sitemap
- Redirect loops

### Tier 2: Technical Foundations (HIGH)
> "Is the site fast and technically sound?"

- [ ] Core Web Vitals (LCP, FID, CLS)
- [ ] Mobile responsiveness
- [ ] HTTPS implementation
- [ ] Page speed (target <3s)
- [ ] JavaScript rendering issues
- [ ] Structured data errors
- [ ] Broken links (4xx errors)

**Critical Metrics**:
| Metric | Good | Needs Work | Poor |
|--------|------|------------|------|
| LCP | <2.5s | 2.5-4s | >4s |
| FID | <100ms | 100-300ms | >300ms |
| CLS | <0.1 | 0.1-0.25 | >0.25 |

### Tier 3: On-Page Optimization (MEDIUM)
> "Is content optimized for target keywords?"

- [ ] Title tag optimization (50-60 chars)
- [ ] Meta description (150-160 chars)
- [ ] H1 tag presence and optimization
- [ ] Header hierarchy (H1 → H2 → H3)
- [ ] Image alt text
- [ ] Internal linking structure
- [ ] URL structure
- [ ] Keyword placement (title, H1, first 100 words)

**Local On-Page Signals**:
- [ ] NAP consistency
- [ ] Local keywords in titles
- [ ] Service area mentions
- [ ] LocalBusiness schema

### Tier 4: Content Quality (MEDIUM)
> "Does the content deserve to rank?"

- [ ] Content depth (word count vs competitors)
- [ ] E-E-A-T signals (Experience, Expertise, Authority, Trust)
- [ ] Content freshness
- [ ] Duplicate content issues
- [ ] Thin content pages
- [ ] Topic coverage completeness
- [ ] User intent alignment

**Local Content Factors**:
- [ ] Location-specific pages
- [ ] Local case studies
- [ ] Community involvement content
- [ ] Local testimonials with attribution

### Tier 5: Authority & Links (LONG-TERM)
> "What credibility signals exist?"

- [ ] Domain authority metrics
- [ ] Backlink profile quality
- [ ] Anchor text distribution
- [ ] Local citations (NAP directories)
- [ ] Google Business Profile optimization
- [ ] Social signals
- [ ] Brand mentions

## Output Format (Decision-Grade)

### Geo Context Block
```yaml
geo_scope: [local_radius | multi_location | domestic]
geo_bucket: [0-10 | 10-30 | 30-60 | 60-90 | 90+]
location_cluster: "[Market Name]"
confidence_score: [0.0-1.0]
last_verified: [YYYY-MM-DD]
```

### Executive Summary
> Total issues found: X
> Critical (blocking): X
> High priority: X
> Quick wins: X

### 3D Scoring (Psybir)
| Metric | Score | Evidence |
|--------|-------|----------|
| Local Pack Probability | X% | [SEO signals observed] |
| Organic Local Probability | X% | [content/technical signals] |
| Domestic Organic Probability | X% | [authority signals] |

### Prioritized Findings by Tier
| Tier | Issue | Evidence | Impact | Fix | Priority |
|------|-------|----------|--------|-----|----------|
| 1 | [Crawlability issue] | [how found] | Critical | [fix] | P1 |
| 2 | [Technical issue] | [how found] | High | [fix] | P2 |
| ... | ... | ... | ... | ... | ... |

### Recommended Actions (Psybir Pipeline)
1. **Evidence**: Technical findings summary
2. **Hypothesis**: Expected ranking impact from fixes
3. **Design**: Prioritized fix sequence
4. **Measure**: Tracking setup (GSC, rank tracking)

## AEO/GEO Optimization (AI Search)

### AI Overview Optimization
- [ ] Clear, direct answers in content
- [ ] FAQ schema implementation
- [ ] Conversational query targeting
- [ ] Source attribution optimization

### Local AI Search Signals
- [ ] "Near me" query optimization
- [ ] Voice search friendly content
- [ ] Local entity recognition
- [ ] Geographic disambiguation

## Related Skills
- `/competitor_intel` - For SEO competitor analysis
- `/local_seo` - For Google Business Profile optimization
- `/schema_markup` - For structured data implementation
- `/content_gap` - For content opportunity analysis
