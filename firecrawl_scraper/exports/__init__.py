"""
Export System - Generate markdown deliverables for AI agent handoffs

Produces structured markdown files from pipeline outputs:
- Client Brief: Executive summary
- Competitive Analysis: Detailed competitor breakdown
- Implementation Spec: Technical build instructions
- Content Brief: For content creators/AI
- SEO Strategy: For SEO execution
- Research Export: Integrated analysis from research repos
"""

from .markdown_exporter import MarkdownExporter
from .client_brief import ClientBriefGenerator
from .competitive_analysis import CompetitiveAnalysisGenerator
from .implementation_spec import ImplementationSpecGenerator
from .content_brief import ContentBriefGenerator
from .seo_strategy import SEOStrategyGenerator
from .research_export import (
    ResearchCompetitiveAnalysisGenerator,
    export_escape_exe_competitive_analysis,
    create_escape_exe_client,
)

__all__ = [
    'MarkdownExporter',
    'ClientBriefGenerator',
    'CompetitiveAnalysisGenerator',
    'ImplementationSpecGenerator',
    'ContentBriefGenerator',
    'SEOStrategyGenerator',
    # Research exports
    'ResearchCompetitiveAnalysisGenerator',
    'export_escape_exe_competitive_analysis',
    'create_escape_exe_client',
]
