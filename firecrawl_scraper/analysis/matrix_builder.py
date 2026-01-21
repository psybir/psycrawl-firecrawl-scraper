"""
Matrix Builder - Helpers for Intent/Geo Matrix generation

Provides utilities for building and analyzing the service × geo matrix.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from ..models import (
    Client,
    Service,
    Location,
    IntentGeoMatrix,
    MatrixRow,
    MatrixColumn,
    MatrixCell,
    MatrixCTARules,
    PageStrategy,
    GeoBucket,
    GeoScope,
    UrgencyLevel,
)


@dataclass
class KeywordOpportunity:
    """Keyword opportunity data"""
    keyword: str
    search_volume: int
    competition: str  # low, medium, high
    current_rank: Optional[float] = None
    cpc: Optional[float] = None


class MatrixBuilder:
    """Build and analyze Intent/Geo Matrix"""

    def __init__(self, client: Client):
        self.client = client

    def build_matrix(
        self,
        keyword_data: Dict[str, KeywordOpportunity] = None
    ) -> IntentGeoMatrix:
        """Build complete Intent/Geo Matrix"""
        rows = self._build_rows()
        columns = self._build_columns()
        cells = self._build_cells(rows, columns, keyword_data or {})

        matrix = IntentGeoMatrix(
            client_id=self.client.id,
            rows=rows,
            columns=columns,
            cells=cells
        )
        matrix.calculate_summary()

        return matrix

    def _build_rows(self) -> List[MatrixRow]:
        """Build service rows"""
        rows = []
        priority = 1

        # Money services first
        for service in sorted(self.client.services, key=lambda s: (not s.is_money_service, s.name)):
            rows.append(MatrixRow(
                service_id=service.id,
                service_name=service.name,
                is_money_service=service.is_money_service,
                priority=priority
            ))
            priority += 1

        return rows

    def _build_columns(self) -> List[MatrixColumn]:
        """Build geo bucket columns"""
        bucket_locations: Dict[str, List[str]] = {}

        for loc in self.client.locations:
            bucket = loc.geo_bucket.value
            if bucket not in bucket_locations:
                bucket_locations[bucket] = []
            bucket_locations[bucket].append(loc.name)

        columns = []
        bucket_order = [
            (GeoBucket.BUCKET_0_10, "Primary (0-10 mi)"),
            (GeoBucket.BUCKET_10_30, "Secondary (10-30 mi)"),
            (GeoBucket.BUCKET_30_60, "Extended (30-60 mi)"),
            (GeoBucket.BUCKET_60_90, "Far (60-90 mi)"),
            (GeoBucket.BUCKET_90_PLUS, "Domestic"),
        ]

        priority = 1
        for bucket, label in bucket_order:
            if bucket.value in bucket_locations:
                columns.append(MatrixColumn(
                    geo_bucket=bucket,
                    label=label,
                    locations=bucket_locations[bucket.value],
                    priority=priority
                ))
                priority += 1

        return columns

    def _build_cells(
        self,
        rows: List[MatrixRow],
        columns: List[MatrixColumn],
        keyword_data: Dict[str, KeywordOpportunity]
    ) -> List[MatrixCell]:
        """Build matrix cells"""
        cells = []

        for row in rows:
            service = self._get_service(row.service_id)
            if not service:
                continue

            for col in columns:
                cell = self._build_cell(service, row, col, keyword_data)
                cells.append(cell)

        return cells

    def _build_cell(
        self,
        service: Service,
        row: MatrixRow,
        col: MatrixColumn,
        keyword_data: Dict[str, KeywordOpportunity]
    ) -> MatrixCell:
        """Build single matrix cell"""
        geo_bucket = col.geo_bucket.value

        # Determine page strategy
        page_strategy, page_type = self._determine_strategy(service, geo_bucket)

        # Build keyword cluster
        keywords = self._build_keywords(service, col.locations)

        # Get search volume from keyword data
        total_volume = sum(
            keyword_data.get(kw, KeywordOpportunity(kw, 0, "medium")).search_volume
            for kw in keywords[:5]
        )

        # Determine competition
        competition = self._assess_competition(keywords, keyword_data)

        # Get current rank from locations
        current_rank = self._get_average_rank(col.locations)

        return MatrixCell(
            service_id=service.id,
            geo_bucket=geo_bucket,
            page_strategy=page_strategy,
            page_type=page_type,
            keyword_cluster=keywords[:10],
            search_volume={"total": total_volume},
            competition_level=competition,
            current_rank=current_rank,
            target_rank=3 if geo_bucket in ["0-10", "10-30"] else 5,
            proof_requirements=self._get_proof_requirements(geo_bucket),
            cta_rules=self._get_cta_rules(geo_bucket),
            schema_types=self._get_schema_types(page_type)
        )

    def _determine_strategy(
        self,
        service: Service,
        geo_bucket: str
    ) -> Tuple[PageStrategy, str]:
        """Determine page strategy for service/geo combo"""
        if service.is_money_service:
            if geo_bucket in ["0-10", "10-30", "30-60"]:
                return PageStrategy.DEDICATED, "service-area"
            else:
                return PageStrategy.SECTION, "blog"
        else:
            if geo_bucket == "0-10":
                return PageStrategy.DEDICATED, "service"
            elif geo_bucket in ["10-30", "30-60"]:
                if service.parent_service_id:
                    return PageStrategy.MERGED, "merged"
                return PageStrategy.SECTION, "service"
            return PageStrategy.NONE, None

    def _build_keywords(
        self,
        service: Service,
        locations: List[str]
    ) -> List[str]:
        """Build keyword cluster for service/locations"""
        keywords = []
        base = service.keywords or [service.name.lower()]

        for kw in base[:3]:
            keywords.append(kw)
            for loc in locations[:3]:
                city = loc.split(",")[0].strip().lower()
                keywords.append(f"{kw} {city}")
                keywords.append(f"{city} {kw}")

        if service.synonyms:
            keywords.extend(service.synonyms[:3])

        return keywords

    def _assess_competition(
        self,
        keywords: List[str],
        keyword_data: Dict[str, KeywordOpportunity]
    ) -> str:
        """Assess overall competition level"""
        competitions = []
        for kw in keywords[:5]:
            if kw in keyword_data:
                competitions.append(keyword_data[kw].competition)

        if not competitions:
            return "medium"

        # Count competition levels
        levels = {"low": 0, "medium": 0, "high": 0}
        for c in competitions:
            levels[c] = levels.get(c, 0) + 1

        # Return most common
        return max(levels, key=levels.get)

    def _get_average_rank(self, locations: List[str]) -> Optional[float]:
        """Get average rank for locations"""
        ranks = []
        for loc in self.client.locations:
            if loc.name in locations and loc.current_rank:
                ranks.append(loc.current_rank)
        return sum(ranks) / len(ranks) if ranks else None

    def _get_proof_requirements(self, geo_bucket: str) -> List[str]:
        """Get proof requirements for geo bucket"""
        base = ["reviews_above_fold", "rating_visible"]

        if geo_bucket == "0-10":
            return base + ["before_after_gallery", "local_testimonials", "certifications_visible"]
        elif geo_bucket in ["10-30", "30-60"]:
            return base + ["local_testimonials", "service_area_mention"]
        return base

    def _get_cta_rules(self, geo_bucket: str) -> MatrixCTARules:
        """Get CTA rules for geo bucket"""
        if geo_bucket == "0-10":
            return MatrixCTARules(primary="Get Free Quote", urgency=UrgencyLevel.HIGH, phone_prominent=True)
        elif geo_bucket in ["10-30", "30-60"]:
            return MatrixCTARules(primary="Schedule Estimate", urgency=UrgencyLevel.MEDIUM, phone_prominent=True)
        return MatrixCTARules(primary="Contact Us", urgency=UrgencyLevel.LOW, phone_prominent=False)

    def _get_schema_types(self, page_type: str) -> List[str]:
        """Get schema types for page type"""
        schemas = {
            "service": ["Service", "LocalBusiness"],
            "service-area": ["Service", "LocalBusiness", "GeoCircle"],
            "blog": ["Article", "FAQPage"],
            "merged": ["Service"],
        }
        return schemas.get(page_type, ["Service"])

    def _get_service(self, service_id: str) -> Optional[Service]:
        """Get service by ID"""
        for s in self.client.services:
            if s.id == service_id:
                return s
        return None

    def get_priority_cells(self, n: int = 10) -> List[MatrixCell]:
        """Get top N priority cells from matrix"""
        matrix = self.build_matrix()
        return sorted(matrix.cells, key=lambda c: c.priority_score, reverse=True)[:n]

    def get_gaps(self) -> List[Dict]:
        """Identify gaps in current coverage"""
        matrix = self.build_matrix()
        gaps = []

        for cell in matrix.cells:
            if cell.page_strategy == PageStrategy.NONE:
                continue
            if cell.current_rank and cell.target_rank:
                if cell.current_rank > cell.target_rank + 5:
                    gaps.append({
                        "service": cell.service_id,
                        "geo": cell.geo_bucket,
                        "current_rank": cell.current_rank,
                        "target_rank": cell.target_rank,
                        "gap": cell.current_rank - cell.target_rank
                    })

        return sorted(gaps, key=lambda g: g["gap"], reverse=True)
