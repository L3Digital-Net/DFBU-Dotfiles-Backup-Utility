"""Theme loader utility for applying QSS stylesheets to the application."""

from pathlib import Path

from PySide6.QtWidgets import QApplication


# PURPOSE: Dict avoids `global` statement — mutated in place to track current theme across calls
_theme_state = {"current": "dfbu_light"}


def load_theme(app: QApplication, theme_name: str = "dfbu_light") -> bool:
    """Load and apply a QSS theme to the application.

    Args:
        app: The QApplication instance to apply the theme to.
        theme_name: Name of the theme file (without .qss extension).

    Returns:
        True if the theme was loaded successfully, False otherwise.
    """
    qss_path = Path(__file__).parent / "styles" / f"{theme_name}.qss"
    if not qss_path.exists():
        return False
    app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
    _theme_state["current"] = theme_name
    return True


def get_current_theme() -> str:
    """Return the name of the currently loaded theme."""
    return _theme_state["current"]


def get_available_themes() -> list[str]:
    """Return list of available theme names (QSS files in styles directory)."""
    styles_dir = Path(__file__).parent / "styles"
    return sorted(p.stem for p in styles_dir.glob("dfbu_*.qss"))
