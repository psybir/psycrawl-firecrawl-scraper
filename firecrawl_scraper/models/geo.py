"""
Geo models - Location and geographic tagging entities
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class GeoScope(str, Enum):
    """Geographic scope of service"""
    LOCAL_RADIUS = "local_radius"
    MULTI_LOCATION = "multi_location"
    DOMESTIC = "domestic"
    NATIONAL = "national"


class GeoBucket(str, Enum):
    """Distance buckets from primary location"""
    BUCKET_0_10 = "0-10"
    BUCKET_10_30 = "10-30"
    BUCKET_30_60 = "30-60"
    BUCKET_60_90 = "60-90"
    BUCKET_90_PLUS = "90+"


class Coordinates(BaseModel):
    """GPS coordinates"""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class GeoTag(BaseModel):
    """Geo-tagging for location-aware entities"""
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State abbreviation")
    zip: Optional[str] = Field(None, description="ZIP code")
    county: Optional[str] = Field(None, description="County name")
    region: Optional[str] = Field(None, description="Region/area name")
    dma: Optional[str] = Field(None, description="Designated Market Area")
    coordinates: Optional[Coordinates] = None
    radius_miles: Optional[float] = Field(None, description="Service radius from this point")

    @property
    def full_name(self) -> str:
        return f"{self.city}, {self.state}"

    @property
    def slug(self) -> str:
        return f"{self.city.lower().replace(' ', '-')}-{self.state.lower()}"


class Location(BaseModel):
    """Location entity - geo-targeted service areas"""
    id: str
    name: str = Field(..., description="Location name (e.g., 'Bethlehem, PA')")
    slug: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    geo_scope: GeoScope = Field(..., description="How this location is served")
    geo_bucket: GeoBucket = Field(..., description="Distance bucket from primary location")
    location_cluster: Optional[str] = Field(None, description="Logical grouping (e.g., 'Lehigh Valley')")
    is_primary: bool = Field(False, description="Is this the main business location?")
    is_physical: bool = Field(False, description="Physical location vs. service area only")
    population: Optional[int] = None
    households: Optional[int] = None
    median_income: Optional[float] = None
    current_rank: Optional[float] = Field(None, description="Current average grid rank")
    target_rank: Optional[int] = Field(None, ge=1, le=20, description="Target rank goal")
    rank_trend: Optional[str] = Field(None, description="improving, stable, declining")
    competitor_density: Optional[str] = Field(None, description="low, medium, high")
    priority: Optional[str] = Field(None, description="primary, secondary, expansion")
    travel_time_minutes: Optional[int] = None

    def to_geo_tag(self) -> GeoTag:
        """Convert to GeoTag for tagging purposes"""
        parts = self.name.split(", ")
        city = parts[0] if parts else self.name
        state = parts[1] if len(parts) > 1 else ""
        return GeoTag(
            city=city,
            state=state,
            coordinates=self.coordinates,
            radius_miles=self.travel_time_minutes * 0.75 if self.travel_time_minutes else None
        )
