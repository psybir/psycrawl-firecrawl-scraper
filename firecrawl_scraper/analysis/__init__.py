"""
Analysis Module - Insight rules and scoring algorithms

This module contains:
- Insight rules: Pattern-based rules for generating findings
- Scoring algorithms: Priority and opportunity scoring
- Matrix builders: Intent/Geo matrix generation helpers
"""

from .insight_rules import (
    InsightRule,
    BacklinkGapRule,
    ReviewVisibilityRule,
    CertificationCheckRule,
    GalleryPresenceRule,
    ServiceAreaCoverageRule,
    StickyCTARule,
    ChatWidgetRule,
    ContentDepthRule,
    GridRankingRule,
    RuleEngine,
)
from .scoring import OpportunityScorer, PriorityCalculator
from .matrix_builder import MatrixBuilder

__all__ = [
    'InsightRule',
    'BacklinkGapRule',
    'ReviewVisibilityRule',
    'CertificationCheckRule',
    'GalleryPresenceRule',
    'ServiceAreaCoverageRule',
    'StickyCTARule',
    'ChatWidgetRule',
    'ContentDepthRule',
    'GridRankingRule',
    'RuleEngine',
    'OpportunityScorer',
    'PriorityCalculator',
    'MatrixBuilder',
]
