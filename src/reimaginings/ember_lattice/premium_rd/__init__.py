"""Deterministic premium R&D authoring, rendering, and audit tools."""

from .model import REQUIRED_CRITERIA, REQUIRED_SCENARIOS, validate_bundle
from .render import build_site

__all__ = ["REQUIRED_CRITERIA", "REQUIRED_SCENARIOS", "build_site", "validate_bundle"]
__version__ = "1.0.0"
