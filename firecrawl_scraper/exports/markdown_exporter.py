"""
Markdown Exporter - Main orchestrator for generating all deliverables

Coordinates generation of all markdown files from pipeline results.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from ..models import (
    Client,
    IntentGeoMatrix,
    CompetitorProfile,
    FindingsReport,
    InsightReport,
    OutputSpec,
)
from ..pipeline.orchestrator import PipelineResult

logger = logging.getLogger(__name__)


class MarkdownExporter:
    """Generate all markdown deliverables from pipeline results"""

    def __init__(
        self,
        client: Client,
        pipeline_result: PipelineResult,
        output_dir: Optional[str] = None
    ):
        self.client = client
        self.result = pipeline_result
        self.output_dir = Path(output_dir) if output_dir else Path("./output") / client.id / "deliverables"
        self.generated_files: List[Path] = []

    def export_all(self) -> Dict[str, Path]:
        """Generate all markdown deliverables"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        files = {}

        # Generate each deliverable
        files['brief'] = self._export_client_brief()
        files['competitive'] = self._export_competitive_analysis()
        files['implementation'] = self._export_implementation_spec()
        files['content'] = self._export_content_brief()
        files['seo'] = self._export_seo_strategy()

        # Generate index file
        files['index'] = self._export_index(files)

        logger.info(f"Exported {len(files)} deliverables to {self.output_dir}")
        return files

    def _export_client_brief(self) -> Path:
        """Generate client brief markdown"""
        from .client_brief import ClientBriefGenerator

        generator = ClientBriefGenerator(
            client=self.client,
            matrix=self.result.matrix,
            insights=self.result.insights_report,
            findings=self.result.findings_report
        )

        content = generator.generate()
        filepath = self.output_dir / f"{self.client.id}_brief.md"
        filepath.write_text(content)

        logger.info(f"Generated client brief: {filepath}")
        return filepath

    def _export_competitive_analysis(self) -> Path:
        """Generate competitive analysis markdown"""
        from .competitive_analysis import CompetitiveAnalysisGenerator

        generator = CompetitiveAnalysisGenerator(
            client=self.client,
            competitors=self.result.competitor_profiles or [],
            findings=self.result.findings_report
        )

        content = generator.generate()
        filepath = self.output_dir / f"{self.client.id}_competitive.md"
        filepath.write_text(content)

        logger.info(f"Generated competitive analysis: {filepath}")
        return filepath

    def _export_implementation_spec(self) -> Path:
        """Generate implementation spec markdown"""
        from .implementation_spec import ImplementationSpecGenerator

        generator = ImplementationSpecGenerator(
            client=self.client,
            output_spec=self.result.output_spec,
            matrix=self.result.matrix,
            insights=self.result.insights_report
        )

        content = generator.generate()
        filepath = self.output_dir / f"{self.client.id}_implementation.md"
        filepath.write_text(content)

        logger.info(f"Generated implementation spec: {filepath}")
        return filepath

    def _export_content_brief(self) -> Path:
        """Generate content brief markdown"""
        from .content_brief import ContentBriefGenerator

        generator = ContentBriefGenerator(
            client=self.client,
            output_spec=self.result.output_spec,
            matrix=self.result.matrix
        )

        content = generator.generate()
        filepath = self.output_dir / f"{self.client.id}_content.md"
        filepath.write_text(content)

        logger.info(f"Generated content brief: {filepath}")
        return filepath

    def _export_seo_strategy(self) -> Path:
        """Generate SEO strategy markdown"""
        from .seo_strategy import SEOStrategyGenerator

        generator = SEOStrategyGenerator(
            client=self.client,
            matrix=self.result.matrix,
            insights=self.result.insights_report,
            output_spec=self.result.output_spec
        )

        content = generator.generate()
        filepath = self.output_dir / f"{self.client.id}_seo.md"
        filepath.write_text(content)

        logger.info(f"Generated SEO strategy: {filepath}")
        return filepath

    def _export_index(self, files: Dict[str, Path]) -> Path:
        """Generate index file linking all deliverables"""
        content = self._generate_index_content(files)
        filepath = self.output_dir / "README.md"
        filepath.write_text(content)

        logger.info(f"Generated index: {filepath}")
        return filepath

    def _generate_index_content(self, files: Dict[str, Path]) -> str:
        """Generate index markdown content"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            f"# {self.client.name} - Strategy Deliverables",
            "",
            f"**Generated:** {timestamp}",
            f"**Vertical:** {self.client.vertical.value}",
            f"**Pipeline Status:** {self.result.status}",
            "",
            "---",
            "",
            "## Deliverables",
            "",
            "| Document | Purpose | Target Agent |",
            "|----------|---------|--------------|",
            f"| [{self.client.id}_brief.md](./{self.client.id}_brief.md) | Executive summary | Strategy Agent |",
            f"| [{self.client.id}_competitive.md](./{self.client.id}_competitive.md) | Competitor analysis | Research Agent |",
            f"| [{self.client.id}_implementation.md](./{self.client.id}_implementation.md) | Build specifications | Builder Agent |",
            f"| [{self.client.id}_content.md](./{self.client.id}_content.md) | Content requirements | Content Agent |",
            f"| [{self.client.id}_seo.md](./{self.client.id}_seo.md) | SEO execution plan | SEO Agent |",
            "",
            "---",
            "",
            "## Pipeline Summary",
            "",
            f"- **Matrix Cells:** {len(self.result.matrix.cells) if self.result.matrix else 0}",
            f"- **Sources Collected:** {self.result.total_sources}",
            f"- **Competitor Profiles:** {self.result.total_competitors}",
            f"- **Findings:** {self.result.total_findings}",
            f"- **Actionable Insights:** {self.result.total_insights}",
            f"- **Pages to Generate:** {self.result.total_pages}",
            "",
            "---",
            "",
            "## Quick Start for AI Agents",
            "",
            "1. **Strategy Planning:** Start with `_brief.md` for context",
            "2. **Competitor Research:** Deep-dive with `_competitive.md`",
            "3. **Site Building:** Follow `_implementation.md` specs",
            "4. **Content Creation:** Use `_content.md` for page copy",
            "5. **SEO Optimization:** Execute `_seo.md` strategy",
            "",
            "---",
            "",
            "## Data Freshness",
            "",
            f"- **Generated:** {timestamp}",
            f"- **Data Sources:** Pipeline Stage 2 collection",
            f"- **Confidence Level:** {'High' if self.result.total_competitors >= 3 else 'Medium' if self.result.total_competitors >= 1 else 'Low (no competitor data)'}",
            "",
        ]

        if self.result.errors:
            lines.extend([
                "## Warnings",
                "",
            ])
            for error in self.result.errors:
                lines.append(f"- {error}")
            lines.append("")

        return "\n".join(lines)
