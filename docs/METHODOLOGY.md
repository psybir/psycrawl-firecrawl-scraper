# Dan's Competitive Intelligence Methodology

## Overview

This document defines the systematic approach for analyzing local service businesses and generating actionable strategies. The methodology transforms raw competitive data into structured deliverables that AI agents and human teams can execute.

---

## The 5-Stage Pipeline

```
PLAN → COLLECT → NORMALIZE → SCORE → EXPORT
```

### Stage 1: PLAN
**Input:** Client configuration (services, locations, constraints)
**Output:** Intent/Geo Matrix

The matrix maps every service × location combination to determine:
- Page type needed (service, service-area, hub, etc.)
- Keyword clusters to target
- Content requirements
- Schema markup needs

### Stage 2: COLLECT
**Input:** Intent/Geo Matrix
**Output:** Source entities (SERP data, competitor URLs, GBP profiles)

Data sources:
- DataForSEO: SERP rankings, local pack, keyword data
- Firecrawl: Competitor website scraping
- GBP API: Business profiles, reviews

### Stage 3: NORMALIZE
**Input:** Raw source data
**Output:** Structured Competitor Profiles

Transforms messy scrape data into canonical schema:
- Trust signals (reviews, certs, photos)
- Conversion mechanics (CTAs, forms, booking)
- SEO structure (pages, schema, links)
- Backlink profile

### Stage 4: SCORE
**Input:** Competitor Profiles + Client context
**Output:** Findings → Actionable Insights

The critical "bridge" stage that answers "so what?":
- Pattern detection across competitors
- Gap analysis vs. client
- Opportunity scoring
- Priority ranking

### Stage 5: EXPORT
**Input:** Insights + Matrix
**Output:** Implementation-ready specs

Generates:
- Page map with routes
- Component specifications
- Content requirements
- Schema requirements
- LLM answer blocks

---

## Entity Relationships

```
CLIENT (Dent Sorcery, escape.exe)
    │
    ├── SERVICES (what they sell)
    │       └── money_service flag for revenue drivers
    │
    ├── LOCATIONS (where they serve)
    │       └── geo_bucket: 0-10, 10-30, 30-60, 60-90, 90+
    │
    └── CONSTRAINTS (operational limits)

COMPETITOR PROFILE
    │
    ├── TRUST SIGNALS
    │       ├── Universal: reviews, ratings, photos
    │       ├── Blue Collar: licenses, insurance, warranties
    │       ├── Entertainment: experience photos, awards, unique features
    │       └── Healthcare: credentials, certifications
    │
    ├── CONVERSION MECHANICS
    │       ├── Universal: CTAs, forms, chat
    │       ├── Blue Collar: emergency language, financing
    │       ├── Entertainment: online booking, packages
    │       └── Healthcare: scheduling, patient portal
    │
    └── SEO STRUCTURE
            ├── Page types present
            ├── Service area coverage
            └── Schema usage

FINDING → ACTIONABLE INSIGHT → OUTPUT SPEC
```

---

## Vertical Classification

### Blue Collar (Service Delivery Model)
Provider travels TO customer.

**Verticals:** PDR, Plumbing, HVAC, Roofing, Electrical, Landscaping, Auto Body

**Key Trust Signals:**
- Licenses and insurance visibility
- Before/after galleries
- Truck/equipment photos
- Warranty language

**Key Conversion:**
- Sticky click-to-call
- Emergency/24-7 language
- Free quote forms
- Financing options

### Entertainment (Destination Model)
Customer travels TO provider.

**Verticals:** Escape Room, Entertainment Venue, Amusement, Events

**Key Trust Signals:**
- Experience/venue photos
- Promo videos
- Awards and press mentions
- Unique feature highlights

**Key Conversion:**
- Online booking with calendar
- Group/party packages
- Corporate booking options
- Gift cards

### Healthcare (Hybrid Model)
Mix of in-office and some mobile services.

**Verticals:** Dental, MedSpa, Chiropractic

**Key Trust Signals:**
- Provider credentials
- Board certifications
- Patient testimonials

**Key Conversion:**
- Online scheduling
- Insurance checker
- Patient portal

---

## Insight Generation Rules

### Universal Rules (All Verticals)
1. **Backlink Gap Analysis** - Authority benchmarking
2. **Review Visibility** - Count and rating patterns
3. **Content Depth** - Page word counts
4. **Grid Rankings** - Local pack dominance
5. **Chat Widget Adoption** - Live chat presence

### Blue Collar Rules
1. **Certification Visibility** - License/insurance display
2. **Gallery Presence** - Before/after photos
3. **Service Area Coverage** - Location page count
4. **Sticky CTA** - Persistent call buttons
5. **Emergency Language** - 24/7 messaging

### Entertainment Rules
1. **Experience Photo Quality** - Venue imagery
2. **Online Booking System** - Direct booking capability
3. **Group Packages** - Party/corporate options
4. **Unique Experience Features** - Differentiators
5. **Repeat Visit Incentives** - Replay value

### Healthcare Rules
1. **Credential Display** - Provider qualifications
2. **Online Scheduling** - Appointment booking
3. **Patient Testimonials** - Social proof

---

## Priority Scoring

Insights are scored on two dimensions:

### Impact (What it achieves)
- **Rank Impact:** SEO ranking improvement
- **CVR Impact:** Conversion rate improvement
- **Trust Impact:** Credibility building
- **Speed Impact:** Time to results

### Effort (What it costs)
- **LOW:** < 1 week, minimal resources
- **MEDIUM:** 1-4 weeks, some resources
- **HIGH:** 4+ weeks, significant resources

### Priority Matrix
```
                    LOW EFFORT    MEDIUM EFFORT    HIGH EFFORT
HIGH IMPACT         🔥 DO FIRST   ✅ DO NEXT       📋 PLAN
MEDIUM IMPACT       ✅ DO NEXT    📋 PLAN          🤔 CONSIDER
LOW IMPACT          🤔 CONSIDER   ❌ SKIP          ❌ SKIP
```

---

## Output Deliverables

### 1. Client Brief (`{client}_brief.md`)
Executive summary for stakeholders:
- Business overview
- Current state analysis
- Key opportunities
- Recommended priorities

### 2. Competitive Analysis (`{client}_competitive.md`)
Detailed competitor breakdown:
- Competitor profiles
- Threat assessment
- Gap analysis
- Benchmark data

### 3. Implementation Spec (`{client}_implementation.md`)
Technical build instructions:
- Page map with routes
- Component requirements
- Schema specifications
- Internal linking rules

### 4. Content Brief (`{client}_content.md`)
For content creators/AI:
- Page-by-page content requirements
- LLM answer blocks
- FAQ specifications
- Keyword targets per page

### 5. SEO Strategy (`{client}_seo.md`)
For SEO execution:
- Keyword strategy by geo
- Backlink targets
- Schema checklist
- Technical requirements

---

## AI Agent Handoff Protocol

Each markdown file includes:

1. **Context Header**
   - Client name and vertical
   - Generated timestamp
   - Data freshness indicators

2. **Structured Sections**
   - Clear headings for parsing
   - Bullet points over paragraphs
   - Tables for comparative data

3. **Action Items**
   - Explicit next steps
   - Priority indicators
   - Dependencies noted

4. **Data References**
   - Source citations
   - Confidence levels
   - Raw data locations

### Agent Routing

| Deliverable | Target Agent | Purpose |
|-------------|--------------|---------|
| Client Brief | Strategy Agent | High-level planning |
| Competitive Analysis | Research Agent | Deep-dive analysis |
| Implementation Spec | Builder Agent | Site construction |
| Content Brief | Content Agent | Copy generation |
| SEO Strategy | SEO Agent | Optimization execution |

---

## Quality Gates

Before handoff, verify:

- [ ] All required sections populated
- [ ] No placeholder text remaining
- [ ] Data points have sources
- [ ] Priorities are assigned
- [ ] Action items are specific
- [ ] Dependencies are documented
