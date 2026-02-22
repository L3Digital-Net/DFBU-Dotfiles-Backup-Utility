"""Help dialog for DFBU application.

This module provides the HelpDialog class which displays user documentation
in a tabbed interface with Quick Start and Configuration Reference sections.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class HelpDialog(QDialog):
    """User guide dialog with Quick Start and Configuration Reference tabs.

    A modal dialog displaying application documentation in a tabbed format.
    Content is loaded from external HTML files in the resources/help/ directory
    and rendered in QTextBrowser widgets for rich formatting.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the help dialog.

        Args:
            parent: Parent widget, typically the main window.
        """
        super().__init__(parent)
        self.setWindowTitle("DFBU User Guide")
        self.setMinimumSize(500, 400)
        self.resize(650, 550)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI with tabs and buttons."""
        layout = QVBoxLayout(self)
        help_dir = Path(__file__).parent.parent / "resources" / "help"

        tab_widget = QTabWidget()

        quick_start_browser = QTextBrowser()
        try:
            quick_start_browser.setHtml(
                (help_dir / "quick_start.html").read_text(encoding="utf-8")
            )
        except FileNotFoundError:
            quick_start_browser.setHtml("<p>Help content not available.</p>")
        quick_start_browser.setOpenExternalLinks(True)
        tab_widget.addTab(quick_start_browser, "Quick Start")

        config_browser = QTextBrowser()
        try:
            config_browser.setHtml(
                (help_dir / "config_reference.html").read_text(encoding="utf-8")
            )
        except FileNotFoundError:
            config_browser.setHtml("<p>Help content not available.</p>")
        config_browser.setOpenExternalLinks(True)
        tab_widget.addTab(config_browser, "Configuration Reference")

        layout.addWidget(tab_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
