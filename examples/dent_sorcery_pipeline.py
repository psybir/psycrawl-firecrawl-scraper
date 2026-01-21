"""
Dent Sorcery Pipeline Example

Demonstrates running the complete 5-stage pipeline for Dent Sorcery.

Usage:
    python examples/dent_sorcery_pipeline.py

This example:
1. Creates the Dent Sorcery client configuration
2. Runs Stage 1 (Plan) to generate Intent/Geo Matrix
3. Runs Stage 4 (Score) with mock competitor data
4. Runs Stage 5 (Export) to generate Output Spec
5. Prints summary and saves outputs
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.clients.dent_sorcery import (
    create_dent_sorcery_client,
    DENT_SORCERY_BASELINE,
    DENT_SORCERY_TARGETS
)
from firecrawl_scraper.pipeline import (
    PlanStage,
    ScoreStage,
    ExportStage,
    PipelineOrchestrator
)
from firecrawl_scraper.models import (
    CompetitorProfile,
    TrustSignals,
    ConversionMechanics,
    SEOStructure,
    BacklinkProfile,
    PhotoType,
    InsightReport,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_mock_competitor(
    domain: str,
    name: str,
    review_count: int = 50,
    rating: float = 4.5,
    has_gallery: bool = True,
    has_sticky_cta: bool = True,
    authority: int = 25,
    service_area_pages: int = 3
) -> CompetitorProfile:
    """Create a mock competitor profile for testing"""
    return CompetitorProfile(
        id=f"comp-{domain.replace('.', '-')}",
        domain=domain,
        name=name,
        url=f"https://{domain}",
        trust_signals=TrustSignals(
            review_count=review_count,
            rating=rating,
            licenses_shown=True,
            insurance_shown=True,
            certifications=["PDR Certified"],
            before_after_gallery=has_gallery,
            team_photos=True,
            real_photos_vs_stock=PhotoType.REAL
        ),
        conversion_mechanics=ConversionMechanics(
            phone_visible=True,
            phone_clickable=True,
            sticky_cta=has_sticky_cta,
            form_present=True,
            form_length=4,
            free_quote_language=True,
            multiple_cta_types=True,
            cta_types=["call", "form"]
        ),
        seo_structure=SEOStructure(
            page_count=15,
            page_types_present=["home", "service", "service-area", "about", "contact"],
            service_area_pages=[
                {"url": f"https://{domain}/service-area/{i}", "location": f"City {i}"}
                for i in range(service_area_pages)
            ],
            blog_active=authority > 20,
        ),
        backlinks=BacklinkProfile(
            domain_authority=authority,
            total_backlinks=authority * 5,
            referring_domains=authority * 2
        ),
        grid_performance={
            "Bethlehem": 2.0 + (50 - review_count) / 50,
            "Allentown": 3.0 + (50 - review_count) / 50,
        }
    )


def run_pipeline_demo():
    """Run a demo of the pipeline stages"""

    print("=" * 70)
    print("DENT SORCERY PIPELINE DEMO")
    print("=" * 70)

    # Step 1: Create client
    print("\n[1] Creating Dent Sorcery client configuration...")
    client = create_dent_sorcery_client()
    print(f"    Client: {client.name}")
    print(f"    Services: {len(client.services)} ({len(client.money_services)} money services)")
    print(f"    Locations: {len(client.locations)}")
    print(f"    Primary: {client.primary_location.name}")

    # Step 2: Run Stage 1 - Plan
    print("\n[2] Running Stage 1: PLAN...")
    plan_stage = PlanStage(client)
    matrix = plan_stage.run()
    print(f"    Generated Intent/Geo Matrix:")
    print(f"    - Rows (services): {len(matrix.rows)}")
    print(f"    - Columns (geo buckets): {len(matrix.columns)}")
    print(f"    - Cells: {len(matrix.cells)}")

    # Show matrix sample
    print("\n    Matrix Sample (first 5 cells):")
    for cell in matrix.cells[:5]:
        print(f"    - {cell.service_id} x {cell.geo_bucket}: {cell.page_strategy.value} -> {cell.page_type}")

    # Step 3: Create mock competitors (simulating Stage 2 & 3)
    print("\n[3] Creating mock competitor profiles (simulating Stage 2 & 3)...")
    competitors = [
        create_mock_competitor("lehighvalleypdr.com", "Lehigh Valley PDR", 75, 4.8, True, True, 30, 5),
        create_mock_competitor("dentprospa.com", "Dent Pros PA", 45, 4.6, True, False, 20, 2),
        create_mock_competitor("eastonpdr.com", "Easton PDR", 30, 4.4, False, True, 15, 1),
        create_mock_competitor("allentowndentrepair.com", "Allentown Dent Repair", 60, 4.7, True, True, 25, 4),
        create_mock_competitor("valleydentfix.com", "Valley Dent Fix", 20, 4.3, False, False, 10, 0),
    ]
    print(f"    Created {len(competitors)} competitor profiles")

    # Calculate threat levels
    for comp in competitors:
        comp.trust_signals.calculate_trust_score()
        comp.conversion_mechanics.calculate_conversion_score()
        comp.calculate_threat_level()

    print("\n    Competitor Threat Analysis:")
    for comp in competitors:
        print(f"    - {comp.name}: {comp.overall_threat_level.value} (Trust: {comp.trust_signals.trust_score:.0f}, Conv: {comp.conversion_mechanics.conversion_score:.0f})")

    # Step 4: Run Stage 4 - Score
    print("\n[4] Running Stage 4: SCORE...")
    score_stage = ScoreStage(client, competitors)
    findings_report, insights_report = score_stage.run()

    print(f"\n    Findings Report:")
    print(f"    - Total findings: {len(findings_report.findings)}")
    print(f"    - Gaps: {len(findings_report.gaps)}")
    print(f"    - Opportunities: {len(findings_report.opportunities)}")
    print(f"    - Critical: {len(findings_report.critical_findings)}")

    print(f"\n    Insights Report:")
    print(f"    - Total insights: {len(insights_report.insights)}")
    print(f"    - Quick wins: {len(insights_report.quick_wins)}")

    # Show top insights
    print("\n    Top 5 Priority Insights:")
    for insight in insights_report.get_top_priorities(5):
        print(f"    - [{insight.priority_score:.0f}] {insight.title}")
        print(f"      Problem: {insight.problem[:60]}...")
        print(f"      Action: {insight.spec_change[:60]}...")
        print()

    # Step 5: Run Stage 5 - Export
    print("\n[5] Running Stage 5: EXPORT...")
    export_stage = ExportStage(client, matrix, insights_report)
    output_spec = export_stage.run()

    print(f"\n    Output Spec Generated:")
    print(f"    - Total pages: {len(output_spec.page_map)}")
    print(f"    - Service pages: {len(output_spec.service_pages)}")
    print(f"    - Service area pages: {len(output_spec.service_area_pages)}")
    print(f"    - Components: {len(output_spec.component_set)}")
    print(f"    - Linking rules: {len(output_spec.internal_linking_rules)}")
    print(f"    - LLM blocks: {len(output_spec.llm_answer_blocks)}")

    # Show page map sample
    print("\n    Page Map Sample (first 10 pages):")
    for page in output_spec.page_map[:10]:
        print(f"    - {page.route} [{page.page_type.value}]")
        print(f"      Title: {page.title}")

    # Show LLM blocks sample
    if output_spec.llm_answer_blocks:
        print("\n    LLM Answer Block Sample:")
        block = output_spec.llm_answer_blocks[0]
        print(f"    Service: {block.service}")
        print(f"    Definition: {block.definition[:100]}...")
        print(f"    Triggers: {block.triggers[:3]}")
        print(f"    Process steps: {len(block.process_steps)} steps")

    # Summary
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    print(f"""
    Client: {client.name}

    Stage 1 (Plan):     {len(matrix.cells)} matrix cells generated
    Stage 2 (Collect):  Skipped (using mock data)
    Stage 3 (Normalize): {len(competitors)} competitor profiles
    Stage 4 (Score):    {len(findings_report.findings)} findings -> {len(insights_report.insights)} insights
    Stage 5 (Export):   {len(output_spec.page_map)} pages in output spec

    Quick Wins Identified: {len(insights_report.quick_wins)}

    Current Baseline:
    - Backlinks: {DENT_SORCERY_BASELINE['backlinks']}
    - Authority: {DENT_SORCERY_BASELINE['authority_score']}/100
    - Quakertown rank: {DENT_SORCERY_BASELINE['grid_rankings']['Quakertown']}

    Targets (3-6 months):
    - Backlinks: {DENT_SORCERY_TARGETS['backlinks']}
    - Authority: {DENT_SORCERY_TARGETS['authority_score']}/100
    - Quakertown rank: {DENT_SORCERY_TARGETS['grid_rankings']['Quakertown']}
    """)
    print("=" * 70)

    return {
        "client": client,
        "matrix": matrix,
        "competitors": competitors,
        "findings": findings_report,
        "insights": insights_report,
        "output_spec": output_spec
    }


async def run_full_pipeline():
    """Run the full pipeline with orchestrator (requires API clients)"""
    print("Full pipeline requires DataForSEO and Firecrawl clients.")
    print("Use run_pipeline_demo() for testing without API calls.")

    client = create_dent_sorcery_client()

    orchestrator = PipelineOrchestrator(
        client=client,
        dataforseo_client=None,  # Add your client here
        firecrawl_client=None,   # Add your client here
        output_dir="./output"
    )

    # Skip collection stage for demo
    result = await orchestrator.run(skip_collection=True, existing_sources=[])
    orchestrator.print_summary()

    return result


if __name__ == "__main__":
    # Run the demo
    results = run_pipeline_demo()

    # Uncomment to run full pipeline with API clients:
    # asyncio.run(run_full_pipeline())
