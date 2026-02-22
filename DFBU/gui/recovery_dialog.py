"""Recovery dialog for handling backup/restore failures.

Displays operation results with options to retry, skip, or abort.
Loaded from Qt Designer .ui file.
"""

from pathlib import Path
from typing import Final

from core.common_types import OperationResultDict
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)


UI_FILE: Final[Path] = Path(__file__).parent / "designer" / "recovery_dialog.ui"


class RecoveryDialog(QDialog):
    """Dialog for recovery options after backup/restore failures.

    Shows summary of completed/failed items and provides options to:
    - Retry failed items that might succeed
    - Skip failed items and continue
    - Abort the operation

    Attributes:
        action: User's chosen action ("retry", "continue", "abort")
        operation_result: The OperationResultDict being displayed

    Public methods:
        get_retryable_paths: Get list of paths that can be retried
    """

    def __init__(
        self,
        operation_result: OperationResultDict,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the recovery dialog.

        Args:
            operation_result: Structured operation result to display
            parent: Parent widget, typically the main window
        """
        super().__init__(parent)
        self.operation_result = operation_result
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

        self.success_count_label: QLabel = loaded.findChild(QLabel, "successCountLabel")  # type: ignore[assignment]
        self.failed_count_label: QLabel = loaded.findChild(QLabel, "failedCountLabel")  # type: ignore[assignment]
        self.failed_items_tree: QTreeWidget = loaded.findChild(
            QTreeWidget, "failedItemsTree"
        )  # type: ignore[assignment]
        self.retry_info_label: QLabel = loaded.findChild(QLabel, "retryInfoLabel")  # type: ignore[assignment]
        self.retry_failed_btn: QPushButton = loaded.findChild(
            QPushButton, "retryFailedBtn"
        )  # type: ignore[assignment]
        self.continue_btn: QPushButton = loaded.findChild(QPushButton, "continueBtn")  # type: ignore[assignment]
        self.abort_btn: QPushButton = loaded.findChild(QPushButton, "abortBtn")  # type: ignore[assignment]

        if not all(
            [
                self.success_count_label,
                self.failed_count_label,
                self.failed_items_tree,
                self.retry_info_label,
                self.retry_failed_btn,
                self.continue_btn,
                self.abort_btn,
            ]
        ):
            raise RuntimeError(f"Missing required widgets in UI file: {UI_FILE}")

        # Transfer layout from loaded widget to this dialog
        layout = loaded.layout()
        if layout is not None:
            self.setLayout(layout)

    def _populate_data(self) -> None:
        """Populate dialog with operation result data."""
        result = self.operation_result

        completed_count = len(result["completed"])
        failed_count = len(result["failed"])

        operation = result["operation_type"]
        action_text = "backed up" if "backup" in operation else "restored"
        self.success_count_label.setText(
            f"{completed_count} files {action_text} successfully"
        )
        self.failed_count_label.setText(f"{failed_count} files failed")

        self.failed_items_tree.clear()
        for item in result["failed"]:
            tree_item = QTreeWidgetItem(
                [
                    item["path"],
                    item["error_message"],
                    "Yes" if item["can_retry"] else "No",
                ]
            )
            self.failed_items_tree.addTopLevelItem(tree_item)

        retryable_count = len(result["can_retry"])
        self.retry_failed_btn.setEnabled(retryable_count > 0)

        if retryable_count == 0:
            self.retry_info_label.setText("No items can be retried.")
        else:
            self.retry_info_label.setText(
                f"{retryable_count} item(s) marked 'Yes' may succeed if retried."
            )

    def _connect_signals(self) -> None:
        """Connect button signals to handlers."""
        self.retry_failed_btn.clicked.connect(self._on_retry)
        self.continue_btn.clicked.connect(self._on_continue)
        self.abort_btn.clicked.connect(self._on_abort)

    def _on_retry(self) -> None:
        """Handle Retry Failed button click."""
        self.action = "retry"
        self.accept()

    def _on_continue(self) -> None:
        """Handle Skip & Continue button click."""
        self.action = "continue"
        self.accept()

    def _on_abort(self) -> None:
        """Handle Abort button click."""
        self.action = "abort"
        self.reject()

    def get_retryable_paths(self) -> list[str]:
        """Get list of paths that can be retried.

        Returns:
            List of path strings from failed items where can_retry is True
        """
        return self.operation_result["can_retry"].copy()
