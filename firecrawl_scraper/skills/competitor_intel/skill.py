"""
Competitor Intelligence Skill

Extracts decision-grade competitive intelligence using Firecrawl's
extract_with_pro() for LLM-powered analysis.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from ..base import (
    BaseSkill,
    AssessmentQuestion,
    Finding,
    FindingImpact,
    FindingPriority,
    GeoContext,
    ThreeDScore,
    DecisionStatement,
    SkillResult,
)

logger = logging.getLogger(__name__)


# Schema for competitor extraction
COMPETITOR_EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "tagline": {"type": "string"},
        "value_proposition": {"type": "string"},
        "target_audience": {"type": "string"},
        "services": {
            "type": "array",
            "items": {"type": "string"}
        },
        "pricing_info": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "packages": {"type": "array", "items": {"type": "string"}},
                "starting_price": {"type": "string"},
                "price_range": {"type": "string"}
            }
        },
        "trust_signals": {
            "type": "object",
            "properties": {
                "testimonials_count": {"type": "integer"},
                "certifications": {"type": "array", "items": {"type": "string"}},
                "awards": {"type": "array", "items": {"type": "string"}},
                "years_in_business": {"type": "integer"},
                "team_size": {"type": "string"},
                "case_studies": {"type": "boolean"}
            }
        },
        "local_signals": {
            "type": "object",
            "properties": {
                "address_visible": {"type": "boolean"},
                "phone_visible": {"type": "boolean"},
                "service_areas": {"type": "array", "items": {"type": "string"}},
                "local_testimonials": {"type": "boolean"},
                "google_rating": {"type": "number"},
                "review_count": {"type": "integer"}
            }
        },
        "differentiators": {
            "type": "array",
            "items": {"type": "string"}
        },
        "weaknesses_observed": {
            "type": "array",
            "items": {"type": "string"}
        },
        "technology_stack": {
            "type": "array",
            "items": {"type": "string"}
        },
        "social_media": {
            "type": "object",
            "properties": {
                "facebook": {"type": "string"},
                "instagram": {"type": "string"},
                "linkedin": {"type": "string"},
                "youtube": {"type": "string"}
            }
        },
        "contact_info": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "address": {"type": "string"}
            }
        }
    }
}


class Skill(BaseSkill):
    """
    Competitor Intelligence Skill

    Analyzes competitors with focus on:
    - Local presence signals
    - Trust stack elements
    - Positioning & messaging
    - Pricing intelligence
    - Feature comparison
    """

    @property
    def name(self) -> str:
        return "competitor_intel"

    @property
    def version(self) -> str:
        return "1.0.0"

    def _get_skill_dir(self) -> str:
        return "competitor_intel"

    def get_assessment_questions(self, existing_context: Dict) -> List[AssessmentQuestion]:
        """Return assessment questions, skipping those answered in context"""
        questions = []

        # Check what's already in context
        has_business = 'business' in existing_context
        has_geography = 'geography' in existing_context

        if not has_business:
            questions.append(AssessmentQuestion(
                question="What is your business/product name and type?",
                category="target",
                required=True,
            ))
            questions.append(AssessmentQuestion(
                question="What industry vertical are you in?",
                category="target",
                options=["Virtual Tours", "Real Estate", "Hospitality", "Retail", "Professional Services", "Other"],
            ))

        if not has_geography:
            questions.append(AssessmentQuestion(
                question="What is your primary market/location cluster?",
                category="geography",
                required=True,
            ))
            questions.append(AssessmentQuestion(
                question="What is your geographic scope?",
                category="geography",
                options=["local_radius", "multi_location", "domestic"],
                default="local_radius",
            ))

        questions.append(AssessmentQuestion(
            question="What aspect should we focus on?",
            category="focus",
            options=["comprehensive", "positioning", "pricing", "local_presence", "features"],
            default="comprehensive",
        ))

        return questions

    async def execute(self, context: Dict, answers: Dict) -> Dict[str, Any]:
        """Execute competitor analysis using Firecrawl"""
        target_url = answers.get('url') or answers.get('target')

        if not target_url:
            return {"error": "No competitor URL provided"}

        # Import Firecrawl client
        try:
            from ...core.firecrawl_client import EnhancedFirecrawlClient
            client = EnhancedFirecrawlClient()
        except ImportError as e:
            logger.error(f"Could not import Firecrawl client: {e}")
            return {"error": "Firecrawl client not available"}

        results = {
            "target_url": target_url,
            "extracted_at": datetime.now().isoformat(),
            "focus": answers.get('focus', 'comprehensive'),
        }

        # Extract competitor data using Spark 1 Pro
        try:
            logger.info(f"Extracting competitor data from {target_url}")

            # Main page extraction - extract_with_pro is async and expects urls list
            extraction = await client.extract_with_pro(
                urls=[target_url],
                schema=COMPETITOR_EXTRACT_SCHEMA,
                prompt="""
                Analyze this competitor website for competitive intelligence.
                Extract all visible information about:
                - Company positioning and value proposition
                - Services/products offered
                - Pricing information (if visible)
                - Trust signals (testimonials, certifications, awards)
                - Local presence signals (address, service areas, local reviews)
                - Key differentiators they claim
                - Observable weaknesses in their presentation
                - Contact information and social media
                """
            )

            results["main_extraction"] = extraction

            # Try to get pricing page if exists
            pricing_urls = [
                f"{target_url.rstrip('/')}/pricing",
                f"{target_url.rstrip('/')}/prices",
                f"{target_url.rstrip('/')}/packages",
            ]

            for pricing_url in pricing_urls:
                try:
                    pricing_data = await client.extract_with_pro(
                        urls=[pricing_url],
                        schema={
                            "type": "object",
                            "properties": {
                                "packages": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "price": {"type": "string"},
                                            "features": {"type": "array", "items": {"type": "string"}}
                                        }
                                    }
                                },
                                "pricing_model": {"type": "string"},
                                "custom_pricing": {"type": "boolean"}
                            }
                        },
                        prompt="Extract pricing and package information from this page."
                    )
                    if pricing_data:
                        results["pricing_extraction"] = pricing_data
                        break
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            results["error"] = str(e)

        # Add context info for synthesis
        results["context"] = {
            "your_business": context.get('business', {}).get('name', 'Your Business'),
            "your_industry": context.get('business', {}).get('type', answers.get('industry')),
            "location_cluster": context.get('geography', {}).get('primary_market', answers.get('geo', '')),
        }

        return results

    def synthesize(self, data: Dict[str, Any], geo_context: GeoContext) -> SkillResult:
        """Synthesize extracted data into decision-grade output"""

        findings = []
        decision_statements = []

        # Extract main data - Firecrawl returns nested 'data' object
        main_extraction = data.get('main_extraction', {})
        main = main_extraction.get('data', {}) if main_extraction.get('success') else {}

        pricing_extraction = data.get('pricing_extraction', {})
        pricing = pricing_extraction.get('data', {}) if pricing_extraction.get('success') else {}

        context_info = data.get('context', {})

        # Analyze local signals
        local_signals = main.get('local_signals', {})
        trust_signals = main.get('trust_signals', {})

        # Calculate 3D scores
        three_d_score = self._calculate_3d_score(main, local_signals, trust_signals)

        # Generate findings from local presence
        self._analyze_local_presence(local_signals, findings, geo_context)

        # Generate findings from trust signals
        self._analyze_trust_signals(trust_signals, findings)

        # Generate findings from positioning
        self._analyze_positioning(main, findings)

        # Generate decision statements
        competitor_name = main.get('company_name', 'Competitor')
        your_name = context_info.get('your_business', 'You')

        if local_signals.get('review_count', 0) > 20:
            decision_statements.append(DecisionStatement(
                choose_option=competitor_name,
                if_condition=f"you need established local credibility ({local_signals.get('review_count', 0)} reviews)",
                geo_context=geo_context,
            ))

        if main.get('weaknesses_observed'):
            weaknesses = main.get('weaknesses_observed', [])
            if weaknesses:
                decision_statements.append(DecisionStatement(
                    choose_option=your_name,
                    if_condition=f"you can address their weakness: {weaknesses[0]}",
                    geo_context=geo_context,
                ))

        # Build result
        result = SkillResult(
            skill_name=self.name,
            executed_at=datetime.now(),
            geo_context=geo_context,
            three_d_score=three_d_score,
            decision_statements=decision_statements,
            findings=findings,
            raw_data=data,
            related_skills=self.get_related_skills(),
        )

        # Psybir Pipeline recommendations
        result.evidence_summary = f"Analyzed {competitor_name}'s website for competitive positioning"
        result.hypothesis = self._generate_hypothesis(main, three_d_score)
        result.design_recommendation = self._generate_design_rec(findings)
        result.measure_plan = "Track: Local pack position, review count, conversion rate vs competitor"

        return result

    def _calculate_3d_score(self, main: Dict, local: Dict, trust: Dict) -> ThreeDScore:
        """Calculate Psybir 3D scoring"""

        # Local Pack Probability (based on local signals)
        local_pack_score = 0
        local_evidence = []

        if local.get('google_rating'):
            local_pack_score += 20
            local_evidence.append(f"Rating: {local.get('google_rating')}")
        if local.get('review_count', 0) > 10:
            local_pack_score += 20
            local_evidence.append(f"{local.get('review_count')} reviews")
        if local.get('address_visible'):
            local_pack_score += 15
            local_evidence.append("Address visible")
        if local.get('phone_visible'):
            local_pack_score += 10
        if local.get('service_areas'):
            local_pack_score += 15
            local_evidence.append(f"{len(local.get('service_areas', []))} service areas")

        # Organic Local Probability
        organic_local_score = 0
        organic_evidence = []

        if main.get('services'):
            organic_local_score += 20
            organic_evidence.append(f"{len(main.get('services', []))} services listed")
        if local.get('local_testimonials'):
            organic_local_score += 20
            organic_evidence.append("Local testimonials")
        if local.get('service_areas'):
            organic_local_score += 20
            organic_evidence.append("Location pages likely")

        # Domestic Organic Probability
        domestic_score = 0
        domestic_evidence = []

        if trust.get('case_studies'):
            domestic_score += 20
            domestic_evidence.append("Has case studies")
        if main.get('differentiators'):
            domestic_score += 15
            domestic_evidence.append(f"{len(main.get('differentiators', []))} differentiators")
        if trust.get('certifications'):
            domestic_score += 15

        return ThreeDScore(
            local_pack_probability=min(local_pack_score, 100),
            local_pack_evidence=", ".join(local_evidence) or "Limited local signals",
            organic_local_probability=min(organic_local_score, 100),
            organic_local_evidence=", ".join(organic_evidence) or "Limited local content",
            domestic_organic_probability=min(domestic_score, 100),
            domestic_organic_evidence=", ".join(domestic_evidence) or "Limited authority signals",
        )

    def _analyze_local_presence(self, local: Dict, findings: List[Finding], geo_context: GeoContext):
        """Analyze local presence signals"""

        if not local.get('address_visible'):
            findings.append(Finding(
                issue="No visible address on website",
                evidence="Page scan - no address found",
                impact=FindingImpact.HIGH,
                fix="Add prominent address to header/footer",
                priority=FindingPriority.P2,
                category="local_presence",
                geo_context=geo_context,
            ))

        if local.get('review_count', 0) < 10:
            findings.append(Finding(
                issue=f"Low review count ({local.get('review_count', 0)})",
                evidence="Google Business Profile",
                impact=FindingImpact.MEDIUM,
                fix="Implement review generation campaign",
                priority=FindingPriority.P2,
                category="local_presence",
                geo_context=geo_context,
            ))

        if not local.get('service_areas'):
            findings.append(Finding(
                issue="No service areas defined",
                evidence="Page scan - no location pages",
                impact=FindingImpact.HIGH,
                fix="Create location-specific landing pages",
                priority=FindingPriority.P1,
                category="local_presence",
                geo_context=geo_context,
            ))

    def _analyze_trust_signals(self, trust: Dict, findings: List[Finding]):
        """Analyze trust signal gaps"""

        if not trust.get('testimonials_count'):
            findings.append(Finding(
                issue="No testimonials visible",
                evidence="Homepage and about page scan",
                impact=FindingImpact.MEDIUM,
                fix="Add testimonials section with photos",
                priority=FindingPriority.P2,
                category="trust",
            ))

        if not trust.get('certifications'):
            findings.append(Finding(
                issue="No certifications displayed",
                evidence="Site-wide scan",
                impact=FindingImpact.LOW,
                fix="Add industry certifications/badges",
                priority=FindingPriority.P3,
                category="trust",
            ))

        if not trust.get('case_studies'):
            findings.append(Finding(
                issue="No case studies",
                evidence="Content analysis",
                impact=FindingImpact.MEDIUM,
                fix="Create detailed case studies with results",
                priority=FindingPriority.P2,
                category="trust",
            ))

    def _analyze_positioning(self, main: Dict, findings: List[Finding]):
        """Analyze positioning and messaging"""

        if not main.get('value_proposition'):
            findings.append(Finding(
                issue="Unclear value proposition",
                evidence="Homepage hero section",
                impact=FindingImpact.HIGH,
                fix="Define clear, specific value proposition",
                priority=FindingPriority.P1,
                category="positioning",
            ))

        weaknesses = main.get('weaknesses_observed', [])
        for weakness in weaknesses[:3]:  # Top 3 weaknesses
            findings.append(Finding(
                issue=f"Competitor weakness: {weakness}",
                evidence="Site analysis",
                impact=FindingImpact.INFO,
                fix=f"Opportunity: Emphasize your strength in this area",
                priority=FindingPriority.P4,
                category="opportunity",
            ))

    def _generate_hypothesis(self, main: Dict, score: ThreeDScore) -> str:
        """Generate hypothesis for Psybir pipeline"""
        if score.local_pack_probability > 70:
            return "Competitor has strong local presence; focus on differentiation and specific service areas they don't cover"
        elif score.local_pack_probability < 40:
            return "Competitor weak on local SEO; aggressive local content strategy could capture market share"
        else:
            return "Balanced competition; focus on trust signals and review generation to gain edge"

    def _generate_design_rec(self, findings: List[Finding]) -> str:
        """Generate design recommendation from findings"""
        critical = [f for f in findings if f.priority == FindingPriority.P1]
        if critical:
            return f"Priority: {critical[0].fix}"
        high = [f for f in findings if f.priority == FindingPriority.P2]
        if high:
            return f"Focus on: {high[0].fix}"
        return "Continue monitoring competitor positioning"

    def get_related_skills(self) -> List[str]:
        return ["seo_audit", "pricing_intel", "local_seo", "content_gap"]


# Export the skill class
__all__ = ['Skill']
