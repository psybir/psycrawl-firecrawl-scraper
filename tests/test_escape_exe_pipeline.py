"""
Test escape.exe pipeline - Entertainment vertical with full markdown export
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.clients.escape_exe import create_escape_exe_client
from firecrawl_scraper.pipeline.orchestrator import PipelineOrchestrator
from firecrawl_scraper.models import Vertical
from firecrawl_scraper.models.entities import ENTERTAINMENT_VERTICALS, get_business_model, BusinessModel
from firecrawl_scraper.exports.markdown_exporter import MarkdownExporter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_escape_exe_pipeline():
    """Run the full pipeline for escape.exe"""

    print("\n" + "=" * 60)
    print("TESTING ESCAPE.EXE PIPELINE")
    print("Entertainment Vertical Implementation")
    print("=" * 60 + "\n")

    # Create client
    client = create_escape_exe_client()

    # Verify entertainment vertical detection
    print("VERTICAL DETECTION TEST:")
    print(f"  - Vertical: {client.vertical}")
    print(f"  - Is Entertainment: {client.vertical in ENTERTAINMENT_VERTICALS}")
    print(f"  - Business Model: {get_business_model(client.vertical)}")
    print(f"  - Expected Business Model: {BusinessModel.DESTINATION}")
    assert client.vertical == Vertical.ESCAPE_ROOM
    assert client.vertical in ENTERTAINMENT_VERTICALS
    assert get_business_model(client.vertical) == BusinessModel.DESTINATION
    print("  ✓ Vertical detection PASSED\n")

    # Create orchestrator (no API clients - skip collection)
    orchestrator = PipelineOrchestrator(
        client=client,
        output_dir=str(Path(__file__).parent.parent / "output")
    )

    # Run pipeline (skipping collection since we don't have API credentials)
    print("RUNNING PIPELINE...")
    result = await orchestrator.run(skip_collection=True, existing_sources=[])

    # Print summary
    orchestrator.print_summary()

    # Verify results
    print("\nVERIFICATION:")
    print(f"  - Matrix cells: {len(result.matrix.cells) if result.matrix else 0}")
    print(f"  - Findings: {result.total_findings}")
    print(f"  - Insights: {result.total_insights}")
    print(f"  - Pages: {result.total_pages}")

    # Check that entertainment-specific rules were NOT skipped
    # (we should have findings even without competitors because some rules
    # create findings from patterns)

    if result.output_spec:
        print(f"\nOUTPUT SPEC PAGES ({len(result.output_spec.page_map)} total):")
        for page in result.output_spec.page_map[:10]:
            print(f"  - {page.route} ({page.page_type})")
        if len(result.output_spec.page_map) > 10:
            print(f"  ... and {len(result.output_spec.page_map) - 10} more")

    # ==================== MARKDOWN EXPORT ====================
    print("\n" + "=" * 60)
    print("EXPORTING MARKDOWN DELIVERABLES")
    print("=" * 60 + "\n")

    exporter = MarkdownExporter(
        client=client,
        pipeline_result=result,
        output_dir=str(Path(__file__).parent.parent / "output" / client.id / "deliverables")
    )

    files = exporter.export_all()

    print("GENERATED DELIVERABLES:")
    for name, filepath in files.items():
        print(f"  - {name}: {filepath.name}")

    print("\n" + "=" * 60)
    print("PIPELINE TEST COMPLETE")
    print("=" * 60 + "\n")

    print(f"\nDeliverables saved to: {exporter.output_dir}")
    print("\nThese files are ready for AI agent handoff:")
    print("  1. _brief.md      -> Strategy Agent")
    print("  2. _competitive.md -> Research Agent")
    print("  3. _implementation.md -> Builder Agent")
    print("  4. _content.md    -> Content Agent")
    print("  5. _seo.md        -> SEO Agent")

    return result


if __name__ == "__main__":
    result = asyncio.run(test_escape_exe_pipeline())
