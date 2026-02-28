"""
DFBU GUI Theme Constants

Description:
    Centralized color palette, spacing, and typography constants for the
    DFBU desktop application. All colors are derived from the brand icon
    palette (DFBU/resources/icons/dfbu.svg).

    This module serves as the single source of truth for visual styling
    constants used across the application. QSS stylesheets reference
    these values, and Python code should use these constants instead of
    hardcoded color values.

Author: Chris Purcell
License: MIT
"""

from typing import Final


class DFBUColors:
    """Centralized color palette derived from brand icon."""

    # Primary (from document shape in icon)
    PRIMARY: Final[str] = "#2563EB"
    PRIMARY_DARK: Final[str] = "#1D4ED8"
    PRIMARY_LIGHT: Final[str] = "#3B82F6"
    PRIMARY_SUBTLE: Final[str] = "#EFF6FF"

    # Success (from shield in icon)
    SUCCESS: Final[str] = "#10B981"
    SUCCESS_DARK: Final[str] = "#059669"
    SUCCESS_LIGHT: Final[str] = "#34D399"

    WARNING: Final[str] = "#F59E0B"
    ALERT: Final[str] = "#F97316"
    CRITICAL: Final[str] = "#EF4444"

    NEUTRAL_50: Final[str] = "#F8FAFC"
    NEUTRAL_100: Final[str] = "#F1F5F9"
    NEUTRAL_200: Final[str] = "#E2E8F0"
    NEUTRAL_300: Final[str] = "#CBD5E1"
    NEUTRAL_400: Final[str] = "#94A3B8"
    NEUTRAL_500: Final[str] = "#64748B"
    NEUTRAL_600: Final[str] = "#475569"
    NEUTRAL_700: Final[str] = "#334155"
    NEUTRAL_800: Final[str] = "#1E293B"
    NEUTRAL_900: Final[str] = "#0F172A"

    # Semantic aliases
    BACKGROUND: Final[str] = "#FFFFFF"
    SURFACE: Final[str] = NEUTRAL_50
    TEXT_PRIMARY: Final[str] = NEUTRAL_800
    TEXT_SECONDARY: Final[str] = NEUTRAL_500
    TEXT_DISABLED: Final[str] = NEUTRAL_400
    BORDER: Final[str] = NEUTRAL_200
    BORDER_FOCUS: Final[str] = PRIMARY


class DFBUSpacing:
    """4px base unit spacing system."""

    XS: Final[int] = 4
    SM: Final[int] = 8
    MD: Final[int] = 12
    LG: Final[int] = 16
    XL: Final[int] = 24
    XXL: Final[int] = 32


class DFBUTypography:
    """Font families and sizes."""

    FONT_FAMILY: Final[str] = "Segoe UI, Ubuntu, Cantarell, sans-serif"
    FONT_MONO: Final[str] = "JetBrains Mono, Fira Code, Consolas, monospace"
    SIZE_CAPTION: Final[int] = 11
    SIZE_BODY: Final[int] = 13
    SIZE_HEADING: Final[int] = 15
    SIZE_TITLE: Final[int] = 18
