"""
Stage 1: PLAN - Generate Intent/Geo Matrix

Input: Client config (services, locations, constraints)
Output: Intent/Geo Matrix artifact

This stage creates the targeting matrix that maps services to geo buckets
with targeting specs for each cell.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from ..models import (
    Client,
    Service,
    Location,
    GeoScope,
    GeoBucket,
    IntentGeoMatrix,
    MatrixRow,
    MatrixColumn,
    MatrixCell,
    MatrixCTARules,
    PageStrategy,
    UrgencyLevel,
)

logger = logging.getLogger(__name__)


class PlanStage:
    """Generate Intent/Geo Matrix from client config"""

    def __init__(self, client: Client):
        self.client = client

    def run(self) -> IntentGeoMatrix:
        """Execute Stage 1: Generate Intent/Geo Matrix"""
        logger.info(f"Stage 1: Generating Intent/Geo Matrix for {self.client.name}")

        # Build rows (services)
        rows = self._build_service_rows()

        # Build columns (geo buckets)
        columns = self._build_geo_columns()

        # Build cells (service × geo combinations)
        cells = self._build_matrix_cells(rows, columns)

        # Create matrix
        matrix = IntentGeoMatrix(
            client_id=self.client.id,
            generated_at=datetime.now(),
            version="1.0.0",
            rows=rows,
            columns=columns,
            cells=cells,
        )

        # Calculate summary
        matrix.calculate_summary()

        logger.info(f"Stage 1 Complete: Generated matrix with {len(cells)} cells")
        return matrix

    def _build_service_rows(self) -> List[MatrixRow]:
        """Build matrix rows from client services"""
        rows = []
        priority = 1

        # Money services first
        for service in self.client.services:
            if service.is_money_service:
                rows.append(MatrixRow(
                    service_id=service.id,
                    service_name=service.name,
                    is_money_service=True,
                    priority=priority
                ))
                priority += 1

        # Non-money services
        for service in self.client.services:
            if not service.is_money_service:
                rows.append(MatrixRow(
                    service_id=service.id,
                    service_name=service.name,
                    is_money_service=False,
                    priority=priority
                ))
                priority += 1

        return rows

    def _build_geo_columns(self) -> List[MatrixColumn]:
        """Build matrix columns from location geo buckets"""
        columns = []
        bucket_locations: Dict[str, List[str]] = {}

        # Group locations by bucket
        for loc in self.client.locations:
            bucket = loc.geo_bucket.value
            if bucket not in bucket_locations:
                bucket_locations[bucket] = []
            bucket_locations[bucket].append(loc.name)

        # Create columns in order
        bucket_order = ["0-10", "10-30", "30-60", "60-90", "90+"]
        bucket_labels = {
            "0-10": "Primary (0-10 mi)",
            "10-30": "Secondary (10-30 mi)",
            "30-60": "Extended (30-60 mi)",
            "60-90": "Far (60-90 mi)",
            "90+": "Domestic",
        }

        priority = 1
        for bucket in bucket_order:
            if bucket in bucket_locations:
                columns.append(MatrixColumn(
                    geo_bucket=GeoBucket(bucket),
                    label=bucket_labels[bucket],
                    locations=bucket_locations[bucket],
                    priority=priority
                ))
                priority += 1

        return columns

    def _build_matrix_cells(
        self,
        rows: List[MatrixRow],
        columns: List[MatrixColumn]
    ) -> List[MatrixCell]:
        """Build matrix cells for each service × geo combination"""
        cells = []

        for row in rows:
            service = self._get_service(row.service_id)
            if not service:
                continue

            for col in columns:
                cell = self._build_cell(service, row, col)
                cells.append(cell)

        return cells

    def _build_cell(
        self,
        service: Service,
        row: MatrixRow,
        col: MatrixColumn
    ) -> MatrixCell:
        """Build a single matrix cell"""
        geo_bucket = col.geo_bucket.value

        # Determine page strategy based on service and geo
        page_strategy, page_type, merge_with = self._determine_page_strategy(
            service, geo_bucket
        )

        # Build keyword cluster
        keyword_cluster = self._build_keyword_cluster(service, col.locations)

        # Determine proof requirements
        proof_requirements = self._determine_proof_requirements(service, geo_bucket)

        # Determine CTA rules
        cta_rules = self._determine_cta_rules(service, geo_bucket)

        # Determine schema types
        schema_types = self._determine_schema_types(service, page_type)

        # Calculate priority score
        priority_score = self._calculate_priority_score(
            row.is_money_service,
            row.priority,
            col.priority,
            geo_bucket
        )

        return MatrixCell(
            service_id=service.id,
            geo_bucket=geo_bucket,
            page_strategy=page_strategy,
            page_type=page_type,
            merge_with=merge_with,
            keyword_cluster=keyword_cluster,
            proof_requirements=proof_requirements,
            cta_rules=cta_rules,
            schema_types=schema_types,
            priority_score=priority_score,
        )

    def _determine_page_strategy(
        self,
        service: Service,
        geo_bucket: str
    ) -> tuple:
        """Determine page strategy for service/geo combo"""
        # Money services get dedicated pages for primary buckets
        if service.is_money_service:
            if geo_bucket in ["0-10", "10-30"]:
                return PageStrategy.DEDICATED, "service-area", None
            elif geo_bucket in ["30-60"]:
                return PageStrategy.DEDICATED, "service-area", None
            elif geo_bucket in ["60-90", "90+"]:
                return PageStrategy.SECTION, "blog", None
        else:
            # Non-money services may be merged
            if geo_bucket == "0-10":
                return PageStrategy.DEDICATED, "service", None
            elif geo_bucket in ["10-30", "30-60"]:
                # Check if should merge with parent
                if service.parent_service_id:
                    return PageStrategy.MERGED, "merged", service.parent_service_id
                return PageStrategy.SECTION, "service", None
            else:
                return PageStrategy.NONE, None, None

        return PageStrategy.DEDICATED, "service", None

    def _build_keyword_cluster(
        self,
        service: Service,
        locations: List[str]
    ) -> List[str]:
        """Build keyword cluster for service/locations"""
        keywords = []

        # Primary service keywords
        base_keywords = service.keywords or [service.name.lower()]

        # Add location variations
        for kw in base_keywords[:3]:  # Top 3 keywords
            keywords.append(kw)
            for loc in locations[:3]:  # Top 3 locations
                keywords.append(f"{kw} {loc.lower()}")
                keywords.append(f"{loc.lower()} {kw}")

        # Add synonyms
        if service.synonyms:
            for syn in service.synonyms[:2]:
                keywords.append(syn)
                for loc in locations[:2]:
                    keywords.append(f"{syn} {loc.lower()}")

        return keywords[:15]  # Limit to 15 keywords per cell

    def _determine_proof_requirements(
        self,
        service: Service,
        geo_bucket: str
    ) -> List[str]:
        """Determine trust/proof requirements for this combo"""
        requirements = []

        # Base requirements
        requirements.extend([
            "reviews_above_fold",
            "rating_visible",
        ])

        # Primary locations need more proof
        if geo_bucket == "0-10":
            requirements.extend([
                "before_after_gallery",
                "local_testimonials",
                "certifications_visible",
                "license_badge",
            ])
        elif geo_bucket == "10-30":
            requirements.extend([
                "local_testimonials",
                "service_area_mention",
            ])
        elif geo_bucket in ["30-60", "60-90"]:
            requirements.extend([
                "travel_time_copy",
                "service_area_map",
            ])

        # Service-specific requirements
        if service.name.lower() in ["hail damage repair", "hail damage"]:
            requirements.append("insurance_partnership_badges")

        return requirements

    def _determine_cta_rules(
        self,
        service: Service,
        geo_bucket: str
    ) -> MatrixCTARules:
        """Determine CTA rules for this combo"""
        # Primary locations = high urgency
        if geo_bucket == "0-10":
            return MatrixCTARules(
                primary="Get Free Quote",
                urgency=UrgencyLevel.HIGH,
                phone_prominent=True
            )
        elif geo_bucket in ["10-30", "30-60"]:
            return MatrixCTARules(
                primary="Schedule Estimate",
                urgency=UrgencyLevel.MEDIUM,
                phone_prominent=True
            )
        else:
            return MatrixCTARules(
                primary="Contact Us",
                urgency=UrgencyLevel.LOW,
                phone_prominent=False
            )

    def _determine_schema_types(
        self,
        service: Service,
        page_type: Optional[str]
    ) -> List[str]:
        """Determine schema.org types for this page"""
        schemas = []

        if page_type == "service":
            schemas.extend(["Service", "LocalBusiness"])
        elif page_type == "service-area":
            schemas.extend(["Service", "LocalBusiness", "GeoCircle"])
        elif page_type == "blog":
            schemas.extend(["Article", "FAQPage"])

        # Add FAQPage if service has FAQ topics
        if service.faq_topics and "FAQPage" not in schemas:
            schemas.append("FAQPage")

        return schemas

    def _calculate_priority_score(
        self,
        is_money_service: bool,
        service_priority: int,
        geo_priority: int,
        geo_bucket: str
    ) -> float:
        """Calculate priority score for this cell (0-100)"""
        score = 50.0

        # Money services get priority
        if is_money_service:
            score += 20

        # Lower service priority number = higher score
        score += max(0, 10 - service_priority)

        # Lower geo priority number = higher score
        score += max(0, 10 - geo_priority)

        # Primary buckets get priority
        bucket_bonus = {
            "0-10": 15,
            "10-30": 10,
            "30-60": 5,
            "60-90": 0,
            "90+": -5
        }
        score += bucket_bonus.get(geo_bucket, 0)

        return min(100, max(0, score))

    def _get_service(self, service_id: str) -> Optional[Service]:
        """Get service by ID"""
        for service in self.client.services:
            if service.id == service_id:
                return service
        return None
