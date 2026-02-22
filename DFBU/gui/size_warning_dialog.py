"""Size warning dialog for pre-backup size analysis.

Displays large files and directories with options to continue or cancel.
Loaded from Qt Designer .ui file.
"""

from pathlib import Path
from typing import Final

from core.common_types import SizeReportDict
from PySide6.QtCore import QFile
from PySide6.QtGui import QColor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from gui.theme import DFBUColors


UI_FILE: Final[Path] = Path(__file__).parent / "designer" / "size_warning_dialog.ui"

LEVEL_COLORS: Final[dict[str, QColor]] = {
    "warning": QColor(DFBUColors.WARNING),
    "alert": QColor(DFBUColors.ALERT),
    "critical": QColor(DFBUColors.CRITICAL),
}

LEVEL_ICONS: Final[dict[str, str]] = {
    "warning": "\u26a0\ufe0f",  # Warning sign
    "alert": "\U0001f536",  # Orange diamond
    "critical": "\U0001f534",  # Red circle
}


class SizeWarningDialog(QDialog):
    """Dialog for size warnings before backup operations.

    Shows summary of backup size and lists large files/directories.
    User can choose to continue anyway or cancel the backup.

    Attributes:
        action: User's chosen action ("continue" or "cancel")
        size_report: The SizeReportDict being displayed

    Public methods:
        None (dialog is modal, action is set on close)
    """

    def __init__(
        self,
        size_report: SizeReportDict,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the size warning dialog.

        Args:
            size_report: Size analysis report to display
            parent: Parent widget, typically the main window
        """
        super().__init__(parent)
        self.size_report = size_report
        self.action: str = ""

        self._load_ui()
        self._populate_data()
        self._connect_signals()

    def _load_ui(self) -> None:
        """Load UI from .ui file and find child widgets."""
        ui_file = QFile(str(UI_FILE))
        if not ui_file.open(QFile.OpenModeFlag.ReadOnly):
            raise RuntimeError(f"Cannot open UI file: {UI_FILE}")

        loader = QUiLoader()
        loaded = loader.load(ui_file, self)
        ui_file.close()

        if loaded is None:  # QUiLoader may return None on error
            raise RuntimeError(f"Failed to load UI file: {UI_FILE}")

        self.setWindowTitle(loaded.windowTitle())
        self.setMinimumSize(loaded.minimumSize())
        self.resize(loaded.size())

        title_label = loaded.findChild(QLabel, "titleLabel")
        total_size_label = loaded.findChild(QLabel, "totalSizeLabel")
        file_count_label = loaded.findChild(QLabel, "fileCountLabel")
        large_items_tree = loaded.findChild(QTreeWidget, "largeItemsTree")
        recommendation_label = loaded.findChild(QLabel, "recommendationLabel")
        critical_warning_label = loaded.findChild(QLabel, "criticalWarningLabel")
        continue_btn = loaded.findChild(QPushButton, "continueBtn")
        cancel_btn = loaded.findChild(QPushButton, "cancelBtn")

        if not all(
            [
                title_label,
                total_size_label,
                file_count_label,
                large_items_tree,
                recommendation_label,
                critical_warning_label,
                continue_btn,
                cancel_btn,
            ]
        ):
            raise RuntimeError(f"Missing required widgets in UI file: {UI_FILE}")

        # Assign to instance attributes (assertions for type narrowing)
        assert title_label is not None
        assert total_size_label is not None
        assert file_count_label is not None
        assert large_items_tree is not None
        assert recommendation_label is not None
        assert critical_warning_label is not None
        assert continue_btn is not None
        assert cancel_btn is not None

        self.title_label: QLabel = title_label
        self.total_size_label: QLabel = total_size_label
        self.file_count_label: QLabel = file_count_label
        self.large_items_tree: QTreeWidget = large_items_tree
        self.recommendation_label: QLabel = recommendation_label
        self.critical_warning_label: QLabel = critical_warning_label
        self.continue_btn: QPushButton = continue_btn
        self.cancel_btn: QPushButton = cancel_btn

        # Transfer layout from loaded widget to this dialog
        layout = loaded.layout()
        if layout:
            self.setLayout(layout)

    def _populate_data(self) -> None:
        """Populate dialog with size report data."""
        report = self.size_report

        total_size_mb = report["total_size_mb"]
        if total_size_mb >= 1024:
            size_text = f"{total_size_mb / 1024:.2f} GB"
        else:
            size_text = f"{total_size_mb:.1f} MB"

        self.total_size_label.setText(f"Total backup size: {size_text}")
        self.file_count_label.setText(f"{report['total_files']} files analyzed")

        if report["has_critical"]:
            self.title_label.setText("Critical: Very large files detected")
            self.title_label.setStyleSheet(f"color: {DFBUColors.CRITICAL};")
        elif report["has_alert"]:
            self.title_label.setText("Alert: Large files detected")
            self.title_label.setStyleSheet(f"color: {DFBUColors.ALERT};")
        else:
            self.title_label.setText("Warning: Some large files detected")
            self.title_label.setStyleSheet(f"color: {DFBUColors.WARNING};")

        self.large_items_tree.clear()
        for item in report["large_items"]:
            level = item["level"]
            icon = LEVEL_ICONS.get(level, "")

            size_mb = item["size_mb"]
            if size_mb >= 1024:
                size_text = f"{size_mb / 1024:.2f} GB"
            else:
                size_text = f"{size_mb:.1f} MB"

            tree_item = QTreeWidgetItem(
                [
                    f"{icon} {level.upper()}",
                    size_text,
                    item["path"],
                    item["application"],
                ]
            )

            if level in LEVEL_COLORS:
                tree_item.setBackground(0, LEVEL_COLORS[level])
                tree_item.setForeground(0, QColor(DFBUColors.NEUTRAL_900))

            self.large_items_tree.addTopLevelItem(tree_item)

        for i in range(self.large_items_tree.columnCount()):
            self.large_items_tree.resizeColumnToContents(i)

        if report["has_critical"]:
            self.critical_warning_label.setText(
                "⚠️ CRITICAL: Files over 1 GB detected. These files may cause issues "
                "with Git repositories. You must explicitly confirm to proceed."
            )
            self.continue_btn.setText("I Understand, Continue Anyway")
        else:
            self.critical_warning_label.setText("")

    def _connect_signals(self) -> None:
        """Connect button signals to handlers."""
        self.continue_btn.clicked.connect(self._on_continue)
        self.cancel_btn.clicked.connect(self._on_cancel)

    def _on_continue(self) -> None:
        """Handle Continue Anyway button click."""
        self.action = "continue"
        self.accept()

    def _on_cancel(self) -> None:
        """Handle Cancel button click."""
        self.action = "cancel"
        self.reject()
