"""
Output Formatter - Decision-grade output for skills

Formats SkillResult into Psybir-aligned markdown reports:
- Geo context block
- 3D scoring table
- Decision statements
- Prioritized findings table
- Psybir Pipeline recommendations
- Related skills routing
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json
import yaml

from .base import (
    SkillResult,
    Finding,
    FindingImpact,
    FindingPriority,
    GeoContext,
    ThreeDScore,
    DecisionStatement,
)


class OutputFormatter:
    """
    Formats skill results into decision-grade reports.

    Supports multiple output formats:
    - Markdown (default, for human consumption)
    - JSON (for programmatic use)
    - YAML (for configuration/storage)
    """

    def __init__(self, skill_name: str):
        self.skill_name = skill_name

    def format_markdown(self, result: SkillResult) -> str:
        """Format SkillResult as Psybir-aligned markdown"""
        sections = []

        # Header
        sections.append(f"# {self._title_case(self.skill_name)} Analysis")
        sections.append("")
        sections.append(f"_Generated: {result.executed_at.strftime('%Y-%m-%d %H:%M')}_")
        sections.append("")

        # Geo Context
        sections.append(self._format_geo_context(result.geo_context))

        # Executive Summary (Decision Statements)
        if result.decision_statements:
            sections.append(self._format_decision_statements(result.decision_statements))

        # 3D Scoring
        if result.three_d_score:
            sections.append(self._format_three_d_score(result.three_d_score))

        # Prioritized Findings
        if result.findings:
            sections.append(self._format_findings(result.findings))

        # Psybir Pipeline Recommendations
        sections.append(self._format_psybir_pipeline(result))

        # Related Skills
        if result.related_skills:
            sections.append(self._format_related_skills(result.related_skills))

        return '\n'.join(sections)

    def _format_geo_context(self, geo: GeoContext) -> str:
        """Format geo context block"""
        lines = [
            "## Geo Context",
            "",
            "```yaml",
            f"geo_scope: {geo.geo_scope.value}",
            f"geo_bucket: {geo.geo_bucket.value}",
            f"location_cluster: \"{geo.location_cluster}\"",
            f"confidence_score: {geo.confidence_score:.2f}",
            f"last_verified: {geo.last_verified.strftime('%Y-%m-%d')}",
        ]

        if geo.service_areas:
            lines.append("service_areas:")
            for area in geo.service_areas:
                lines.append(f"  - \"{area}\"")

        lines.append("```")
        lines.append("")

        return '\n'.join(lines)

    def _format_decision_statements(self, statements: List[DecisionStatement]) -> str:
        """Format executive summary with decision statements"""
        lines = [
            "## Executive Summary (Decision-Grade)",
            "",
        ]

        for stmt in statements:
            lines.append(f"> {stmt}")
            lines.append(">")

        lines.append("")
        return '\n'.join(lines)

    def _format_three_d_score(self, score: ThreeDScore) -> str:
        """Format 3D scoring table"""
        lines = [
            "## 3D Scoring (Psybir)",
            "",
            "| Metric | Score | Evidence |",
            "|--------|-------|----------|",
            f"| Local Pack Probability | {score.local_pack_probability:.0f}% | {score.local_pack_evidence} |",
            f"| Organic Local Probability | {score.organic_local_probability:.0f}% | {score.organic_local_evidence} |",
            f"| Domestic Organic Probability | {score.domestic_organic_probability:.0f}% | {score.domestic_organic_evidence} |",
            "",
        ]

        return '\n'.join(lines)

    def _format_findings(self, findings: List[Finding]) -> str:
        """Format prioritized findings"""
        lines = ["## Prioritized Findings", ""]

        # Group by priority
        priority_groups = {
            FindingPriority.P1: ("Critical (Blocking Issues)", []),
            FindingPriority.P2: ("High Impact", []),
            FindingPriority.P3: ("Medium Priority", []),
            FindingPriority.P4: ("Quick Wins", []),
            FindingPriority.P5: ("Future Considerations", []),
        }

        for finding in findings:
            if finding.priority in priority_groups:
                priority_groups[finding.priority][1].append(finding)

        for priority, (label, group_findings) in priority_groups.items():
            if not group_findings:
                continue

            lines.append(f"### {priority.value}. {label}")
            lines.append("")
            lines.append("| Issue | Evidence | Impact | Fix | Priority |")
            lines.append("|-------|----------|--------|-----|----------|")

            for f in group_findings:
                impact_emoji = {
                    FindingImpact.CRITICAL: "!!",
                    FindingImpact.HIGH: "!",
                    FindingImpact.MEDIUM: "-",
                    FindingImpact.LOW: ".",
                    FindingImpact.INFO: "i",
                }.get(f.impact, "-")

                lines.append(
                    f"| {f.issue} | {f.evidence} | {impact_emoji} {f.impact.value} | {f.fix} | {f.priority.value} |"
                )

            lines.append("")

        return '\n'.join(lines)

    def _format_psybir_pipeline(self, result: SkillResult) -> str:
        """Format Psybir Pipeline recommendations"""
        lines = [
            "## Recommended Actions (Psybir Pipeline)",
            "",
        ]

        if result.evidence_summary:
            lines.append(f"1. **Evidence**: {result.evidence_summary}")
        if result.hypothesis:
            lines.append(f"2. **Hypothesis**: {result.hypothesis}")
        if result.design_recommendation:
            lines.append(f"3. **Design**: {result.design_recommendation}")
        if result.measure_plan:
            lines.append(f"4. **Measure**: {result.measure_plan}")

        if not any([result.evidence_summary, result.hypothesis,
                   result.design_recommendation, result.measure_plan]):
            lines.append("_No specific pipeline recommendations generated._")

        lines.append("")
        return '\n'.join(lines)

    def _format_related_skills(self, skills: List[str]) -> str:
        """Format related skills section"""
        lines = [
            "## Related Skills",
            "",
        ]

        for skill in skills:
            lines.append(f"- `/{skill}` - Run for deeper analysis")

        lines.append("")
        return '\n'.join(lines)

    def _title_case(self, text: str) -> str:
        """Convert skill name to title case"""
        return text.replace('_', ' ').replace('-', ' ').title()

    # Alternative formats

    def format_json(self, result: SkillResult) -> str:
        """Format SkillResult as JSON"""
        return json.dumps(result.to_dict(), indent=2, default=str)

    def format_yaml(self, result: SkillResult) -> str:
        """Format SkillResult as YAML"""
        return yaml.dump(result.to_dict(), default_flow_style=False)

    def format_findings_table(self, findings: List[Finding]) -> str:
        """Format just the findings as a table (for embedding)"""
        lines = [
            "| Issue | Evidence | Impact | Fix | Priority |",
            "|-------|----------|--------|-----|----------|",
        ]

        for f in sorted(findings, key=lambda x: x.priority.value):
            lines.append(
                f"| {f.issue} | {f.evidence} | {f.impact.value} | {f.fix} | {f.priority.value} |"
            )

        return '\n'.join(lines)


def save_report(
    result: SkillResult,
    output_dir: Path,
    format: str = "markdown"
) -> Path:
    """
    Save skill result to file.

    Args:
        result: SkillResult to save
        output_dir: Directory to save to
        format: 'markdown', 'json', or 'yaml'

    Returns:
        Path to saved file
    """
    formatter = OutputFormatter(result.skill_name)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M')

    if format == "json":
        content = formatter.format_json(result)
        ext = "json"
    elif format == "yaml":
        content = formatter.format_yaml(result)
        ext = "yaml"
    else:
        content = formatter.format_markdown(result)
        ext = "md"

    filename = f"{result.skill_name}-{timestamp}.{ext}"
    file_path = output_dir / filename

    output_dir.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)

    return file_path


def print_summary(result: SkillResult):
    """Print a brief summary to console"""
    print(f"\n{'=' * 60}")
    print(f"{result.skill_name.upper()} Analysis Complete")
    print(f"{'=' * 60}")

    # Geo context
    print(f"\nLocation: {result.geo_context.location_cluster}")
    print(f"Scope: {result.geo_context.geo_scope.value}")

    # 3D Score summary
    if result.three_d_score:
        print(f"\n3D Scores:")
        print(f"  Local Pack: {result.three_d_score.local_pack_probability:.0f}%")
        print(f"  Organic Local: {result.three_d_score.organic_local_probability:.0f}%")
        print(f"  Domestic: {result.three_d_score.domestic_organic_probability:.0f}%")

    # Findings summary
    critical = [f for f in result.findings if f.impact == FindingImpact.CRITICAL]
    high = [f for f in result.findings if f.impact == FindingImpact.HIGH]
    print(f"\nFindings: {len(result.findings)} total")
    if critical:
        print(f"  !! Critical: {len(critical)}")
    if high:
        print(f"  !  High: {len(high)}")

    # Decision statements
    if result.decision_statements:
        print(f"\nDecisions:")
        for stmt in result.decision_statements[:2]:
            print(f"  > {stmt}")

    print(f"\n{'=' * 60}\n")


__all__ = [
    'OutputFormatter',
    'save_report',
    'print_summary',
]
