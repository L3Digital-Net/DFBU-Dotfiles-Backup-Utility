"""
GUI Configuration Constants for DFBU

Description:
    Centralized configuration constants for GUI elements including UI dimensions,
    timeouts, and other configurable values. Extracted from hardcoded values in
    view.py to improve maintainability and configurability.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 11-01-2025
License: MIT

Features:
    - Centralized UI configuration constants
    - Timeout and duration settings
    - Dialog dimension specifications
    - Standard library only (no external dependencies)

Requirements:
    - Python 3.14+ for latest typing features
"""

from typing import Final


STATUS_MESSAGE_TIMEOUT_MS: Final[int] = 3000  # ms before status bar auto-clears

MIN_DIALOG_WIDTH: Final[int] = 600  # px — add/update dotfile dialog minimum width
MIN_DIALOG_HEIGHT: Final[int] = 400  # px — add/update dotfile dialog minimum height

MIN_MAIN_WINDOW_WIDTH: Final[int] = 1024  # px — main window minimum width
MIN_MAIN_WINDOW_HEIGHT: Final[int] = 768  # px — main window minimum height
