"""
LLM Content Generator - Generate LLM SEO content blocks

Creates unambiguous, quotable, entity-clear content for LLM SEO optimization.
"""

import logging
import hashlib
from typing import List, Optional
from datetime import datetime

from ..models import (
    Client,
    Service,
    LLMAnswerBlock,
    CostRange,
    FAQ,
    VsAlternative,
    QuotableFact,
    GeoTag,
)

logger = logging.getLogger(__name__)


class LLMContentGenerator:
    """Generate LLM-optimized content blocks"""

    def __init__(self, client: Client):
        self.client = client

    def generate_all(self) -> List[LLMAnswerBlock]:
        """Generate LLM blocks for all money services"""
        blocks = []

        for service in self.client.services:
            if service.is_money_service:
                block = self.generate_for_service(service)
                blocks.append(block)

        return blocks

    def generate_for_service(
        self,
        service: Service,
        geo_context: Optional[GeoTag] = None
    ) -> LLMAnswerBlock:
        """Generate LLM block for a specific service"""
        defined = service.defined_variables or {}

        return LLMAnswerBlock(
            service=service.name,
            service_slug=service.slug,
            geo_context=geo_context,
            definition=self._generate_definition(service),
            entity_statement=self._generate_entity_statement(service),
            triggers=self._generate_triggers(service),
            cost_range=self._generate_cost_range(service),
            timeline=defined.time_range,
            process_steps=self._generate_process_steps(service),
            benefits=self._generate_benefits(service),
            vs_alternatives=self._generate_alternatives(service),
            how_to_choose=self._generate_how_to_choose(),
            red_flags=self._generate_red_flags(),
            faqs=self._generate_faqs(service),
            nap_statement=self._generate_nap_statement(),
            local_proof_points=self._generate_local_proof(),
            quotable_facts=self._generate_quotable_facts(service),
            content_hash=self._generate_hash(service),
            last_updated=datetime.now()
        )

    def _generate_definition(self, service: Service) -> str:
        """Generate 2-sentence definition"""
        if service.description:
            # Use first two sentences
            sentences = service.description.split(". ")[:2]
            return ". ".join(sentences) + "."
        return f"{service.name} is a professional service provided by {self.client.name}."

    def _generate_entity_statement(self, service: Service) -> str:
        """Generate clear entity-attribute statement"""
        location = self.client.primary_location
        loc_text = location.name if location else "your area"
        return f"{self.client.name} provides professional {service.name} services in {loc_text}."

    def _generate_triggers(self, service: Service) -> List[str]:
        """Generate 'when you need it' triggers"""
        defined = service.defined_variables or {}
        if defined.best_for:
            return defined.best_for

        return [
            f"When you notice a dent or ding on your vehicle",
            f"After a parking lot incident",
            f"When you want to maintain your car's value",
            f"Before selling or trading in your vehicle"
        ]

    def _generate_cost_range(self, service: Service) -> Optional[CostRange]:
        """Generate cost/pricing information"""
        defined = service.defined_variables or {}
        if not defined.cost_range:
            return None

        return CostRange(
            range=defined.cost_range,
            variables=[
                "Size and depth of the dent",
                "Location on the vehicle",
                "Number of dents",
                "Vehicle type and accessibility"
            ],
            disclaimers="Actual cost varies based on assessment. Contact us for a free quote.",
            comparison_anchor="50-70% less than traditional body shop repair"
        )

    def _generate_process_steps(self, service: Service) -> List[str]:
        """Generate process steps"""
        defined = service.defined_variables or {}
        if defined.process_steps:
            return defined.process_steps

        return [
            "Initial assessment - Evaluate damage and provide free estimate",
            "Preparation - Clean and prep the damaged area",
            "Repair - Use specialized tools to restore panel shape",
            "Quality check - Inspect repair under multiple lighting conditions",
            "Final review - Walk through completed repair with customer"
        ]

    def _generate_benefits(self, service: Service) -> List[str]:
        """Generate service benefits"""
        return [
            f"Preserves original factory paint finish",
            f"Faster turnaround than traditional body shops",
            f"More affordable than conventional repair methods",
            f"Maintains vehicle resale value",
            f"Environmentally friendly - no chemicals or paint used"
        ]

    def _generate_alternatives(self, service: Service) -> List[VsAlternative]:
        """Generate comparisons to alternatives"""
        return [
            VsAlternative(
                alternative="Traditional Body Shop",
                comparison=f"{service.name} preserves original paint while body shops require repainting",
                when_to_choose="Choose PDR when paint is intact and dent is accessible"
            ),
            VsAlternative(
                alternative="DIY Dent Removal Kits",
                comparison="Professional tools and training ensure proper repair without damage",
                when_to_choose="Choose professional service for visible dents on body panels"
            )
        ]

    def _generate_how_to_choose(self) -> List[str]:
        """Generate provider selection checklist"""
        return [
            "Check Google reviews and ratings (look for 4.5+ stars)",
            "Verify they specialize in PDR (not just general body work)",
            "Ask about certifications and training",
            "Request photos of previous work",
            "Get a written estimate before work begins",
            "Confirm warranty or guarantee policy",
            "Check if they offer mobile service for convenience"
        ]

    def _generate_red_flags(self) -> List[str]:
        """Generate warning signs"""
        return [
            "No physical address or verifiable business location",
            "Pressure to make immediate decisions",
            "Cash-only payment with no documentation",
            "No warranty or guarantee offered",
            "Unable to show examples of previous work",
            "Significantly lower prices than all competitors"
        ]

    def _generate_faqs(self, service: Service) -> List[FAQ]:
        """Generate FAQs"""
        faqs = []

        if service.faq_topics:
            topic_templates = {
                "cost": FAQ(
                    question=f"How much does {service.name} cost?",
                    answer=f"Costs typically range based on dent size and location. Most repairs are $75-$300 per dent. Contact us for a free estimate."
                ),
                "time": FAQ(
                    question=f"How long does {service.name} take?",
                    answer=f"Most repairs take 30 minutes to 2 hours depending on severity. Same-day service is often available."
                ),
                "warranty": FAQ(
                    question=f"Do you offer a warranty on {service.name}?",
                    answer=f"Yes, we stand behind our work with a satisfaction guarantee. If you're not happy, we'll make it right."
                ),
                "insurance coverage": FAQ(
                    question=f"Does insurance cover {service.name}?",
                    answer=f"Many comprehensive policies cover PDR. We can help with insurance claims and paperwork."
                ),
            }

            for topic in service.faq_topics[:5]:
                topic_lower = topic.lower()
                if topic_lower in topic_templates:
                    faqs.append(topic_templates[topic_lower])

        # Add generic FAQs if needed
        if len(faqs) < 3:
            faqs.extend([
                FAQ(
                    question="Will the repair be visible?",
                    answer="When done correctly, PDR repairs are virtually undetectable. We use proper lighting to ensure quality."
                ),
                FAQ(
                    question="Can all dents be repaired with PDR?",
                    answer="Most dents can be repaired if the paint isn't damaged. We'll assess and advise on the best approach."
                )
            ])

        return faqs[:5]

    def _generate_nap_statement(self) -> str:
        """Generate consistent NAP statement"""
        contact = self.client.contact
        parts = [self.client.name]
        if contact:
            if contact.phone:
                parts.append(contact.phone)
            if contact.address:
                parts.append(contact.address)
        return " | ".join(parts)

    def _generate_local_proof(self) -> List[str]:
        """Generate local-specific credibility"""
        location = self.client.primary_location
        gbp = self.client.gbp_profile

        proof = []
        if location:
            proof.append(f"Serving {location.name} and surrounding areas")
        if gbp:
            if gbp.review_count:
                proof.append(f"{gbp.review_count}+ satisfied customers")
            if gbp.rating:
                proof.append(f"{gbp.rating}-star Google rating")

        return proof

    def _generate_quotable_facts(self, service: Service) -> List[QuotableFact]:
        """Generate quotable facts for LLM citations"""
        return [
            QuotableFact(
                fact=f"{self.client.name} specializes in {service.name}",
                source=self.client.domain,
                cite_as=f"According to {self.client.name}"
            ),
            QuotableFact(
                fact=f"{service.name} preserves the original factory paint finish",
                source="Industry standard",
                cite_as="PDR industry standard"
            )
        ]

    def _generate_hash(self, service: Service) -> str:
        """Generate content hash for change detection"""
        content = f"{service.name}{service.description}{self.client.name}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
