"""
SEO Audit Skill

Performs 5-tier prioritized SEO analysis using Firecrawl for
crawlability checks and page-level analysis.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
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


# Schema for SEO extraction
SEO_EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "meta_description": {"type": "string"},
        "h1": {"type": "string"},
        "h2_tags": {"type": "array", "items": {"type": "string"}},
        "word_count": {"type": "integer"},
        "images_without_alt": {"type": "integer"},
        "internal_links_count": {"type": "integer"},
        "external_links_count": {"type": "integer"},
        "has_canonical": {"type": "boolean"},
        "canonical_url": {"type": "string"},
        "has_robots_meta": {"type": "boolean"},
        "robots_content": {"type": "string"},
        "structured_data_types": {"type": "array", "items": {"type": "string"}},
        "local_signals": {
            "type": "object",
            "properties": {
                "has_address": {"type": "boolean"},
                "has_phone": {"type": "boolean"},
                "has_local_schema": {"type": "boolean"},
                "service_areas_mentioned": {"type": "array", "items": {"type": "string"}}
            }
        },
        "page_speed_hints": {
            "type": "object",
            "properties": {
                "large_images": {"type": "boolean"},
                "excessive_scripts": {"type": "boolean"},
                "render_blocking_resources": {"type": "boolean"}
            }
        },
        "content_quality": {
            "type": "object",
            "properties": {
                "has_thin_content": {"type": "boolean"},
                "has_duplicate_sections": {"type": "boolean"},
                "readability_score": {"type": "string"},
                "topic_coverage": {"type": "string"}
            }
        }
    }
}


class Skill(BaseSkill):
    """
    SEO Audit Skill

    Performs 5-tier prioritized SEO audit:
    1. Crawlability & Indexation (Blocking)
    2. Technical Foundations (High)
    3. On-Page Optimization (Medium)
    4. Content Quality (Medium)
    5. Authority & Links (Long-term)
    """

    @property
    def name(self) -> str:
        return "seo_audit"

    @property
    def version(self) -> str:
        return "1.0.0"

    def _get_skill_dir(self) -> str:
        return "seo_audit"

    def get_assessment_questions(self, existing_context: Dict) -> List[AssessmentQuestion]:
        """Return assessment questions for SEO audit"""
        questions = []

        questions.append(AssessmentQuestion(
            question="What is the audit depth?",
            category="depth",
            options=["quick", "standard", "comprehensive"],
            default="standard",
        ))

        questions.append(AssessmentQuestion(
            question="What is your primary focus?",
            category="focus",
            options=["technical", "local_seo", "content", "aeo_geo", "all"],
            default="all",
        ))

        if 'geography' not in existing_context:
            questions.append(AssessmentQuestion(
                question="What is your target market/location?",
                category="geography",
            ))

        return questions

    async def execute(self, context: Dict, answers: Dict) -> Dict[str, Any]:
        """Execute SEO audit using Firecrawl"""
        target_url = answers.get('url') or answers.get('target')

        if not target_url:
            return {"error": "No URL provided for SEO audit"}

        # Ensure URL has protocol
        if not target_url.startswith('http'):
            target_url = f"https://{target_url}"

        parsed = urlparse(target_url)
        domain = parsed.netloc

        # Import Firecrawl client
        try:
            from ...core.firecrawl_client import EnhancedFirecrawlClient
            client = EnhancedFirecrawlClient()
        except ImportError as e:
            logger.error(f"Could not import Firecrawl client: {e}")
            return {"error": "Firecrawl client not available"}

        results = {
            "target_url": target_url,
            "domain": domain,
            "audited_at": datetime.now().isoformat(),
            "audit_depth": answers.get('depth', 'standard'),
            "focus": answers.get('focus', 'all'),
            "tiers": {},
        }

        depth = answers.get('depth', 'standard')
        tiers_to_run = self._get_tiers_for_depth(depth)

        # Tier 1: Crawlability & Indexation
        if 1 in tiers_to_run:
            results["tiers"]["tier1_crawlability"] = await self._audit_crawlability(
                client, target_url, domain
            )

        # Tier 2: Technical Foundations
        if 2 in tiers_to_run:
            results["tiers"]["tier2_technical"] = await self._audit_technical(
                client, target_url
            )

        # Tier 3: On-Page Optimization
        if 3 in tiers_to_run:
            results["tiers"]["tier3_onpage"] = await self._audit_onpage(
                client, target_url
            )

        # Tier 4: Content Quality
        if 4 in tiers_to_run:
            results["tiers"]["tier4_content"] = await self._audit_content(
                client, target_url
            )

        # Tier 5: Authority & Links (placeholder - would need external API)
        if 5 in tiers_to_run:
            results["tiers"]["tier5_authority"] = {
                "note": "Authority metrics require DataForSEO or similar API",
                "basic_signals": await self._audit_authority_basic(client, target_url)
            }

        return results

    def _get_tiers_for_depth(self, depth: str) -> List[int]:
        """Get which tiers to run based on audit depth"""
        if depth == "quick":
            return [1, 2]
        elif depth == "standard":
            return [1, 2, 3]
        else:  # comprehensive
            return [1, 2, 3, 4, 5]

    async def _audit_crawlability(self, client, url: str, domain: str) -> Dict:
        """Tier 1: Crawlability & Indexation audit"""
        results = {}

        try:
            # Check robots.txt
            robots_url = f"https://{domain}/robots.txt"
            robots_response = await client.scrape(robots_url, formats=["markdown"])
            results["robots_txt"] = {
                "exists": bool(robots_response),
                "content": robots_response.get("markdown", "")[:1000] if robots_response else None,
                "has_disallow": "Disallow" in str(robots_response) if robots_response else False,
            }
        except Exception as e:
            results["robots_txt"] = {"exists": False, "error": str(e)}

        try:
            # Check sitemap
            sitemap_url = f"https://{domain}/sitemap.xml"
            sitemap_response = await client.scrape(sitemap_url, formats=["markdown"])
            results["sitemap"] = {
                "exists": bool(sitemap_response),
                "has_urls": "<url>" in str(sitemap_response) if sitemap_response else False,
            }
        except Exception:
            results["sitemap"] = {"exists": False}

        # Check main page indexability
        try:
            main_page = await client.extract_with_pro(
                urls=[url],
                schema={
                    "type": "object",
                    "properties": {
                        "has_noindex": {"type": "boolean"},
                        "has_canonical": {"type": "boolean"},
                        "canonical_url": {"type": "string"},
                        "robots_meta": {"type": "string"}
                    }
                },
                prompt="Check if this page has noindex tags, canonical tags, and robots meta directives."
            )
            results["indexability"] = main_page
        except Exception as e:
            results["indexability"] = {"error": str(e)}

        return results

    async def _audit_technical(self, client, url: str) -> Dict:
        """Tier 2: Technical foundations audit"""
        results = {}

        try:
            # Page scrape with technical analysis
            page_data = await client.scrape(url, formats=["markdown", "html"])

            if page_data:
                html = page_data.get("html", "")
                results["https"] = url.startswith("https://")
                results["html_size_kb"] = len(html) / 1024 if html else 0

                # Check for common technical issues
                results["has_viewport_meta"] = 'name="viewport"' in html.lower()
                results["has_charset"] = 'charset=' in html.lower()

                # Extract structured data types
                import re
                schema_types = re.findall(r'"@type"\s*:\s*"([^"]+)"', html)
                results["structured_data_types"] = list(set(schema_types))

        except Exception as e:
            results["error"] = str(e)

        return results

    async def _audit_onpage(self, client, url: str) -> Dict:
        """Tier 3: On-page optimization audit"""
        try:
            extraction = await client.extract_with_pro(
                urls=[url],
                schema=SEO_EXTRACT_SCHEMA,
                prompt="""
                Analyze this page for SEO optimization:
                - Extract title tag, meta description, H1
                - Count H2 tags and word count
                - Check for images without alt text
                - Count internal and external links
                - Check for canonical and robots meta tags
                - Identify local SEO signals (address, phone, local schema)
                - Note any page speed concerns
                """
            )
            return extraction or {}
        except Exception as e:
            return {"error": str(e)}

    async def _audit_content(self, client, url: str) -> Dict:
        """Tier 4: Content quality audit"""
        try:
            extraction = await client.extract_with_pro(
                urls=[url],
                schema={
                    "type": "object",
                    "properties": {
                        "main_topic": {"type": "string"},
                        "content_depth": {"type": "string"},
                        "expertise_signals": {"type": "array", "items": {"type": "string"}},
                        "trust_signals": {"type": "array", "items": {"type": "string"}},
                        "content_freshness": {"type": "string"},
                        "unique_value": {"type": "string"},
                        "calls_to_action": {"type": "array", "items": {"type": "string"}}
                    }
                },
                prompt="""
                Analyze the content quality of this page:
                - What is the main topic?
                - How deep/comprehensive is the content coverage?
                - What expertise signals are present (credentials, experience)?
                - What trust signals exist (testimonials, certifications)?
                - Does the content seem fresh or outdated?
                - What unique value does this content provide?
                - What calls-to-action are present?
                """
            )
            return extraction or {}
        except Exception as e:
            return {"error": str(e)}

    async def _audit_authority_basic(self, client, url: str) -> Dict:
        """Tier 5: Basic authority signals (without external API)"""
        try:
            extraction = await client.extract_with_pro(
                urls=[url],
                schema={
                    "type": "object",
                    "properties": {
                        "brand_mentions": {"type": "boolean"},
                        "external_links_to_authority": {"type": "array", "items": {"type": "string"}},
                        "social_proof_elements": {"type": "array", "items": {"type": "string"}},
                        "press_mentions": {"type": "boolean"},
                        "partnership_logos": {"type": "boolean"}
                    }
                },
                prompt="Identify authority and trust signals on this page."
            )
            return extraction or {}
        except Exception as e:
            return {"error": str(e)}

    def synthesize(self, data: Dict[str, Any], geo_context: GeoContext) -> SkillResult:
        """Synthesize audit data into decision-grade output"""

        findings = []
        tiers = data.get("tiers", {})

        # Helper to extract data from Firecrawl response
        def get_tier_data(tier_data):
            if tier_data.get('success') and tier_data.get('data'):
                return tier_data['data']
            return tier_data

        # Process Tier 1: Crawlability
        tier1 = tiers.get("tier1_crawlability", {})
        # Tier1 has nested structure (indexability is Firecrawl response)
        if tier1.get("indexability", {}).get("success"):
            tier1["indexability"] = tier1["indexability"].get("data", {})
        self._process_crawlability_findings(tier1, findings, geo_context)

        # Process Tier 2: Technical
        tier2 = tiers.get("tier2_technical", {})
        self._process_technical_findings(tier2, findings)

        # Process Tier 3: On-Page (Firecrawl extraction response)
        tier3_raw = tiers.get("tier3_onpage", {})
        tier3 = get_tier_data(tier3_raw)
        self._process_onpage_findings(tier3, findings, geo_context)

        # Process Tier 4: Content (Firecrawl extraction response)
        tier4_raw = tiers.get("tier4_content", {})
        tier4 = get_tier_data(tier4_raw)
        self._process_content_findings(tier4, findings)

        # Calculate 3D scores
        three_d_score = self._calculate_3d_score(tiers, geo_context)

        # Generate decision statements
        decision_statements = self._generate_decisions(findings, data)

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

        # Psybir Pipeline
        critical_count = len([f for f in findings if f.priority == FindingPriority.P1])
        high_count = len([f for f in findings if f.priority == FindingPriority.P2])

        result.evidence_summary = f"Audited {data.get('target_url')} - {len(findings)} issues found ({critical_count} critical, {high_count} high priority)"
        result.hypothesis = self._generate_hypothesis(findings, three_d_score)
        result.design_recommendation = self._generate_design_rec(findings)
        result.measure_plan = "Track: GSC impressions/clicks, Core Web Vitals, target keyword rankings"

        return result

    def _process_crawlability_findings(self, tier1: Dict, findings: List[Finding], geo: GeoContext):
        """Process Tier 1 crawlability data into findings"""

        robots = tier1.get("robots_txt", {})
        sitemap = tier1.get("sitemap", {})
        indexability = tier1.get("indexability", {})

        if not robots.get("exists"):
            findings.append(Finding(
                issue="Missing robots.txt",
                evidence="Direct URL check",
                impact=FindingImpact.MEDIUM,
                fix="Create robots.txt with appropriate directives",
                priority=FindingPriority.P2,
                category="crawlability",
            ))

        if not sitemap.get("exists"):
            findings.append(Finding(
                issue="Missing XML sitemap",
                evidence="Direct URL check at /sitemap.xml",
                impact=FindingImpact.HIGH,
                fix="Generate and submit XML sitemap to GSC",
                priority=FindingPriority.P1,
                category="crawlability",
            ))

        if indexability.get("has_noindex"):
            findings.append(Finding(
                issue="Page has noindex directive",
                evidence="Meta robots tag analysis",
                impact=FindingImpact.CRITICAL,
                fix="Remove noindex if page should be indexed",
                priority=FindingPriority.P1,
                category="crawlability",
            ))

    def _process_technical_findings(self, tier2: Dict, findings: List[Finding]):
        """Process Tier 2 technical data into findings"""

        if not tier2.get("https"):
            findings.append(Finding(
                issue="Site not using HTTPS",
                evidence="URL protocol check",
                impact=FindingImpact.CRITICAL,
                fix="Install SSL certificate and redirect HTTP to HTTPS",
                priority=FindingPriority.P1,
                category="technical",
            ))

        if not tier2.get("has_viewport_meta"):
            findings.append(Finding(
                issue="Missing viewport meta tag",
                evidence="HTML head analysis",
                impact=FindingImpact.HIGH,
                fix="Add viewport meta tag for mobile responsiveness",
                priority=FindingPriority.P2,
                category="technical",
            ))

        if not tier2.get("structured_data_types"):
            findings.append(Finding(
                issue="No structured data found",
                evidence="JSON-LD/microdata scan",
                impact=FindingImpact.MEDIUM,
                fix="Implement LocalBusiness and relevant schema markup",
                priority=FindingPriority.P2,
                category="technical",
            ))

    def _process_onpage_findings(self, tier3: Dict, findings: List[Finding], geo: GeoContext):
        """Process Tier 3 on-page data into findings"""

        title = tier3.get("title", "")
        meta_desc = tier3.get("meta_description", "")
        h1 = tier3.get("h1", "")
        local = tier3.get("local_signals", {})

        if not title or len(title) < 10:
            findings.append(Finding(
                issue="Missing or too short title tag",
                evidence="HTML head analysis",
                impact=FindingImpact.HIGH,
                fix="Write compelling title tag (50-60 characters) with target keyword",
                priority=FindingPriority.P1,
                category="on_page",
            ))
        elif len(title) > 60:
            findings.append(Finding(
                issue=f"Title tag too long ({len(title)} chars)",
                evidence="HTML head analysis",
                impact=FindingImpact.LOW,
                fix="Shorten title to 50-60 characters",
                priority=FindingPriority.P3,
                category="on_page",
            ))

        if not meta_desc or len(meta_desc) < 50:
            findings.append(Finding(
                issue="Missing or too short meta description",
                evidence="HTML head analysis",
                impact=FindingImpact.MEDIUM,
                fix="Write compelling meta description (150-160 characters) with CTA",
                priority=FindingPriority.P2,
                category="on_page",
            ))

        if not h1:
            findings.append(Finding(
                issue="Missing H1 tag",
                evidence="HTML structure analysis",
                impact=FindingImpact.HIGH,
                fix="Add single H1 tag with primary keyword",
                priority=FindingPriority.P1,
                category="on_page",
            ))

        # Local SEO findings
        if geo.geo_scope.value in ["local_radius", "multi_location"]:
            if not local.get("has_local_schema"):
                findings.append(Finding(
                    issue="Missing LocalBusiness schema",
                    evidence="Structured data analysis",
                    impact=FindingImpact.HIGH,
                    fix="Implement LocalBusiness JSON-LD with NAP",
                    priority=FindingPriority.P1,
                    category="local_seo",
                    geo_context=geo,
                ))

            if not local.get("has_address"):
                findings.append(Finding(
                    issue="No address visible on page",
                    evidence="Content analysis",
                    impact=FindingImpact.MEDIUM,
                    fix="Add business address to footer/contact section",
                    priority=FindingPriority.P2,
                    category="local_seo",
                    geo_context=geo,
                ))

    def _process_content_findings(self, tier4: Dict, findings: List[Finding]):
        """Process Tier 4 content data into findings"""

        if tier4.get("content_depth") == "thin" or tier4.get("content_depth") == "shallow":
            findings.append(Finding(
                issue="Thin content detected",
                evidence="Content depth analysis",
                impact=FindingImpact.MEDIUM,
                fix="Expand content with comprehensive topic coverage",
                priority=FindingPriority.P2,
                category="content",
            ))

        if not tier4.get("expertise_signals"):
            findings.append(Finding(
                issue="Missing expertise signals (E-E-A-T)",
                evidence="Content analysis",
                impact=FindingImpact.MEDIUM,
                fix="Add credentials, experience, and author information",
                priority=FindingPriority.P3,
                category="content",
            ))

    def _calculate_3d_score(self, tiers: Dict, geo: GeoContext) -> ThreeDScore:
        """Calculate Psybir 3D scoring based on audit findings"""

        # Extract data from Firecrawl response if nested
        tier3_raw = tiers.get("tier3_onpage", {})
        tier3 = tier3_raw.get("data", {}) if tier3_raw.get("success") else tier3_raw
        local = tier3.get("local_signals", {})

        # Local Pack Probability
        local_score = 0
        local_evidence = []

        if local.get("has_local_schema"):
            local_score += 25
            local_evidence.append("Local schema present")
        if local.get("has_address"):
            local_score += 20
            local_evidence.append("Address visible")
        if local.get("has_phone"):
            local_score += 15
            local_evidence.append("Phone visible")
        if local.get("service_areas_mentioned"):
            local_score += 20
            local_evidence.append(f"{len(local.get('service_areas_mentioned', []))} service areas")

        # Organic Local Probability
        organic_score = 0
        organic_evidence = []

        if tier3.get("title"):
            organic_score += 20
            organic_evidence.append("Has title tag")
        if tier3.get("h1"):
            organic_score += 15
            organic_evidence.append("Has H1")
        if tier3.get("word_count", 0) > 500:
            organic_score += 20
            organic_evidence.append(f"{tier3.get('word_count', 0)} words")

        # Domestic Probability
        domestic_score = 0
        domestic_evidence = []

        tier2 = tiers.get("tier2_technical", {})
        if tier2.get("structured_data_types"):
            domestic_score += 15
            domestic_evidence.append("Has structured data")
        if tier2.get("https"):
            domestic_score += 10
            domestic_evidence.append("HTTPS enabled")

        return ThreeDScore(
            local_pack_probability=min(local_score, 100),
            local_pack_evidence=", ".join(local_evidence) or "Limited local signals",
            organic_local_probability=min(organic_score, 100),
            organic_local_evidence=", ".join(organic_evidence) or "Needs on-page optimization",
            domestic_organic_probability=min(domestic_score, 100),
            domestic_organic_evidence=", ".join(domestic_evidence) or "Technical improvements needed",
        )

    def _generate_decisions(self, findings: List[Finding], data: Dict) -> List[DecisionStatement]:
        """Generate decision statements from audit findings"""
        statements = []

        critical = [f for f in findings if f.priority == FindingPriority.P1]
        if critical:
            statements.append(DecisionStatement(
                choose_option="Fix Critical Issues First",
                if_condition=f"you want to rank at all ({len(critical)} blocking issues found)",
            ))

        local_issues = [f for f in findings if f.category == "local_seo"]
        if local_issues:
            statements.append(DecisionStatement(
                choose_option="Prioritize Local SEO",
                if_condition=f"you need local pack visibility ({len(local_issues)} local issues found)",
            ))

        return statements

    def _generate_hypothesis(self, findings: List[Finding], score: ThreeDScore) -> str:
        """Generate hypothesis for Psybir pipeline"""
        critical = len([f for f in findings if f.priority == FindingPriority.P1])
        if critical > 0:
            return f"Fixing {critical} critical issues should remove indexation barriers and enable ranking"
        if score.local_pack_probability < 50:
            return "Implementing local SEO improvements could significantly increase local pack visibility"
        return "Site has solid foundation; focus on content depth and authority building"

    def _generate_design_rec(self, findings: List[Finding]) -> str:
        """Generate design recommendation"""
        p1 = [f for f in findings if f.priority == FindingPriority.P1]
        if p1:
            return f"Immediate: {p1[0].fix}"
        p2 = [f for f in findings if f.priority == FindingPriority.P2]
        if p2:
            return f"Priority: {p2[0].fix}"
        return "No critical issues - focus on content expansion"

    def get_related_skills(self) -> List[str]:
        return ["competitor_intel", "local_seo", "schema_markup", "content_gap"]


__all__ = ['Skill']
