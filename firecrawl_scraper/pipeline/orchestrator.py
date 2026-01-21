"""
Pipeline Orchestrator - Run the complete 5-stage pipeline

Orchestrates:
Stage 1: PLAN - Generate Intent/Geo Matrix
Stage 2: COLLECT - DataForSEO + Firecrawl collection
Stage 3: NORMALIZE - Raw → Competitor Profiles
Stage 4: SCORE - Findings → Actionable Insights
Stage 5: EXPORT - Output Specs generation
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
import json
from pathlib import Path

from ..models import (
    Client,
    IntentGeoMatrix,
    Source,
    CompetitorProfile,
    FindingsReport,
    InsightReport,
    OutputSpec,
)

from .stage_1_plan import PlanStage
from .stage_2_collect import CollectStage
from .stage_3_normalize import NormalizeStage
from .stage_4_score import ScoreStage
from .stage_5_export import ExportStage

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Complete pipeline execution result"""
    client_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"

    # Stage outputs
    matrix: Optional[IntentGeoMatrix] = None
    sources: Optional[list] = None
    competitor_profiles: Optional[list] = None
    findings_report: Optional[FindingsReport] = None
    insights_report: Optional[InsightReport] = None
    output_spec: Optional[OutputSpec] = None

    # Stats
    total_sources: int = 0
    total_competitors: int = 0
    total_findings: int = 0
    total_insights: int = 0
    total_pages: int = 0

    # Errors
    errors: list = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "client_id": self.client_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "stats": {
                "total_sources": self.total_sources,
                "total_competitors": self.total_competitors,
                "total_findings": self.total_findings,
                "total_insights": self.total_insights,
                "total_pages": self.total_pages,
            },
            "errors": self.errors,
        }


class PipelineOrchestrator:
    """Orchestrate the complete 5-stage pipeline"""

    def __init__(
        self,
        client: Client,
        dataforseo_client=None,
        firecrawl_client=None,
        output_dir: Optional[str] = None
    ):
        self.client = client
        self.dataforseo_client = dataforseo_client
        self.firecrawl_client = firecrawl_client
        self.output_dir = Path(output_dir) if output_dir else Path("./output")

        # Pipeline state
        self.result = PipelineResult(
            client_id=client.id,
            started_at=datetime.now()
        )

    async def run(
        self,
        skip_collection: bool = False,
        existing_sources: list = None
    ) -> PipelineResult:
        """Run the complete pipeline"""
        logger.info(f"Starting pipeline for {self.client.name}")

        try:
            # Stage 1: Plan
            await self._run_stage_1()

            # Stage 2: Collect (can be skipped if data exists)
            if skip_collection and existing_sources:
                self.result.sources = existing_sources
                self.result.total_sources = len(existing_sources)
                logger.info("Stage 2: Using existing sources (skipped collection)")
            else:
                await self._run_stage_2()

            # Stage 3: Normalize
            await self._run_stage_3()

            # Stage 4: Score
            await self._run_stage_4()

            # Stage 5: Export
            await self._run_stage_5()

            # Mark complete
            self.result.status = "completed"
            self.result.completed_at = datetime.now()

            # Save outputs
            await self._save_outputs()

            logger.info(f"Pipeline completed successfully for {self.client.name}")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.result.status = "failed"
            self.result.errors.append(str(e))

        return self.result

    async def _run_stage_1(self):
        """Run Stage 1: Plan"""
        logger.info("=" * 50)
        logger.info("STAGE 1: PLAN")
        logger.info("=" * 50)

        try:
            stage = PlanStage(self.client)
            self.result.matrix = stage.run()
            logger.info(f"Generated matrix with {len(self.result.matrix.cells)} cells")
        except Exception as e:
            logger.error(f"Stage 1 failed: {e}")
            self.result.errors.append(f"Stage 1: {e}")
            raise

    async def _run_stage_2(self):
        """Run Stage 2: Collect"""
        logger.info("=" * 50)
        logger.info("STAGE 2: COLLECT")
        logger.info("=" * 50)

        try:
            stage = CollectStage(
                self.result.matrix,
                dataforseo_client=self.dataforseo_client,
                firecrawl_client=self.firecrawl_client
            )
            self.result.sources = await stage.run()
            self.result.total_sources = len(self.result.sources)
            logger.info(f"Collected {self.result.total_sources} sources")
        except Exception as e:
            logger.error(f"Stage 2 failed: {e}")
            self.result.errors.append(f"Stage 2: {e}")
            # Continue with empty sources if collection fails
            self.result.sources = []

    async def _run_stage_3(self):
        """Run Stage 3: Normalize"""
        logger.info("=" * 50)
        logger.info("STAGE 3: NORMALIZE")
        logger.info("=" * 50)

        try:
            stage = NormalizeStage(
                self.result.sources,
                firecrawl_client=self.firecrawl_client
            )
            self.result.competitor_profiles = await stage.run()
            self.result.total_competitors = len(self.result.competitor_profiles)
            logger.info(f"Built {self.result.total_competitors} competitor profiles")
        except Exception as e:
            logger.error(f"Stage 3 failed: {e}")
            self.result.errors.append(f"Stage 3: {e}")
            self.result.competitor_profiles = []

    async def _run_stage_4(self):
        """Run Stage 4: Score"""
        logger.info("=" * 50)
        logger.info("STAGE 4: SCORE")
        logger.info("=" * 50)

        try:
            stage = ScoreStage(
                self.client,
                self.result.competitor_profiles
            )
            self.result.findings_report, self.result.insights_report = stage.run()
            self.result.total_findings = len(self.result.findings_report.findings)
            self.result.total_insights = len(self.result.insights_report.insights)
            logger.info(f"Generated {self.result.total_findings} findings, {self.result.total_insights} insights")
        except Exception as e:
            logger.error(f"Stage 4 failed: {e}")
            self.result.errors.append(f"Stage 4: {e}")
            raise

    async def _run_stage_5(self):
        """Run Stage 5: Export"""
        logger.info("=" * 50)
        logger.info("STAGE 5: EXPORT")
        logger.info("=" * 50)

        try:
            stage = ExportStage(
                self.client,
                self.result.matrix,
                self.result.insights_report
            )
            self.result.output_spec = stage.run()
            self.result.total_pages = len(self.result.output_spec.page_map)
            logger.info(f"Generated output spec with {self.result.total_pages} pages")
        except Exception as e:
            logger.error(f"Stage 5 failed: {e}")
            self.result.errors.append(f"Stage 5: {e}")
            raise

    async def _save_outputs(self):
        """Save all outputs to files"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        client_dir = self.output_dir / self.client.id

        client_dir.mkdir(exist_ok=True)

        # Save matrix
        if self.result.matrix:
            matrix_path = client_dir / "intent_geo_matrix.json"
            with open(matrix_path, "w") as f:
                json.dump(self.result.matrix.model_dump(), f, indent=2, default=str)
            logger.info(f"Saved matrix to {matrix_path}")

        # Save findings
        if self.result.findings_report:
            findings_path = client_dir / "findings_report.json"
            with open(findings_path, "w") as f:
                json.dump(self.result.findings_report.model_dump(), f, indent=2, default=str)
            logger.info(f"Saved findings to {findings_path}")

        # Save insights
        if self.result.insights_report:
            insights_path = client_dir / "insights_report.json"
            with open(insights_path, "w") as f:
                json.dump(self.result.insights_report.model_dump(), f, indent=2, default=str)
            logger.info(f"Saved insights to {insights_path}")

        # Save output spec
        if self.result.output_spec:
            spec_path = client_dir / "output_spec.json"
            with open(spec_path, "w") as f:
                json.dump(self.result.output_spec.model_dump(), f, indent=2, default=str)
            logger.info(f"Saved output spec to {spec_path}")

        # Save summary
        summary_path = client_dir / "pipeline_summary.json"
        with open(summary_path, "w") as f:
            json.dump(self.result.to_dict(), f, indent=2)
        logger.info(f"Saved summary to {summary_path}")

    def get_quick_wins(self) -> list:
        """Get quick win insights (high impact, low effort)"""
        if not self.result.insights_report:
            return []
        return self.result.insights_report.quick_wins

    def get_top_priorities(self, n: int = 10) -> list:
        """Get top N priority insights"""
        if not self.result.insights_report:
            return []
        return self.result.insights_report.get_top_priorities(n)

    def print_summary(self):
        """Print pipeline execution summary"""
        print("\n" + "=" * 60)
        print(f"PIPELINE SUMMARY: {self.client.name}")
        print("=" * 60)
        print(f"Status: {self.result.status}")
        print(f"Started: {self.result.started_at}")
        print(f"Completed: {self.result.completed_at}")
        print()
        print("STATS:")
        print(f"  - Matrix Cells: {len(self.result.matrix.cells) if self.result.matrix else 0}")
        print(f"  - Sources Collected: {self.result.total_sources}")
        print(f"  - Competitor Profiles: {self.result.total_competitors}")
        print(f"  - Findings: {self.result.total_findings}")
        print(f"  - Actionable Insights: {self.result.total_insights}")
        print(f"  - Pages to Generate: {self.result.total_pages}")
        print()

        if self.result.errors:
            print("ERRORS:")
            for error in self.result.errors:
                print(f"  - {error}")
            print()

        if self.result.insights_report:
            quick_wins = self.get_quick_wins()
            if quick_wins:
                print("QUICK WINS (High Impact, Low Effort):")
                for insight in quick_wins[:5]:
                    print(f"  - {insight.title}: {insight.spec_change}")
            print()

        print("=" * 60)
