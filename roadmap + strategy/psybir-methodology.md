# Psybir Methodology & Data Pipeline

## Why this document exists
Psybir is not “web design.” It’s a repeatable, data-driven **local lead engine** methodology that turns evidence into decisions, and decisions into high-performing websites.

At the core is a closed-loop system:

**Evidence → Hypothesis → Design → Build → Measure → Iterate**

Most agencies start at **Design**. Psybir starts at **Evidence** and keeps iterating after launch. That’s the difference between a site that looks good and a site that **prints leads**.

---

## 1) Evidence: what data we use (and why)
We use data to answer one question:

**What makes a local buyer trust this business enough to act right now?**

### Inputs (collected before building)
- **Search intent + demand:** how people phrase problems, seasonal shifts, urgency signals.
- **Local SERP reality:** who ranks (map pack + organic), what their pages emphasize, what proof they show.
- **Conversion friction:** where people hesitate (pricing anxiety, legitimacy concerns, response-time uncertainty).
- **Proof inventory:** reviews, photos, warranties, certifications, team, work examples, case studies.
- **Operational constraints:** service radius, availability, phone coverage, financing offered, lead handling quality.

**Key point:** We don’t design pages; we design **decisions**. The visitor is deciding “call / don’t call.” The page structure exists to win that decision.

---

## 2) Psychology: the rules we design around
Local lead-gen is mostly **anxiety management**.

In ~3 seconds the buyer is asking:
1. **Are you legit and local?**
2. **Can you solve my exact problem?**
3. **Is this going to be a headache or a scam?**

Pages are built from two systems:

### A) Trust Stack (reduce doubt fast)
We surface credibility early:
- Service area clarity (local cues)
- Licenses/insurance/certs (where relevant)
- Review count + rating + recent snippet
- Warranties/guarantees/risk reversal
- Real photos (work, team, trucks) to avoid “stock site” suspicion
- Process clarity (“what happens after I submit?”)

### B) Action Path (reduce effort fast)
We remove friction to acting:
- Sticky mobile call + short form
- Minimal fields (name / zip / issue / time preference)
- One primary CTA (no menu of 12 things)
- “Speed cues” only if operationally true (same-day, 24/7)
- Qualification logic when needed (big-ticket vs emergency)

**Psychology in one sentence:** lower perceived risk + lower action cost.

---

## 3) Translation: psychology → web design (practical rules)
This is where theory becomes repeatable implementation.

### Information hierarchy rules
- **1 page = 1 job to be done**
  - Example: “Water heater replacement” ≠ “Plumbing services”
- Above the fold must answer: **who, where, what, proof, action**
- Every section must “pay rent” by increasing **trust, clarity, or urgency**

### Copy rules (blue-collar specific)
- No poetic brand fluff. Use problem-language.
- State outcomes, timeframes, and next steps.
- Replace vague claims (“high quality”) with proof:
  - “1,200+ local jobs”
  - “5-year labor warranty”
  - “Licensed + insured”

### UI/UX rules (conversion mechanics)
- Sticky CTA on mobile is non-negotiable.
- Avoid choice overload (Hick’s Law): fewer primary actions.
- Reduce cognitive load: short paragraphs, scannable bullets, high contrast, obvious buttons.
- Make the next step explicit (Fogg-style: motivation is high; remove friction).

---

## 4) Local SEO strategy as a system (not “blog posts”)
Local SEO is a **coverage engine**.

### Page architecture that compounds
- **Service pages (money pages):** one per core service, built to convert.
- **Service-area pages (visibility pages):** one per target geography cluster, built to rank + route to service pages.
- **Proof assets (conversion multipliers):** reviews hub + galleries + case studies.
- **Internal linking rules (authority transfer):** location → service → proof → contact.

### Entity + trust signals (local ranking reality)
- Consistent NAP + service area signals
- Structured data (schema) where valid
- Review volume + recency patterns
- Real photos and “local-ness” embedded in content and proof

**Main idea:** build a **map of intent**, not random content.

---

## 5) Business approach: what we sell (a repeatable operating system)
### Phase 1: Diagnose & plan (evidence + hypothesis)
- Define the buyer journey + objections
- Identify missing proof
- Define the page map: services, locations, proof assets
- Define measurement: what counts as a lead vs a qualified lead

### Phase 2: Build the engine (design + implementation)
- Design tokens + component system (repeatable)
- Conversion-first layouts (trust stack + action path)
- Technical SEO implemented intentionally (routing, schema, metadata)
- Analytics + call/form tracking configured day one

### Phase 3: Optimize & scale (measure + iterate)
- Weekly: leads, qualified rate, call answer rate, drop-offs
- Monthly: ranking coverage, page performance, conversion lift tests
- Quarterly: expand service-area footprint + proof library + automation upgrades

**Differentiator:** launch is the middle, not the finish line.

---

## 6) What we measure (real instrumentation, not vanity)
### North Star outcomes
- Qualified leads per month
- Close rate (from CRM)
- Cost per qualified lead (when ads exist)
- Revenue impact (when accessible)

### Leading indicators (early warning signals)
- Call answer rate + speed to response
- Form completion rate
- GBP actions (calls, direction requests)
- Page-level conversion (service vs location pages)
- SERP coverage growth (more queries/pages winning)

### Constraint-based iteration logic
- If traffic is low → **coverage/SEO** problem
- If traffic exists but leads don’t → **trust/friction** problem
- If leads exist but closes don’t → **offer/ops/sales** problem

This is the systems engineer lens.

---

## 7) Method statement (one clean description)
**Psybir builds local lead engines by combining intent data (how people search), behavioral psychology (how people decide), and performance-first implementation (how fast and clean the experience is). We design pages to reduce buyer anxiety and friction, then instrument everything and iterate based on conversion and ranking data—not opinions.**

---

# The Data Pipeline Backbone (scraping → analysis → front-end decisions)
This pipeline is the backbone of every decision. It ties directly into UI/UX, site structure, content, local SEO, keywords, and functionality.

## Pipeline Box 1: Scrape Orchestrator + Normalized Data Store (Geo + Entity)
**Purpose:** convert messy web inputs into clean, comparable datasets.

### Inputs
- Competitor websites + landing pages
- Directories/review platforms (where relevant)
- Client assets (reviews, photos, offers, warranties)
- Location definitions + service radius constraints

### Stored entities (minimum viable schema)
**Location Entity**
- `location_id`
- `address`, `lat`, `lng`
- `service_radius_miles` (30/60/90)
- `primary_city`, `city_cluster[]`
- `county`, `state`
- `gbp_place_id` (if applicable)
- `NAP_variants`

**Service Area Model**
- `service_area_mode`: `radius | city_list | hybrid`
- `cities_in_radius[]` (derived)
- `domestic_targets[]` (statewide regions / national terms)

**Competitor Geo Context**
- competitor service area claims
- competitor GBP category + review density by city
- competitor presence by geo bucket

### Required tags on every datapoint
- `geo_scope`: `local_radius | multi_location | domestic`
- `geo_bucket`: `0–10 | 10–30 | 30–60 | 60–90 | 90+`
- `location_cluster`: e.g., “Lehigh Valley”, “Greater Philly”

**Why this exists:** prevents treating “Allentown plumbing” and “Pennsylvania plumbing” as the same problem.

---

## Pipeline Box 2: Feature Engineering + Statistical Scoring (Geo + Intent + SERP)
**Purpose:** convert normalized data into decision-grade scores and ranked opportunities.

### Scoring is 3-dimensional
You don’t have “SEO score.” You have:
- **Local Pack Probability** (map pack likelihood)
- **Organic Local Probability** (localized organic)
- **Domestic Organic Probability** (statewide / national)

### Three analysis layers per client
#### 1) Local radius layer (30–90 miles)
- City coverage completeness
- Competitor density by city (review count, category fit, proximity signals)
- Local proof strength (photos/reviews/NAP consistency/schema fields)
- Internal link mesh: location → service → proof

**Output:** `LocalCoverageMap`
- `cities_total`, `cities_covered`, `coverage_%`
- top opportunity cities (low competition / high intent)

#### 2) Multi-location layer (2+ physical offices)
- Duplicate content risk scoring
- Proof distribution per location (reviews/photos/case studies)
- Per-location GBP alignment (categories/services)
- Entity separation score (each location looks distinct and real)

**Output:** `MultiLocationEntityScorecard`
- per-location authority + uniqueness + consistency

#### 3) Domestic layer (statewide / national)
This is content architecture, not map pack.
- Topical authority scoring (topic/subtopic coverage)
- Informational clusters that feed money pages
- Intent funnel mapping: info → comparison → service → contact
- Mention/backlink opportunity planning

**Output:** `DomesticTopicMap + FunnelPlan`

---

## Pipeline Box 3: Front-End Blueprint + Content/SEO Spec Generator (Local + Domestic + LLM)
**Purpose:** translate analysis into build-ready artifacts for the front-end and content system.

### Outputs that directly drive Next.js + UI/UX
- **Information architecture:** page map, URL rules, navigation logic
- **Component spec:** which sections to use (hero variant, trust bar, review wall, gallery, FAQ)
- **Copy outline:** section messaging, objections, proof placement rules
- **Local SEO plan:** keyword clusters → page targets, internal linking rules, schema per page type
- **Functionality backlog:** booking vs quote form, financing flows, chat/SMS, CRM routing, review capture workflow

---

# Geo Scaling: Local radius → multi-location → domestic
## Local within 30–90 miles
We treat local SEO as a radius + cluster problem:
- The site must cover the radius via **city clusters**, not random city lists.
- Each cluster gets a location hub + supporting service-area pages.
- Proof and “local-ness” are distributed (photos, reviews, case studies).

## Multi-location
We treat each location as its own entity:
- Unique proof per location (not copy/paste)
- Location-specific service statements
- Entity separation to avoid cannibalization + thin duplication

## Domestic SEO
Domestic is topic authority:
- Build content clusters that earn visibility beyond map pack
- Funnel architecture routes domestic traffic to conversion pathways

---

# LLM SEO: being the answer (not just ranking)
LLM SEO is **structured, quotable, entity-clear content** that machines can reuse.

## LLM SEO deliverables produced by the blueprint
### 1) Entity & authority clarity package
- “About” blocks written like a knowledge graph entry:
  - legal name
  - locations
  - service area definition (radius + clusters)
  - primary services (canonical phrasing)
  - differentiators (warranty, response times, certifications)
- Consistent NAP + service statements across the site

### 2) Answer-ready content blocks (what assistants quote)
For each core service:
- What it is (1–2 sentences)
- When you need it (symptoms/triggers)
- Cost ranges + drivers (with disclaimers)
- How long it takes
- Risks of delaying
- How to choose a provider (criteria)
- What to expect (process steps)
- Clean FAQs with direct answers

### 3) Structured data + page structure rules
- Schema per page type:
  - LocalBusiness + Service (+ areasServed where appropriate)
  - FAQPage where valid
  - Review markup only where accurate/allowed
- Heading rules:
  - Local pages: H1 = service + geo intent
  - Domestic pages: topic authority structure (no city stuffing)
- Internal links reflect entity relationships:
  - Service ↔ Location ↔ Proof ↔ FAQ ↔ Contact

### 4) Mentions & citations plan (LLM SEO moat)
LLMs strongly weight credible third-party mentions.
Blueprint includes a mention plan:
- chambers/associations
- manufacturer dealer directories
- trade publications
- local news/features
- supplier/partner mentions
- reputable local directories (not spam)

---

# The missing visual: Geo/Intent Matrix
This is the control panel that drives all planning and generation.

**Rows:** Services

**Columns:**
- Local (0–30)
- Local (30–60)
- Local (60–90)
- Multi-location
- Domestic

**Each cell specifies:**
- target page type
- keyword cluster
- proof requirements
- CTA type (call/form/book)

This matrix prevents building the wrong pages for the wrong intent.

---

# Practical rule set (so we don’t build the wrong thing)
- **Local radius pages** win on proximity + proof + clarity.
- **Domestic pages** win on topical authority + depth + internal linking.
- **Multi-location** wins on entity separation + unique proof + local relevance.
- **LLM SEO** wins on clean entity statements + answer blocks + third-party mentions + structured data.

---

# Implementation notes (how this maps to the front-end)
- Component library = the “template system” (heroes, trust bars, proof blocks, FAQs, CTAs).
- The blueprint generator assigns components per page type + geo scope.
- QA gates ensure performance, schema, and conversion mechanics stay consistent.

