"""
DFBU ProfileDialog - Profile Management Dialog

Description:
    Dialog for managing backup profiles including creating,
    editing, and deleting named backup configurations.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT
"""

from pathlib import Path
from typing import Final

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QWidget,
)

from gui.viewmodel import DFBUViewModel


UI_FILE: Final[Path] = Path(__file__).parent / "designer" / "profile_dialog.ui"


class ProfileDialog(QDialog):
    """
    Dialog for managing backup profiles.

    Allows users to create, edit, delete, and view backup profiles.
    Uses Qt Designer UI file for layout.
    """

    def __init__(self, viewmodel: DFBUViewModel, parent: QWidget | None = None) -> None:
        """
        Initialize ProfileDialog.

        Args:
            viewmodel: DFBUViewModel instance
            parent: Parent widget
        """
        super().__init__(parent)
        self._viewmodel = viewmodel

        self._load_ui()
        self._connect_signals()
        self._viewmodel.profiles_changed.connect(self._refresh_profile_list)
        self._refresh_profile_list()

    def _load_ui(self) -> None:
        """Load UI from Qt Designer file and find child widgets."""
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

        self.profile_list: QListWidget = loaded.findChild(QListWidget, "profileList")  # type: ignore[assignment]
        self.btn_new: QPushButton = loaded.findChild(QPushButton, "btnNewProfile")  # type: ignore[assignment]
        self.btn_edit: QPushButton = loaded.findChild(QPushButton, "btnEditProfile")  # type: ignore[assignment]
        self.btn_delete: QPushButton = loaded.findChild(QPushButton, "btnDeleteProfile")  # type: ignore[assignment]
        self.button_box: QDialogButtonBox = loaded.findChild(
            QDialogButtonBox, "buttonBox"
        )  # type: ignore[assignment]

        if not all(
            [
                self.profile_list,
                self.btn_new,
                self.btn_edit,
                self.btn_delete,
                self.button_box,
            ]
        ):
            raise RuntimeError(f"Missing required widgets in UI file: {UI_FILE}")

        # Transfer layout from loaded widget to this dialog
        layout = loaded.layout()
        if layout is not None:
            self.setLayout(layout)

    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.profile_list.currentItemChanged.connect(self._on_selection_changed)
        self.btn_new.clicked.connect(self._on_new_profile)
        self.btn_edit.clicked.connect(self._on_edit_profile)
        self.btn_delete.clicked.connect(self._on_delete_profile)
        self.button_box.rejected.connect(self.reject)

    def _refresh_profile_list(self) -> None:
        """Refresh the profile list from ViewModel."""
        self.profile_list.clear()
        for name in self._viewmodel.get_profile_names():
            item = QListWidgetItem(name)
            self.profile_list.addItem(item)

    def _on_selection_changed(self, current: QListWidgetItem | None) -> None:
        """Handle profile selection change."""
        has_selection = current is not None
        self.btn_edit.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)

    def _on_new_profile(self) -> None:
        """Handle new profile button click.

        Note: Profile creation UI is deferred to future implementation.
        The button is present but functionality is not yet available.
        """
        # TODO: profile editor dialog not yet implemented

    def _on_edit_profile(self) -> None:
        """Handle edit profile button click.

        Note: Profile editing UI is deferred to future implementation.
        The button is present but functionality is not yet available.
        """
        # TODO: profile editor dialog not yet implemented

    def _on_delete_profile(self) -> None:
        """Handle delete profile button click."""
        current = self.profile_list.currentItem()
        if current:
            name = current.text()
            success = self._viewmodel.command_delete_profile(name)
            if success:
                self._refresh_profile_list()
