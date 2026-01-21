# Psybir Dashboard UI/UX and Sprint Roadmap

## Purpose
Build an operator-first dashboard for the Local Growth OS. The dashboard should turn strategy into daily execution and proof of ROI. Webuyabe is the test client for validating data quality, workflow fit, and reporting clarity.

## Users and usage modes
- Internal operator (daily): checks lead flow, ranks, QA issues, and pipeline health.
- Strategist (weekly): reviews coverage, trust, conversion, and what changed.
- Client owner (monthly): wants proof, plain language, and a clear next action.

## Feature parity and feature set

### Parity (must have to replace external tools)
- Geo rank tracking with trend deltas.
- GBP insights snapshots.
- Lead ingestion (forms, calls, CRM events).
- Basic reporting with weekly comparisons.

### Differentiation (Psybir moat)
- Intent map (service x location) coverage and gaps.
- pSEO pipeline visibility: planned -> published -> indexed -> ranking -> converting.
- Trust layer visibility (review velocity, freshness, proof assets).
- Money View with visibility, trust, conversion, attribution on one screen.

### Defer (later)
- Full citation management across 100+ directories.
- Deep competitor intelligence.
- Advanced BI and cohort reporting.

## Information architecture
- Money View (default landing).
- Rankings and Coverage.
- Leads and Attribution.
- Trust and Proof.
- pSEO Pipeline.
- Ops and QA.
- Settings (clients, sources, integrations).

## UI/UX guardrails
- Outcome-first: every view ties to visibility, trust, conversion, or attribution.
- Plain language: avoid SEO jargon; label metrics as "calls", "quotes", "reviews".
- Progressive disclosure: show summary first, detail on drill-down.
- Dense data, clear hierarchy: 4-6 KPIs per view, tabular numbers.
- Always show last updated and data source.
- Empty states must offer one clear next action.
- Errors must appear near the action that failed.

## Data model anchors (Payload)
- Clients, Services, Locations, IntentMap.
- Pages, PagePlans, PagePipelineStatus.
- Keywords, Rankings, SerpSnapshots.
- GBPInsights, Reviews, ProofAssets.
- Leads, Calls, Conversions, Attribution.
- Tasks, Notes, QAFindings.

## Logical sprint roadmap (2-week sprints)

### Sprint 0: Foundations
Goal: establish data model and dashboard shell.
- Define Payload collections and relationships.
- Create layout shell and navigation.
- Add basic auth and client switcher.
Success: can create a client and see empty states for all views.

### Sprint 1: Money View v1
Goal: single-screen executive view for Webuyabe.
- KPIs for visibility, trust, conversion, attribution.
- Date range and delta vs previous period.
- "What changed" list with top drivers.
Success: weekly update can be written from this screen alone.

### Sprint 2: Rankings and Coverage
Goal: replace BrightLocal rank view.
- DataForSEO ingestion and storage.
- Service x location coverage table.
- Rank buckets and trend deltas.
Success: can answer "where are we winning or losing" in 60 seconds.

### Sprint 3: Lead Flow and Attribution
Goal: lead visibility with simple attribution.
- Ingest form and call events.
- Unify lead statuses and sources.
- Define primary conversion event per client.
Success: can trace leads back to source and page group.

### Sprint 4: pSEO Pipeline
Goal: visibility into page production and index health.
- Page plan generator from intent map.
- Pipeline statuses with counts and blockers.
- Index checks and "stuck" alerts.
Success: can see if pages are blocked at publish or index.

### Sprint 5: Trust and Proof Layer
Goal: make trust measurable and improvable.
- Review ingestion and dedupe.
- Trust index (rating, velocity, recency).
- Proof asset freshness (photos, case studies).
Success: can explain trust gains and gaps in one view.

### Sprint 6: Ops and QA
Goal: prevent regressions and scale QA.
- Schema validation status.
- CWV/perf budget checks (pass/fail).
- Task and note tracking for operators.
Success: no release without QA pass.

### Sprint 7: Client-ready view (optional)
Goal: shareable view for clients.
- Limited, plain-language dashboard.
- Exportable weekly snapshot.
Success: clients can self-serve proof without support.

## Ongoing focus by sprint
- Keep Money View stable and trustworthy.
- Reduce time to answer core questions:
  - Are we more visible?
  - Do we look more trustworthy?
  - Are we converting better?
  - Can we prove it?
- Add only what directly improves those answers.
