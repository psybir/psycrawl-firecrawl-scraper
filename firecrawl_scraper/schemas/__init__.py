"""
Lead Extraction Schemas for PsyCrawl

Industry-specific schemas for extracting business lead data
for 360 virtual tour sales campaigns.
"""

import json
from pathlib import Path

SCHEMA_DIR = Path(__file__).parent


def load_schema(name: str) -> dict:
    """Load a schema by name"""
    schema_path = SCHEMA_DIR / f"{name}_schema.json"
    if schema_path.exists():
        with open(schema_path, 'r') as f:
            return json.load(f)
    raise FileNotFoundError(f"Schema not found: {name}")


def get_available_schemas() -> list:
    """List all available schemas"""
    return [p.stem.replace('_schema', '') for p in SCHEMA_DIR.glob('*_schema.json')]
