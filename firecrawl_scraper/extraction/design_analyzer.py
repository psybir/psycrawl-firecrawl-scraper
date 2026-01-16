"""
Design Analyzer Module - v2.0

Captures and analyzes UI/UX design elements from websites for:
- Visual design extraction (colors, typography, layout)
- Screenshot capture (desktop + mobile)
- CTA and conversion element analysis
- Psychology-driven design insights
- Competitor design comparison

Uses Firecrawl's screenshot and LLM extraction capabilities.
"""

import asyncio
import json
import logging
import base64
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.firecrawl_client import EnhancedFirecrawlClient

logger = logging.getLogger(__name__)


# ============================================================================
# LLM EXTRACTION SCHEMAS
# ============================================================================

DESIGN_SYSTEM_SCHEMA = {
    "type": "object",
    "properties": {
        "color_palette": {
            "type": "object",
            "properties": {
                "primary": {"type": "string", "description": "Primary brand color (hex)"},
                "secondary": {"type": "string", "description": "Secondary color (hex)"},
                "accent": {"type": "string", "description": "Accent/highlight color (hex)"},
                "background": {"type": "string", "description": "Main background color (hex)"},
                "text_primary": {"type": "string", "description": "Primary text color (hex)"},
                "text_secondary": {"type": "string", "description": "Secondary text color (hex)"},
                "dark_mode": {"type": "boolean", "description": "Uses dark color scheme"}
            }
        },
        "typography": {
            "type": "object",
            "properties": {
                "heading_font": {"type": "string", "description": "Font family for headings"},
                "body_font": {"type": "string", "description": "Font family for body text"},
                "heading_sizes": {
                    "type": "object",
                    "properties": {
                        "h1": {"type": "string"},
                        "h2": {"type": "string"},
                        "h3": {"type": "string"}
                    }
                },
                "body_size": {"type": "string"},
                "line_height": {"type": "string"},
                "font_weight_emphasis": {"type": "string"}
            }
        },
        "spacing": {
            "type": "object",
            "properties": {
                "section_padding": {"type": "string"},
                "container_max_width": {"type": "string"},
                "element_spacing": {"type": "string"}
            }
        },
        "visual_style": {
            "type": "string",
            "description": "Overall visual style (e.g., minimalist, bold, playful, corporate, futuristic)"
        }
    }
}

COMPONENT_SCHEMA = {
    "type": "object",
    "properties": {
        "navigation": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "description": "sticky, fixed, standard"},
                "style": {"type": "string", "description": "transparent, solid, gradient"},
                "items": {"type": "array", "items": {"type": "string"}},
                "has_cta": {"type": "boolean"},
                "mobile_behavior": {"type": "string"}
            }
        },
        "hero_section": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "description": "video, image, animated, split"},
                "headline": {"type": "string"},
                "subheadline": {"type": "string"},
                "cta_text": {"type": "string"},
                "height": {"type": "string", "description": "full-screen, 80vh, etc."},
                "overlay": {"type": "boolean"}
            }
        },
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "layout": {"type": "string", "description": "grid, flex, masonry, etc."},
                    "columns": {"type": "integer"},
                    "background": {"type": "string"},
                    "contains": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "footer": {
            "type": "object",
            "properties": {
                "style": {"type": "string"},
                "columns": {"type": "integer"},
                "has_newsletter": {"type": "boolean"},
                "social_links": {"type": "boolean"}
            }
        }
    }
}

CTA_SCHEMA = {
    "type": "object",
    "properties": {
        "ctas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Button/CTA text"},
                    "type": {"type": "string", "description": "primary, secondary, text-link"},
                    "position": {"type": "string", "description": "hero, nav, section, footer"},
                    "action": {"type": "string", "description": "booking, contact, learn-more"},
                    "style": {
                        "type": "object",
                        "properties": {
                            "color": {"type": "string"},
                            "shape": {"type": "string", "description": "rounded, pill, square"},
                            "size": {"type": "string"}
                        }
                    },
                    "urgency_language": {"type": "boolean"}
                }
            }
        },
        "booking_flow": {
            "type": "object",
            "properties": {
                "integration": {"type": "string", "description": "Resova, FareHarbor, custom, etc."},
                "steps_visible": {"type": "integer"},
                "friction_points": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
}

PSYCHOLOGY_SCHEMA = {
    "type": "object",
    "properties": {
        "emotional_triggers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "element": {"type": "string"},
                    "emotion": {"type": "string", "description": "fear, excitement, curiosity, urgency"},
                    "technique": {"type": "string"}
                }
            }
        },
        "trust_signals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "review, badge, testimonial, award"},
                    "placement": {"type": "string"},
                    "prominence": {"type": "string", "description": "high, medium, low"}
                }
            }
        },
        "social_proof": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "count": {"type": "string"},
                    "visibility": {"type": "string"}
                }
            }
        },
        "scarcity_urgency": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "element": {"type": "string"},
                    "message": {"type": "string"},
                    "effectiveness": {"type": "string"}
                }
            }
        },
        "cognitive_load": {
            "type": "object",
            "properties": {
                "assessment": {"type": "string", "description": "low, moderate, high"},
                "primary_action_clarity": {"type": "string"},
                "visual_hierarchy_score": {"type": "integer", "description": "1-10"}
            }
        },
        "user_journey_friction": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step": {"type": "string"},
                    "friction_type": {"type": "string"},
                    "impact": {"type": "string"}
                }
            }
        }
    }
}

ANIMATION_SCHEMA = {
    "type": "object",
    "properties": {
        "page_transitions": {"type": "string"},
        "scroll_animations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "element": {"type": "string"},
                    "type": {"type": "string", "description": "fade, slide, parallax, reveal"},
                    "trigger": {"type": "string"}
                }
            }
        },
        "hover_effects": {"type": "array", "items": {"type": "string"}},
        "micro_interactions": {"type": "array", "items": {"type": "string"}},
        "3d_elements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "element": {"type": "string"},
                    "technology": {"type": "string", "description": "Three.js, CSS 3D, WebGL"},
                    "purpose": {"type": "string"}
                }
            }
        },
        "performance_concern": {"type": "boolean"}
    }
}


class DesignAnalyzer:
    """
    Comprehensive UI/UX design analyzer using Firecrawl's
    screenshot and LLM extraction capabilities.
    """

    def __init__(self, client: EnhancedFirecrawlClient):
        """
        Initialize the design analyzer.

        Args:
            client: Configured EnhancedFirecrawlClient instance
        """
        self.client = client
        self.results: Dict[str, Any] = {}

    async def capture_screenshots(
        self,
        url: str,
        output_dir: Path,
        include_mobile: bool = True
    ) -> Dict[str, Any]:
        """
        Capture full-page screenshots for desktop and mobile viewports.

        Args:
            url: URL to capture
            output_dir: Directory to save screenshots
            include_mobile: Whether to capture mobile viewport

        Returns:
            Dict with screenshot paths and metadata
        """
        logger.info(f"Capturing screenshots for: {url}")
        output_dir.mkdir(parents=True, exist_ok=True)

        result = {
            "url": url,
            "captured_at": datetime.now().isoformat(),
            "desktop": None,
            "mobile": None
        }

        # Desktop screenshot (default viewport)
        logger.info("  Capturing desktop viewport...")
        try:
            desktop_result = await self.client.scrape(
                url=url,
                formats=['screenshot'],
                wait_for=3000  # Wait for animations to load
            )

            # Screenshot is in data.screenshot, not top-level
            data = desktop_result.get('data', {})
            screenshot_data = data.get('screenshot') if isinstance(data, dict) else None

            if desktop_result.get('success') and screenshot_data:

                # Save screenshot
                desktop_path = output_dir / "desktop_fullpage.png"
                if screenshot_data.startswith('data:image'):
                    # Base64 encoded
                    img_data = screenshot_data.split(',')[1]
                    with open(desktop_path, 'wb') as f:
                        f.write(base64.b64decode(img_data))
                elif screenshot_data.startswith('http'):
                    # URL - download the image
                    async with aiohttp.ClientSession() as session:
                        async with session.get(screenshot_data) as resp:
                            if resp.status == 200:
                                with open(desktop_path, 'wb') as f:
                                    f.write(await resp.read())
                            else:
                                logger.warning(f"    Failed to download screenshot: HTTP {resp.status}")
                                desktop_path = None
                else:
                    # Raw data
                    with open(desktop_path, 'wb') as f:
                        f.write(screenshot_data.encode() if isinstance(screenshot_data, str) else screenshot_data)

                if desktop_path:
                    result["desktop"] = {
                        "path": str(desktop_path),
                        "viewport": "desktop",
                        "full_page": True
                    }
                    logger.info(f"    Saved: {desktop_path}")
            else:
                logger.warning(f"    Desktop screenshot not captured. Response keys: {desktop_result.keys()}, data keys: {data.keys() if isinstance(data, dict) else type(data)}")

        except Exception as e:
            logger.error(f"    Desktop screenshot failed: {e}")

        # Mobile screenshot
        if include_mobile:
            logger.info("  Capturing mobile viewport...")
            try:
                mobile_result = await self.client.scrape(
                    url=url,
                    formats=['screenshot'],
                    mobile=True,
                    wait_for=3000
                )

                # Screenshot is in data.screenshot, not top-level
                data = mobile_result.get('data', {})
                screenshot_data = data.get('screenshot') if isinstance(data, dict) else None

                if mobile_result.get('success') and screenshot_data:

                    mobile_path = output_dir / "mobile_fullpage.png"
                    if screenshot_data.startswith('data:image'):
                        img_data = screenshot_data.split(',')[1]
                        with open(mobile_path, 'wb') as f:
                            f.write(base64.b64decode(img_data))
                    elif screenshot_data.startswith('http'):
                        # URL - download the image
                        async with aiohttp.ClientSession() as session:
                            async with session.get(screenshot_data) as resp:
                                if resp.status == 200:
                                    with open(mobile_path, 'wb') as f:
                                        f.write(await resp.read())
                                else:
                                    logger.warning(f"    Failed to download mobile screenshot: HTTP {resp.status}")
                                    mobile_path = None
                    else:
                        # Raw data
                        with open(mobile_path, 'wb') as f:
                            f.write(screenshot_data.encode() if isinstance(screenshot_data, str) else screenshot_data)

                    if mobile_path:
                        result["mobile"] = {
                            "path": str(mobile_path),
                            "viewport": "mobile",
                            "full_page": True
                        }
                        logger.info(f"    Saved: {mobile_path}")
                else:
                    logger.warning(f"    Mobile screenshot not captured. Data keys: {data.keys() if isinstance(data, dict) else type(data)}")

            except Exception as e:
                logger.error(f"    Mobile screenshot failed: {e}")

        return result

    async def extract_design_system(self, url: str) -> Dict[str, Any]:
        """
        Extract design system details using LLM extraction.

        Args:
            url: URL to analyze

        Returns:
            Dict with design system (colors, typography, spacing)
        """
        logger.info(f"Extracting design system from: {url}")

        try:
            result = await self.client.extract(
                urls=[url],
                prompt="""Analyze this website and extract the complete design system.
                Focus on:
                1. Color palette (primary, secondary, accent, backgrounds, text colors)
                2. Typography (fonts, sizes, weights, line heights)
                3. Spacing patterns (padding, margins, container widths)
                4. Overall visual style classification

                Be specific with hex colors and exact font names where possible.""",
                schema=DESIGN_SYSTEM_SCHEMA
            )

            if result.get('success') and result.get('data'):
                data = result['data']
                logger.debug(f"Extract raw result keys: {result.keys()}")
                logger.debug(f"Extract data type: {type(data)}, value: {str(data)[:500]}")
                # Handle nested structure
                if isinstance(data, list) and len(data) > 0:
                    extracted = data[0].get('extract', data[0])
                    if extracted:
                        return extracted
                elif isinstance(data, dict):
                    return data

            logger.warning(f"Design system extraction returned no data. Result: {str(result)[:300]}")
            return {}

        except Exception as e:
            logger.error(f"Design system extraction failed: {e}")
            return {"error": str(e)}

    async def extract_components(self, url: str) -> Dict[str, Any]:
        """
        Extract UI component patterns from the page.

        Args:
            url: URL to analyze

        Returns:
            Dict with component details (nav, hero, sections, footer)
        """
        logger.info(f"Extracting component patterns from: {url}")

        try:
            result = await self.client.extract(
                urls=[url],
                prompt="""Analyze the UI components and layout patterns on this page.
                Extract details about:
                1. Navigation (type, style, items, mobile behavior)
                2. Hero section (type, content, height, visual elements)
                3. Content sections (layout, columns, backgrounds)
                4. Footer (style, columns, features)

                Focus on patterns that can be recreated in code.""",
                schema=COMPONENT_SCHEMA
            )

            if result.get('success') and result.get('data'):
                data = result['data']
                if isinstance(data, list) and len(data) > 0:
                    extracted = data[0].get('extract', data[0])
                    if extracted:
                        return extracted
                elif isinstance(data, dict):
                    return data

            logger.warning(f"Component extraction returned no data. Result: {str(result)[:300]}")
            return {}

        except Exception as e:
            logger.error(f"Component extraction failed: {e}")
            return {"error": str(e)}

    async def extract_ctas(self, url: str) -> Dict[str, Any]:
        """
        Extract CTA and conversion elements.

        Args:
            url: URL to analyze

        Returns:
            Dict with CTA analysis
        """
        logger.info(f"Extracting CTA patterns from: {url}")

        try:
            result = await self.client.extract(
                urls=[url],
                prompt="""Analyze all call-to-action elements and conversion points.
                For each CTA identify:
                1. Button/link text
                2. Visual style (color, shape, size)
                3. Position on page
                4. Purpose/action
                5. Whether it uses urgency language

                Also analyze the booking/conversion flow if present.""",
                schema=CTA_SCHEMA
            )

            if result.get('success') and result.get('data'):
                data = result['data']
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get('extract', data[0])
                return data

            return {}

        except Exception as e:
            logger.error(f"CTA extraction failed: {e}")
            return {"error": str(e)}

    async def extract_psychology(self, url: str) -> Dict[str, Any]:
        """
        Analyze psychology-driven design elements.

        Args:
            url: URL to analyze

        Returns:
            Dict with psychology insights
        """
        logger.info(f"Extracting psychology patterns from: {url}")

        try:
            result = await self.client.extract(
                urls=[url],
                prompt="""Analyze the psychological design techniques used on this page.
                Look for:
                1. Emotional triggers (fear, excitement, curiosity elements)
                2. Trust signals (reviews, badges, testimonials, awards)
                3. Social proof elements (review counts, user photos)
                4. Scarcity/urgency indicators (limited time, availability)
                5. Cognitive load assessment (is the page overwhelming?)
                6. User journey friction points (barriers to conversion)

                Rate the visual hierarchy clarity from 1-10.""",
                schema=PSYCHOLOGY_SCHEMA
            )

            if result.get('success') and result.get('data'):
                data = result['data']
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get('extract', data[0])
                return data

            return {}

        except Exception as e:
            logger.error(f"Psychology extraction failed: {e}")
            return {"error": str(e)}

    async def extract_animations(self, url: str) -> Dict[str, Any]:
        """
        Analyze animations and interactive elements.

        Args:
            url: URL to analyze

        Returns:
            Dict with animation analysis
        """
        logger.info(f"Extracting animation patterns from: {url}")

        try:
            result = await self.client.extract(
                urls=[url],
                prompt="""Analyze animations and interactive elements on this page.
                Identify:
                1. Page transition effects
                2. Scroll-triggered animations (fade, slide, parallax)
                3. Hover effects on buttons and cards
                4. Micro-interactions (loading states, form feedback)
                5. 3D elements (if any - Three.js, WebGL, CSS 3D)
                6. Whether animations might cause performance issues""",
                schema=ANIMATION_SCHEMA
            )

            if result.get('success') and result.get('data'):
                data = result['data']
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get('extract', data[0])
                return data

            return {}

        except Exception as e:
            logger.error(f"Animation extraction failed: {e}")
            return {"error": str(e)}

    async def analyze_full_design(
        self,
        url: str,
        output_dir: Path,
        include_screenshots: bool = True,
        include_mobile: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive design analysis.

        Args:
            url: URL to analyze
            output_dir: Directory to save outputs
            include_screenshots: Whether to capture screenshots
            include_mobile: Whether to include mobile viewport

        Returns:
            Complete design analysis
        """
        logger.info("=" * 60)
        logger.info(f"FULL DESIGN ANALYSIS: {url}")
        logger.info("=" * 60)

        output_dir.mkdir(parents=True, exist_ok=True)
        screenshots_dir = output_dir / "screenshots"

        result = {
            "url": url,
            "analyzed_at": datetime.now().isoformat(),
            "screenshots": None,
            "design_system": None,
            "components": None,
            "ctas": None,
            "psychology": None,
            "animations": None
        }

        # Run extractions concurrently for efficiency
        tasks = [
            self.extract_design_system(url),
            self.extract_components(url),
            self.extract_ctas(url),
            self.extract_psychology(url),
            self.extract_animations(url)
        ]

        if include_screenshots:
            tasks.insert(0, self.capture_screenshots(url, screenshots_dir, include_mobile))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        idx = 0
        if include_screenshots:
            result["screenshots"] = results[idx] if not isinstance(results[idx], Exception) else {"error": str(results[idx])}
            idx += 1

        result["design_system"] = results[idx] if not isinstance(results[idx], Exception) else {"error": str(results[idx])}
        result["components"] = results[idx + 1] if not isinstance(results[idx + 1], Exception) else {"error": str(results[idx + 1])}
        result["ctas"] = results[idx + 2] if not isinstance(results[idx + 2], Exception) else {"error": str(results[idx + 2])}
        result["psychology"] = results[idx + 3] if not isinstance(results[idx + 3], Exception) else {"error": str(results[idx + 3])}
        result["animations"] = results[idx + 4] if not isinstance(results[idx + 4], Exception) else {"error": str(results[idx + 4])}

        # Save full analysis
        with open(output_dir / "design_analysis.json", 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"Saved full analysis to: {output_dir / 'design_analysis.json'}")

        # Save individual components
        for key in ["design_system", "components", "ctas", "psychology", "animations"]:
            if result[key] and not isinstance(result[key], dict) or not result[key].get("error"):
                with open(output_dir / f"{key}.json", 'w') as f:
                    json.dump(result[key], f, indent=2, default=str)

        self.results = result
        return result

    async def compare_competitor_designs(
        self,
        urls: List[str],
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Compare design patterns across multiple competitor sites.

        Args:
            urls: List of competitor URLs to analyze
            output_dir: Directory to save outputs

        Returns:
            Comparison analysis with insights
        """
        logger.info("=" * 60)
        logger.info(f"COMPETITOR DESIGN COMPARISON ({len(urls)} sites)")
        logger.info("=" * 60)

        output_dir.mkdir(parents=True, exist_ok=True)

        comparison = {
            "analyzed_at": datetime.now().isoformat(),
            "competitors": [],
            "common_patterns": [],
            "differentiation_opportunities": [],
            "best_practices": []
        }

        for url in urls:
            logger.info(f"\nAnalyzing: {url}")
            site_dir = output_dir / url.replace("https://", "").replace("http://", "").replace("/", "_")

            try:
                analysis = await self.analyze_full_design(
                    url=url,
                    output_dir=site_dir,
                    include_screenshots=True,
                    include_mobile=True
                )

                comparison["competitors"].append({
                    "url": url,
                    "analysis": analysis
                })

            except Exception as e:
                logger.error(f"Failed to analyze {url}: {e}")
                comparison["competitors"].append({
                    "url": url,
                    "error": str(e)
                })

            await asyncio.sleep(1)  # Rate limiting between sites

        # Analyze patterns across competitors
        comparison["common_patterns"] = self._identify_common_patterns(comparison["competitors"])
        comparison["differentiation_opportunities"] = self._identify_differentiation(comparison["competitors"])
        comparison["best_practices"] = self._extract_best_practices(comparison["competitors"])

        # Save comparison
        with open(output_dir / "competitor_comparison.json", 'w') as f:
            json.dump(comparison, f, indent=2, default=str)

        return comparison

    def _identify_common_patterns(self, competitors: List[Dict]) -> List[str]:
        """Identify design patterns common across competitors."""
        patterns = []

        # Check for common elements
        has_dark_mode = sum(1 for c in competitors
                           if c.get("analysis", {}).get("design_system", {}).get("color_palette", {}).get("dark_mode"))
        if has_dark_mode > len(competitors) / 2:
            patterns.append("Dark color schemes are common in this industry")

        has_video_hero = sum(1 for c in competitors
                            if c.get("analysis", {}).get("components", {}).get("hero_section", {}).get("type") == "video")
        if has_video_hero > 0:
            patterns.append(f"{has_video_hero}/{len(competitors)} competitors use video heroes")

        has_sticky_nav = sum(1 for c in competitors
                            if c.get("analysis", {}).get("components", {}).get("navigation", {}).get("type") == "sticky")
        if has_sticky_nav > len(competitors) / 2:
            patterns.append("Sticky navigation is standard")

        return patterns

    def _identify_differentiation(self, competitors: List[Dict]) -> List[str]:
        """Identify opportunities to differentiate from competitors."""
        opportunities = []

        # Check for gaps
        has_3d = sum(1 for c in competitors
                    if c.get("analysis", {}).get("animations", {}).get("3d_elements"))
        if has_3d == 0:
            opportunities.append("No competitors use 3D/Three.js - opportunity to stand out")

        high_cognitive_load = sum(1 for c in competitors
                                  if c.get("analysis", {}).get("psychology", {}).get("cognitive_load", {}).get("assessment") == "high")
        if high_cognitive_load > len(competitors) / 2:
            opportunities.append("Competitors have cluttered designs - opportunity for clean, focused UX")

        return opportunities

    def _extract_best_practices(self, competitors: List[Dict]) -> List[str]:
        """Extract best practices from top-performing competitor designs."""
        practices = []

        # Check for effective trust signals
        for comp in competitors:
            trust = comp.get("analysis", {}).get("psychology", {}).get("trust_signals", [])
            for signal in trust:
                if signal.get("prominence") == "high":
                    practices.append(f"High-prominence {signal.get('type')} at {signal.get('placement')}")

        return list(set(practices))[:10]  # Dedupe and limit

    def generate_design_brief(self, output_dir: Path) -> str:
        """
        Generate a design brief from the analysis results.

        Args:
            output_dir: Directory to save the brief

        Returns:
            Markdown string of the design brief
        """
        if not self.results:
            return "No analysis results available. Run analyze_full_design first."

        brief = f"""# Design Analysis Brief

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*URL: {self.results.get('url', 'N/A')}*

## Color Palette

"""
        colors = self.results.get("design_system", {}).get("color_palette", {})
        if colors:
            for name, value in colors.items():
                if value and name != "dark_mode":
                    brief += f"- **{name.replace('_', ' ').title()}**: `{value}`\n"

        brief += f"""
## Typography

"""
        typography = self.results.get("design_system", {}).get("typography", {})
        if typography:
            brief += f"- **Heading Font**: {typography.get('heading_font', 'N/A')}\n"
            brief += f"- **Body Font**: {typography.get('body_font', 'N/A')}\n"

        brief += f"""
## Key Components

"""
        components = self.results.get("components", {})
        if components:
            hero = components.get("hero_section", {})
            if hero:
                brief += f"### Hero Section\n"
                brief += f"- Type: {hero.get('type', 'N/A')}\n"
                brief += f"- Height: {hero.get('height', 'N/A')}\n"

        brief += f"""
## CTAs

"""
        ctas = self.results.get("ctas", {}).get("ctas", [])
        for cta in ctas[:5]:
            brief += f"- **{cta.get('text', 'N/A')}** ({cta.get('position', '')}) - {cta.get('action', '')}\n"

        brief += f"""
## Psychology Insights

"""
        psych = self.results.get("psychology", {})
        if psych:
            cognitive = psych.get("cognitive_load", {})
            if cognitive:
                brief += f"- **Cognitive Load**: {cognitive.get('assessment', 'N/A')}\n"
                brief += f"- **Visual Hierarchy Score**: {cognitive.get('visual_hierarchy_score', 'N/A')}/10\n"

        # Save brief
        with open(output_dir / "design_brief.md", 'w') as f:
            f.write(brief)

        return brief

    async def analyze_site_design(
        self,
        urls: List[str],
        output_dir: Path,
        include_screenshots: bool = True,
        include_mobile: bool = True,
        max_concurrent: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze design across multiple pages of a site.

        Args:
            urls: List of URLs to analyze (from site map)
            output_dir: Directory to save outputs
            include_screenshots: Whether to capture screenshots
            include_mobile: Whether to include mobile viewport
            max_concurrent: Max concurrent page analyses (rate limiting)

        Returns:
            Aggregated design analysis with cross-page consistency scoring
        """
        logger.info("=" * 60)
        logger.info(f"MULTI-PAGE DESIGN ANALYSIS ({len(urls)} pages)")
        logger.info("=" * 60)

        output_dir.mkdir(parents=True, exist_ok=True)
        pages_dir = output_dir / "pages"
        pages_dir.mkdir(exist_ok=True)

        result = {
            "analyzed_at": datetime.now().isoformat(),
            "total_pages": len(urls),
            "pages_analyzed": 0,
            "pages": {},
            "aggregated": {
                "design_consistency": {},
                "color_palettes": [],
                "typography_fonts": [],
                "cta_patterns": [],
                "psychology_scores": [],
                "common_components": []
            },
            "cross_page_insights": [],
            "success": False
        }

        # Analyze pages with rate limiting
        import re
        from urllib.parse import urlparse

        for i, url in enumerate(urls):
            logger.info(f"\n[{i+1}/{len(urls)}] Analyzing: {url}")

            # Create safe directory name from URL
            parsed = urlparse(url)
            page_name = parsed.path.strip('/').replace('/', '_') or 'homepage'
            page_name = re.sub(r'[^\w\-]', '_', page_name)
            page_dir = pages_dir / page_name

            try:
                analysis = await self.analyze_full_design(
                    url=url,
                    output_dir=page_dir,
                    include_screenshots=include_screenshots,
                    include_mobile=include_mobile
                )

                result["pages"][url] = {
                    "page_name": page_name,
                    "output_dir": str(page_dir),
                    "analysis": analysis,
                    "success": True
                }
                result["pages_analyzed"] += 1

                # Aggregate data for cross-page analysis
                self._aggregate_page_data(result["aggregated"], analysis, url)

            except Exception as e:
                logger.error(f"Failed to analyze {url}: {e}")
                result["pages"][url] = {
                    "page_name": page_name,
                    "error": str(e),
                    "success": False
                }

            # Rate limiting between pages
            if i < len(urls) - 1:
                await asyncio.sleep(1.5)

        # Generate cross-page insights
        result["cross_page_insights"] = self._generate_cross_page_insights(result["aggregated"])
        result["aggregated"]["design_consistency"] = self._calculate_design_consistency(result["aggregated"])

        # Save aggregated results
        aggregated_dir = output_dir / "aggregated"
        aggregated_dir.mkdir(exist_ok=True)

        with open(aggregated_dir / "design_consistency.json", 'w') as f:
            json.dump(result["aggregated"]["design_consistency"], f, indent=2, default=str)

        with open(aggregated_dir / "cta_patterns.json", 'w') as f:
            json.dump(result["aggregated"]["cta_patterns"], f, indent=2, default=str)

        with open(aggregated_dir / "psychology_mapping.json", 'w') as f:
            json.dump(result["aggregated"]["psychology_scores"], f, indent=2, default=str)

        # Save full multi-page analysis
        with open(output_dir / "multi_page_analysis.json", 'w') as f:
            json.dump(result, f, indent=2, default=str)

        # Generate multi-page design brief
        self._generate_multi_page_brief(result, output_dir)

        result["success"] = result["pages_analyzed"] > 0
        logger.info(f"\nMulti-page analysis complete: {result['pages_analyzed']}/{len(urls)} pages analyzed")

        return result

    def _aggregate_page_data(self, aggregated: Dict, analysis: Dict, url: str):
        """Aggregate data from a single page analysis into overall metrics."""

        # Color palettes
        colors = analysis.get("design_system", {}).get("color_palette", {})
        if colors:
            aggregated["color_palettes"].append({
                "url": url,
                "colors": colors
            })

        # Typography
        typography = analysis.get("design_system", {}).get("typography", {})
        if typography:
            aggregated["typography_fonts"].append({
                "url": url,
                "heading_font": typography.get("heading_font"),
                "body_font": typography.get("body_font")
            })

        # CTAs
        ctas = analysis.get("ctas", {}).get("ctas", [])
        for cta in ctas:
            aggregated["cta_patterns"].append({
                "url": url,
                "text": cta.get("text"),
                "type": cta.get("type"),
                "position": cta.get("position"),
                "action": cta.get("action")
            })

        # Psychology
        psych = analysis.get("psychology", {})
        if psych:
            aggregated["psychology_scores"].append({
                "url": url,
                "cognitive_load": psych.get("cognitive_load", {}).get("assessment"),
                "visual_hierarchy_score": psych.get("cognitive_load", {}).get("visual_hierarchy_score"),
                "trust_signals_count": len(psych.get("trust_signals", [])),
                "emotional_triggers_count": len(psych.get("emotional_triggers", []))
            })

        # Components
        components = analysis.get("components", {})
        if components:
            aggregated["common_components"].append({
                "url": url,
                "has_sticky_nav": components.get("navigation", {}).get("type") == "sticky",
                "hero_type": components.get("hero_section", {}).get("type"),
                "section_count": len(components.get("sections", []))
            })

    def _calculate_design_consistency(self, aggregated: Dict) -> Dict:
        """Calculate design consistency scores across pages."""
        consistency = {
            "color_consistency": 0,
            "typography_consistency": 0,
            "navigation_consistency": 0,
            "overall_score": 0,
            "notes": []
        }

        # Check color consistency
        if aggregated["color_palettes"]:
            primary_colors = [p["colors"].get("primary") for p in aggregated["color_palettes"] if p["colors"].get("primary")]
            if primary_colors:
                unique_primaries = len(set(primary_colors))
                consistency["color_consistency"] = round((1 - (unique_primaries - 1) / len(primary_colors)) * 100, 1)
                if unique_primaries > 1:
                    consistency["notes"].append(f"Primary color varies across {unique_primaries} variations")

        # Check typography consistency
        if aggregated["typography_fonts"]:
            heading_fonts = [t["heading_font"] for t in aggregated["typography_fonts"] if t["heading_font"]]
            if heading_fonts:
                unique_headings = len(set(heading_fonts))
                consistency["typography_consistency"] = round((1 - (unique_headings - 1) / len(heading_fonts)) * 100, 1)
                if unique_headings > 1:
                    consistency["notes"].append(f"Heading font varies: {set(heading_fonts)}")

        # Check navigation consistency
        if aggregated["common_components"]:
            has_sticky = [c["has_sticky_nav"] for c in aggregated["common_components"]]
            sticky_consistency = has_sticky.count(True) / len(has_sticky) if has_sticky else 0
            consistency["navigation_consistency"] = round(max(sticky_consistency, 1 - sticky_consistency) * 100, 1)

        # Overall score
        scores = [consistency["color_consistency"], consistency["typography_consistency"], consistency["navigation_consistency"]]
        valid_scores = [s for s in scores if s > 0]
        consistency["overall_score"] = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0

        return consistency

    def _generate_cross_page_insights(self, aggregated: Dict) -> List[str]:
        """Generate insights from cross-page analysis."""
        insights = []

        # CTA analysis
        if aggregated["cta_patterns"]:
            cta_texts = [c["text"] for c in aggregated["cta_patterns"] if c["text"]]
            unique_ctas = set(cta_texts)
            if len(unique_ctas) <= 3:
                insights.append(f"Consistent CTA messaging across pages: {', '.join(unique_ctas)}")
            else:
                insights.append(f"Varied CTA messaging ({len(unique_ctas)} unique CTAs) - consider consolidation")

        # Psychology analysis
        if aggregated["psychology_scores"]:
            avg_hierarchy = sum(p["visual_hierarchy_score"] or 0 for p in aggregated["psychology_scores"]) / len(aggregated["psychology_scores"])
            if avg_hierarchy >= 7:
                insights.append(f"Strong visual hierarchy (avg {avg_hierarchy:.1f}/10)")
            elif avg_hierarchy <= 4:
                insights.append(f"Weak visual hierarchy (avg {avg_hierarchy:.1f}/10) - improve layout clarity")

            cognitive_loads = [p["cognitive_load"] for p in aggregated["psychology_scores"] if p["cognitive_load"]]
            if cognitive_loads.count("high") > len(cognitive_loads) / 2:
                insights.append("Most pages have high cognitive load - simplify design")

        # Component analysis
        if aggregated["common_components"]:
            hero_types = [c["hero_type"] for c in aggregated["common_components"] if c["hero_type"]]
            if hero_types:
                most_common_hero = max(set(hero_types), key=hero_types.count)
                insights.append(f"Dominant hero pattern: {most_common_hero}")

        return insights

    def _generate_multi_page_brief(self, result: Dict, output_dir: Path):
        """Generate comprehensive multi-page design brief."""
        brief = f"""# Multi-Page Design Analysis Brief

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Pages Analyzed: {result['pages_analyzed']}/{result['total_pages']}*

## Design Consistency Score

**Overall: {result['aggregated']['design_consistency'].get('overall_score', 0)}%**

- Color Consistency: {result['aggregated']['design_consistency'].get('color_consistency', 0)}%
- Typography Consistency: {result['aggregated']['design_consistency'].get('typography_consistency', 0)}%
- Navigation Consistency: {result['aggregated']['design_consistency'].get('navigation_consistency', 0)}%

### Notes
"""
        for note in result['aggregated']['design_consistency'].get('notes', []):
            brief += f"- {note}\n"

        brief += f"""
## Cross-Page Insights

"""
        for insight in result.get('cross_page_insights', []):
            brief += f"- {insight}\n"

        brief += f"""
## CTA Patterns Across Site

| Page | CTA Text | Position | Action |
|------|----------|----------|--------|
"""
        for cta in result['aggregated']['cta_patterns'][:15]:
            page = cta['url'].split('/')[-1] or 'homepage'
            brief += f"| {page[:20]} | {cta.get('text', 'N/A')[:25]} | {cta.get('position', 'N/A')} | {cta.get('action', 'N/A')} |\n"

        brief += f"""
## Psychology Scores by Page

| Page | Cognitive Load | Visual Hierarchy | Trust Signals |
|------|----------------|------------------|---------------|
"""
        for psych in result['aggregated']['psychology_scores']:
            page = psych['url'].split('/')[-1] or 'homepage'
            brief += f"| {page[:20]} | {psych.get('cognitive_load', 'N/A')} | {psych.get('visual_hierarchy_score', 'N/A')}/10 | {psych.get('trust_signals_count', 0)} |\n"

        brief += f"""
## Pages Analyzed

"""
        for url, data in result['pages'].items():
            status = "✓" if data.get('success') else "✗"
            brief += f"- [{status}] {url}\n"

        with open(output_dir / "multi_page_design_brief.md", 'w') as f:
            f.write(brief)

        logger.info(f"Generated multi-page brief: {output_dir / 'multi_page_design_brief.md'}")
