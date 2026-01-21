"""
Scoring Algorithms - Opportunity and priority scoring

Calculates priority scores for insights and opportunity scores for matrix cells.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from ..models import (
    ActionableInsight,
    ImpactLevel,
    EffortLevel,
    MatrixCell,
    Finding,
    Severity,
)


@dataclass
class ScoringWeights:
    """Configurable weights for scoring"""
    rank_impact: float = 0.35
    cvr_impact: float = 0.30
    trust_impact: float = 0.15
    speed_impact: float = 0.20


class PriorityCalculator:
    """Calculate priority scores for actionable insights"""

    def __init__(self, weights: ScoringWeights = None):
        self.weights = weights or ScoringWeights()

    def calculate(self, insight: ActionableInsight) -> float:
        """Calculate priority score (0-100)"""
        impact = insight.expected_impact

        # Impact level to numeric value
        impact_values = {
            ImpactLevel.HIGH: 1.0,
            ImpactLevel.MEDIUM: 0.6,
            ImpactLevel.LOW: 0.3,
            ImpactLevel.NONE: 0.0
        }

        # Effort level to multiplier (lower effort = higher score)
        effort_multipliers = {
            EffortLevel.LOW: 1.5,
            EffortLevel.MEDIUM: 1.0,
            EffortLevel.HIGH: 0.6
        }

        # Calculate weighted impact score
        weighted_score = (
            impact_values[impact.rank_impact] * self.weights.rank_impact +
            impact_values[impact.cvr_impact] * self.weights.cvr_impact +
            impact_values[impact.trust_impact] * self.weights.trust_impact +
            impact_values[impact.speed_impact] * self.weights.speed_impact
        )

        # Apply effort multiplier
        effort_mult = effort_multipliers[insight.effort_estimate]

        # Calculate final score
        score = weighted_score * effort_mult * 100

        # Bonus for quick wins (high impact + low effort)
        if insight.is_quick_win:
            score *= 1.2

        return min(score, 100)

    def rank_insights(self, insights: List[ActionableInsight]) -> List[ActionableInsight]:
        """Rank insights by priority score"""
        for insight in insights:
            insight.priority_score = self.calculate(insight)
        return sorted(insights, key=lambda x: x.priority_score, reverse=True)


class OpportunityScorer:
    """Calculate opportunity scores for matrix cells"""

    def __init__(
        self,
        search_volume_weight: float = 0.3,
        competition_weight: float = 0.25,
        rank_gap_weight: float = 0.25,
        money_service_weight: float = 0.2
    ):
        self.search_volume_weight = search_volume_weight
        self.competition_weight = competition_weight
        self.rank_gap_weight = rank_gap_weight
        self.money_service_weight = money_service_weight

    def score_cell(
        self,
        cell: MatrixCell,
        is_money_service: bool = True,
        search_volume: int = 0,
        competition: str = "medium"
    ) -> float:
        """Calculate opportunity score for a matrix cell"""
        score = 50.0  # Base score

        # Search volume factor (0-30 points)
        if search_volume > 0:
            volume_score = min(search_volume / 1000 * 30, 30)
            score += volume_score * self.search_volume_weight

        # Competition factor (0-25 points, lower = better)
        competition_scores = {"low": 25, "medium": 15, "high": 5}
        score += competition_scores.get(competition, 15) * self.competition_weight

        # Rank gap factor (0-25 points)
        if cell.current_rank and cell.target_rank:
            gap = cell.current_rank - cell.target_rank
            if gap > 0:
                gap_score = min(gap * 2, 25)
                score += gap_score * self.rank_gap_weight

        # Money service bonus
        if is_money_service:
            score += 20 * self.money_service_weight

        # Geo bucket factor
        bucket_bonuses = {
            "0-10": 15,
            "10-30": 10,
            "30-60": 5,
            "60-90": 0,
            "90+": -5
        }
        score += bucket_bonuses.get(cell.geo_bucket, 0)

        return min(max(score, 0), 100)

    def rank_cells(self, cells: List[MatrixCell]) -> List[MatrixCell]:
        """Rank cells by opportunity score"""
        for cell in cells:
            cell.priority_score = self.score_cell(cell)
        return sorted(cells, key=lambda x: x.priority_score, reverse=True)


class FindingSeverityScorer:
    """Score findings by severity and actionability"""

    SEVERITY_WEIGHTS = {
        Severity.CRITICAL: 1.0,
        Severity.HIGH: 0.75,
        Severity.MEDIUM: 0.5,
        Severity.LOW: 0.25
    }

    @classmethod
    def score(cls, finding: Finding) -> float:
        """Calculate finding priority score"""
        base_score = cls.SEVERITY_WEIGHTS[finding.severity] * 100

        # Bonus for actionable findings
        if finding.is_actionable:
            base_score *= 1.2

        # Confidence adjustment
        base_score *= finding.confidence

        return min(base_score, 100)

    @classmethod
    def rank_findings(cls, findings: List[Finding]) -> List[Finding]:
        """Rank findings by priority"""
        scored = [(f, cls.score(f)) for f in findings]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [f for f, _ in scored]
