"""
Dan's 5-Stage Pipeline for Competitive Intelligence

Stage 1: PLAN - Generate Intent/Geo Matrix
Stage 2: COLLECT - DataForSEO + Firecrawl data collection
Stage 3: NORMALIZE - Raw data → Competitor Profiles
Stage 4: SCORE - Findings → Actionable Insights
Stage 5: EXPORT - Output Specs for Next.js generation
"""

from .stage_1_plan import PlanStage
from .stage_2_collect import CollectStage
from .stage_3_normalize import NormalizeStage
from .stage_4_score import ScoreStage
from .stage_5_export import ExportStage
from .orchestrator import PipelineOrchestrator

__all__ = [
    'PlanStage',
    'CollectStage',
    'NormalizeStage',
    'ScoreStage',
    'ExportStage',
    'PipelineOrchestrator',
]
