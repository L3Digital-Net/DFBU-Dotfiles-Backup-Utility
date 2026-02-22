"""
DFBU View - UI Presentation Layer

Description:
    View layer for DFBU GUI implementing MVVM pattern. Focuses solely on
    UI presentation and user interaction, delegating all business logic to the
    ViewModel. Provides clean separation between presentation and logic.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 02-01-2026
License: MIT

Features:
    - MVVM View layer with pure UI presentation concerns
    - Signal-based data binding to ViewModel
    - Tab-based interface for Backup, Restore, and Configuration views
    - Real-time progress tracking and operation feedback
    - Dotfile list display with validation status indicators
    - Interactive dotfile management with add, update, and remove functionality
    - Window state persistence through ViewModel
    - Python standard library first approach with minimal dependencies
    - Clean architecture with confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - PySide6 framework for modern desktop GUI
    - viewmodel module for presentation logic

Classes:
    - AddDotfileDialog: Dialog for adding new dotfile entries
    - MainWindow: Main application window implementing the GUI interface

Functions:
    None
"""

from pathlib import Path
from typing import Any, Final

from core.common_types import LegacyDotFileDict, OperationResultDict, SizeReportDict
from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import (
    QCloseEvent,
    QColor,
    QKeySequence,
    QPixmap,
    QShortcut,
    QTextCursor,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from gui.constants import MIN_DIALOG_HEIGHT, MIN_DIALOG_WIDTH, STATUS_MESSAGE_TIMEOUT_MS
from gui.help_dialog import HelpDialog
from gui.input_validation import InputValidator
from gui.recovery_dialog import RecoveryDialog
from gui.size_warning_dialog import SizeWarningDialog
from gui.theme import DFBUColors
from gui.theme_loader import get_current_theme, load_theme
from gui.tooltip_manager import TooltipManager
from gui.viewmodel import DFBUViewModel


class NumericTableWidgetItem(QTableWidgetItem):
    """
    Custom QTableWidgetItem for proper numeric sorting.

    Stores a numeric value in UserRole and uses it for comparisons,
    enabling correct sorting of formatted strings (like "1.5 KB").
    """

    def __lt__(self, other: QTableWidgetItem) -> bool:
        """
        Compare items by numeric value stored in UserRole.

        Args:
            other: Other table item to compare against

        Returns:
            True if this item's numeric value is less than other's
        """
        self_value = self.data(Qt.ItemDataRole.UserRole)
        other_value = other.data(Qt.ItemDataRole.UserRole)

        # None values sort as 0 (unset size items sort before sized items)
        self_numeric: int | float = (
            self_value if isinstance(self_value, (int, float)) else 0
        )
        other_numeric: int | float = (
            other_value if isinstance(other_value, (int, float)) else 0
        )

        return self_numeric < other_numeric


class AddDotfileDialog(QDialog):
    """
    Dialog for adding or updating dotfile entry with support for multiple paths.

    CRITICAL: UI is loaded from Qt Designer .ui file, NOT hardcoded.

    Attributes:
        tags_edit: Line edit for tags (comma-separated)
        application_edit: Line edit for application name
        description_edit: Line edit for description
        paths_list: List widget displaying all paths
        path_input_edit: Line edit for new path input
        enabled_checkbox: Checkbox for enabled status
        browse_btn: Button to browse for file/directory
        add_path_btn: Button to add path to list
        remove_path_btn: Button to remove selected paths
        button_box: Dialog button box with Ok/Cancel

    Public methods:
        exec: Show dialog and return result
        get_paths: Get list of paths from the list widget
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        dotfile_data: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the AddDotfileDialog.

        Args:
            parent: Parent widget
            dotfile_data: Optional existing dotfile data for update mode
        """
        super().__init__(parent)
        self.is_update_mode = dotfile_data is not None

        self._load_ui()

        self.setWindowTitle(
            "Update Dotfile Entry" if self.is_update_mode else "Add Dotfile Entry"
        )
        self.setMinimumWidth(MIN_DIALOG_WIDTH)
        self.setMinimumHeight(MIN_DIALOG_HEIGHT)

        info_text = (
            "Update the dotfile entry:"
            if self.is_update_mode
            else "Add a new dotfile entry to the configuration:"
        )
        self.info_label.setText(info_text)

        self._connect_signals()

        if self.is_update_mode and dotfile_data:
            # 'tags' (new format) falls back to 'category' (legacy format)
            tags = dotfile_data.get("tags", dotfile_data.get("category", ""))
            self.tags_edit.setText(tags)
            self.application_edit.setText(dotfile_data.get("application", ""))
            self.description_edit.setText(dotfile_data.get("description", ""))
            self.enabled_checkbox.setChecked(dotfile_data.get("enabled", True))

            # 'paths' (new format) falls back to 'path' (legacy format)
            if "paths" in dotfile_data:
                for path_str in dotfile_data["paths"]:
                    self.paths_list.addItem(path_str)
            elif "path" in dotfile_data:
                self.paths_list.addItem(dotfile_data["path"])

    def _load_ui(self) -> None:
        """Load UI from Qt Designer .ui file."""
        ui_file_path = Path(__file__).parent / "designer" / "add_dotfile_dialog.ui"

        ui_file = QFile(str(ui_file_path))
        if not ui_file.open(QFile.OpenModeFlag.ReadOnly):
            raise RuntimeError(f"Cannot open UI file: {ui_file_path}")

        loader = QUiLoader()
        ui_widget = loader.load(ui_file, self)
        ui_file.close()

        if not isinstance(ui_widget, QDialog):
            raise RuntimeError("Loaded UI is not a QDialog")

        # Transfer layout from loaded widget to this dialog
        loaded_layout = ui_widget.layout()
        if loaded_layout:
            self.setLayout(loaded_layout)

        self.info_label: QLabel = self.findChild(QLabel, "infoLabel")  # type: ignore[assignment]
        self.tags_edit: QLineEdit = self.findChild(QLineEdit, "tagsEdit")  # type: ignore[assignment]
        self.application_edit: QLineEdit = self.findChild(QLineEdit, "applicationEdit")  # type: ignore[assignment]
        self.description_edit: QLineEdit = self.findChild(QLineEdit, "descriptionEdit")  # type: ignore[assignment]
        self.paths_list: QListWidget = self.findChild(QListWidget, "pathsList")  # type: ignore[assignment]
        self.path_input_edit: QLineEdit = self.findChild(QLineEdit, "pathInputEdit")  # type: ignore[assignment]
        self.browse_btn: QPushButton = self.findChild(QPushButton, "browseBtn")  # type: ignore[assignment]
        self.add_path_btn: QPushButton = self.findChild(QPushButton, "addPathBtn")  # type: ignore[assignment]
        self.remove_path_btn: QPushButton = self.findChild(QPushButton, "removePathBtn")  # type: ignore[assignment]
        self.enabled_checkbox: QCheckBox = self.findChild(QCheckBox, "enabledCheckbox")  # type: ignore[assignment]
        self.button_box: QDialogButtonBox = self.findChild(
            QDialogButtonBox, "buttonBox"
        )  # type: ignore[assignment]

        if not all(
            [
                self.info_label,
                self.tags_edit,
                self.application_edit,
                self.description_edit,
                self.paths_list,
                self.path_input_edit,
                self.browse_btn,
                self.add_path_btn,
                self.remove_path_btn,
                self.enabled_checkbox,
                self.button_box,
            ]
        ):
            raise RuntimeError("Required widgets not found in UI file")

    def _connect_signals(self) -> None:
        """Connect widget signals to handler methods."""
        self.browse_btn.clicked.connect(self._on_browse_path)
        self.add_path_btn.clicked.connect(self._on_add_path)
        self.remove_path_btn.clicked.connect(self._on_remove_paths)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def _on_browse_path(self) -> None:
        """Open a unified file/directory picker.

        Uses a non-native QFileDialog that allows selecting either files
        or directories from a single dialog, without a type prompt.
        """
        dialog = QFileDialog(self, "Select File or Directory", str(Path.home()))
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setLabelText(QFileDialog.DialogLabel.Accept, "Select")
        dialog.setNameFilter("All Files (*)")

        def get_path_from_line_edit() -> Path | None:
            """Get path candidate from the dialog's filename line edit."""
            line_edit = dialog.findChild(QLineEdit, "fileNameEdit")
            if line_edit:
                name = line_edit.text().strip()
                if name:
                    return Path(dialog.directory().absolutePath()) / name
            return None

        # Override accept to also allow directory selection.
        # By default, clicking "Select" on a highlighted directory enters it.
        # This patch makes it accept the directory path instead.
        def accept_with_dirs() -> None:
            candidate = get_path_from_line_edit()
            if candidate and candidate.is_dir():
                dialog.done(QDialog.DialogCode.Accepted)
                return
            QFileDialog.accept(dialog)

        dialog.accept = accept_with_dirs  # type: ignore[method-assign]

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.selectedFiles()
            if selected:
                chosen = selected[0]
                # Fallback: selectedFiles() may return the entered directory name, not the full path
                if not Path(chosen).exists():
                    candidate = get_path_from_line_edit()
                    if candidate and candidate.exists():
                        chosen = str(candidate)
                self.path_input_edit.setText(chosen)

    def _on_add_path(self) -> None:
        """Add path from input field to paths list."""
        path_text = self.path_input_edit.text().strip()

        if not path_text:
            return

        validation_result = InputValidator.validate_path(path_text, must_exist=False)
        if not validation_result.success:
            QMessageBox.warning(self, "Invalid Path", validation_result.error_message)
            return

        for i in range(self.paths_list.count()):
            if self.paths_list.item(i).text() == path_text:
                QMessageBox.warning(
                    self, "Duplicate Path", "This path is already in the list."
                )
                return

        self.paths_list.addItem(path_text)
        self.path_input_edit.clear()

    def _on_remove_paths(self) -> None:
        """Remove selected paths from list."""
        selected_items = self.paths_list.selectedItems()

        for item in selected_items:
            self.paths_list.takeItem(self.paths_list.row(item))

    def accept(self) -> None:
        """
        Override accept to validate input before closing dialog.

        Validates all fields and shows error message if validation fails.
        """
        tags = self.tags_edit.text().strip()
        validation_result = InputValidator.validate_string(
            tags, field_name="Tags", allow_empty=True, max_length=200
        )
        if not validation_result.success:
            QMessageBox.warning(
                self, "Validation Error", validation_result.error_message
            )
            self.tags_edit.setFocus()
            return

        application = self.application_edit.text().strip()
        validation_result = InputValidator.validate_string(
            application, field_name="Application", min_length=1, max_length=100
        )
        if not validation_result.success:
            QMessageBox.warning(
                self, "Validation Error", validation_result.error_message
            )
            self.application_edit.setFocus()
            return

        description = self.description_edit.text().strip()
        validation_result = InputValidator.validate_string(
            description,
            field_name="Description",
            allow_empty=True,
            max_length=255,
        )
        if not validation_result.success:
            QMessageBox.warning(
                self, "Validation Error", validation_result.error_message
            )
            self.description_edit.setFocus()
            return

        paths = self.get_paths()
        if not paths:
            QMessageBox.warning(
                self,
                "Validation Error",
                "At least one path is required.",
            )
            self.path_input_edit.setFocus()
            return

        for path_str in paths:
            validation_result = InputValidator.validate_path(path_str, must_exist=False)
            if not validation_result.success:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    f"Invalid path '{path_str}': {validation_result.error_message}",
                )
                return

        super().accept()

    def get_paths(self) -> list[str]:
        """
        Get list of paths from the list widget.

        Returns:
            List of path strings
        """
        paths: list[str] = []
        for i in range(self.paths_list.count()):
            path_text = self.paths_list.item(i).text().strip()
            if path_text:
                paths.append(path_text)
        return paths


class MainWindow(QMainWindow):
    """
    Main application window implementing the GUI interface.

    Attributes:
        viewmodel: DFBUViewModel for presentation logic
        central_widget: Main central widget
        tab_widget: Tab widget for different views
        dotfile_table: Table widget for dotfile display
        add_dotfile_btn: Button to add new dotfile entry
        update_dotfile_btn: Button to update selected dotfile entry
        remove_dotfile_btn: Button to remove selected dotfile entry
        save_dotfiles_btn: Button to save dotfile configuration changes
        backup_btn: Button to start backup
        mirror_checkbox: Checkbox for mirror backup mode
        archive_checkbox: Checkbox for archive backup mode
        force_full_backup_checkbox: Checkbox to force copying all files
        restore_source_edit: Line edit for restore source directory
        browse_restore_btn: Button to browse for restore source
        restore_btn: Button to start restore operation
        options_text: Text edit for options display
        config_mirror_checkbox: Checkbox for mirror backup mode
        config_archive_checkbox: Checkbox for archive backup mode
        config_hostname_checkbox: Checkbox for hostname subdirectory
        config_date_checkbox: Checkbox for date subdirectory
        config_compression_spinbox: SpinBox for compression level
        config_rotate_checkbox: Checkbox for archive rotation
        config_max_archives_spinbox: SpinBox for max archives
        config_mirror_path_edit: Line edit for mirror directory path
        config_archive_path_edit: Line edit for archive directory path
        save_config_btn: Button to save configuration changes
        progress_label: Label for progress text
        progress_bar: Progress bar widget
        operation_log: Text edit for operation log
        status_bar: Status bar widget

    Public methods:
        setup_ui: Initialize the user interface
        setup_menu_bar: Create the application menu bar
        setup_backup_tab: Create the backup operations tab
        setup_restore_tab: Create the restore operations tab
        setup_config_tab: Create the configuration display tab
        closeEvent: Handle application close event

    Private methods:
        _on_add_dotfile: Handle add dotfile button click
        _on_update_dotfile: Handle update dotfile button click
        _on_remove_dotfile: Handle remove dotfile button click
        _on_save_dotfile_config: Handle save dotfile configuration button click
        _on_dotfile_selection_changed: Handle dotfile table selection change
        Various other private methods for UI setup and event handling
    """

    PROJECT_NAME: Final[str] = "DFBU GUI"

    def __init__(self, viewmodel: DFBUViewModel, version: str) -> None:
        """
        Initialize the MainWindow.

        Args:
            viewmodel: DFBUViewModel instance
            version: Application version string
        """
        super().__init__()
        self.viewmodel: DFBUViewModel = viewmodel
        self.version: str = version

        self._skipped_count: int = 0
        self._log_entries: list[tuple[str, str]] = []

        # Filter input reference (set up in _setup_filter_ui)
        self._filter_input: QLineEdit | None = None

        self.setup_ui()
        self._connect_viewmodel_signals()
        self._load_settings()

    def setup_ui(self) -> None:
        """Initialize the user interface by loading from .ui file."""
        ui_file_path = Path(__file__).parent / "designer" / "main_window_complete.ui"
        loader = QUiLoader()
        loaded_window = loader.load(str(ui_file_path), None)

        # QUiLoader.load() returns QWidget, but we know from the .ui file it's QMainWindow.
        # Qt doesn't allow QMainWindow-within-QMainWindow, so we extract and reparent components.
        ui_widget: QWidget | None = None

        if isinstance(loaded_window, QMainWindow):
            central = loaded_window.centralWidget()
            if isinstance(central, QWidget):
                ui_widget = central
                ui_widget.setParent(self)
                self.setCentralWidget(ui_widget)

            menu = loaded_window.menuBar()
            if menu is not None:
                # setMenuBar without reparenting avoids object lifecycle issues
                self.setMenuBar(menu)

            status = loaded_window.statusBar()
            if status is not None:
                status.setParent(self)
                self.setStatusBar(status)
        elif isinstance(loaded_window, QWidget):
            ui_widget = loaded_window
            ui_widget.setParent(self)
            self.setCentralWidget(ui_widget)

        if ui_widget is None:
            raise RuntimeError("Failed to load UI from .ui file")

        self.setWindowTitle(f"{self.PROJECT_NAME} v{self.version}")

        self._setup_widget_references(ui_widget)
        self._connect_ui_signals()
        self._setup_shortcuts()
        self._configure_table_widget()

        if self._backup_stacked_widget:
            self._backup_stacked_widget.setCurrentIndex(0)

        self._tooltip_manager = TooltipManager()
        self._tooltip_manager.apply_tooltips(self)

        self.status_bar.showMessage("Ready - Load configuration to begin")

    def _setup_widget_references(self, ui_widget: QWidget) -> None:
        """
        Get references to UI elements from the loaded widget.

        Args:
            ui_widget: Central widget containing all UI elements
        """
        self.central_widget: QWidget = ui_widget
        found_tab = ui_widget.findChild(QTabWidget, "tab_widget")
        if not isinstance(found_tab, QTabWidget):
            raise RuntimeError("Required widget 'tab_widget' not found in UI file")
        self.tab_widget: QTabWidget = found_tab

        self._find_backup_tab_widgets(ui_widget)
        self._find_logs_tab_widgets(
            ui_widget
        )  # CONSTRAINT: must run before restore to set operation_log
        self._find_restore_tab_widgets(ui_widget)
        self._find_config_tab_widgets(ui_widget)
        self._find_status_widgets()
        self._find_header_widgets(ui_widget)

    def _find_backup_tab_widgets(self, ui_widget: QWidget) -> None:
        """Find and store references to Backup tab widgets."""
        self.dotfile_table: QTableWidget = ui_widget.findChild(
            QTableWidget, "fileGroupFileTable"
        )  # type: ignore[assignment]
        self._filter_input = ui_widget.findChild(QLineEdit, "filterLineEdit")
        self.total_size_label: QLabel = ui_widget.findChild(
            QLabel, "fileGroupTotalSizeLabel"
        )  # type: ignore[assignment]
        self.add_dotfile_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupAddFileButton"
        )  # type: ignore[assignment]
        self.update_dotfile_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupUpdateFileButton"
        )  # type: ignore[assignment]
        self.remove_dotfile_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupRemoveFileButton"
        )  # type: ignore[assignment]
        self.toggle_enabled_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupToggleEnabledButton"
        )  # type: ignore[assignment]
        self.save_dotfiles_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupSaveFilesButton"
        )  # type: ignore[assignment]
        self.mirror_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "mirrorCheckbox"
        )  # type: ignore[assignment]
        self.archive_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "archiveCheckbox"
        )  # type: ignore[assignment]
        self.force_full_backup_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "forceBackupCheckbox"
        )  # type: ignore[assignment]
        self.backup_btn: QPushButton = ui_widget.findChild(
            QPushButton, "startBackupButton"
        )  # type: ignore[assignment]
        self._hide_missing_checkbox: QCheckBox | None = ui_widget.findChild(
            QCheckBox, "hideMissingCheckbox"
        )
        self.edit_config_btn: QPushButton = ui_widget.findChild(
            QPushButton, "editConfigButton"
        )  # type: ignore[assignment]
        self.validate_config_btn: QPushButton = ui_widget.findChild(
            QPushButton, "validateConfigButton"
        )  # type: ignore[assignment]
        self.export_config_btn: QPushButton = ui_widget.findChild(
            QPushButton, "exportConfigButton"
        )  # type: ignore[assignment]
        self.import_config_btn: QPushButton = ui_widget.findChild(
            QPushButton, "importConfigButton"
        )  # type: ignore[assignment]
        self._backup_stacked_widget: QStackedWidget | None = ui_widget.findChild(
            QStackedWidget, "backupStackedWidget"
        )
        self._empty_state_add_btn: QPushButton | None = ui_widget.findChild(
            QPushButton, "emptyStateAddButton"
        )

    def _find_restore_tab_widgets(self, ui_widget: QWidget) -> None:
        """Find and store references to Restore tab widgets."""
        self.restore_source_edit: QLineEdit = ui_widget.findChild(
            QLineEdit, "restoreSourceEdit"
        )  # type: ignore[assignment]
        self.browse_restore_btn: QPushButton = ui_widget.findChild(
            QPushButton, "restoreSourceBrowseButton"
        )  # type: ignore[assignment]
        self.restore_btn: QPushButton = ui_widget.findChild(
            QPushButton, "restoreSourceButton"
        )  # type: ignore[assignment]
        # SIDE-EFFECT: restore_operation_log aliases operation_log (same widget, shared between tabs)
        self.restore_operation_log: QTextEdit = self.operation_log

        self.restore_preview_group: QGroupBox = ui_widget.findChild(
            QGroupBox, "restorePreviewGroup"
        )  # type: ignore[assignment]
        self.restore_preview_host_label: QLabel = ui_widget.findChild(
            QLabel, "restorePreviewHostLabel"
        )  # type: ignore[assignment]
        self.restore_preview_count_label: QLabel = ui_widget.findChild(
            QLabel, "restorePreviewCountLabel"
        )  # type: ignore[assignment]
        self.restore_preview_size_label: QLabel = ui_widget.findChild(
            QLabel, "restorePreviewSizeLabel"
        )  # type: ignore[assignment]
        self.restore_preview_tree: QTreeWidget = ui_widget.findChild(
            QTreeWidget, "restorePreviewTree"
        )  # type: ignore[assignment]

    def _find_config_tab_widgets(self, ui_widget: QWidget) -> None:
        """Find and store references to Configuration tab widgets."""
        self.config_mirror_path_edit: QLineEdit = ui_widget.findChild(
            QLineEdit, "config_mirror_path_edit"
        )  # type: ignore[assignment]
        self.config_archive_path_edit: QLineEdit = ui_widget.findChild(
            QLineEdit, "configArchivePathEdit"
        )  # type: ignore[assignment]
        self.config_mirror_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_mirror_checkbox"
        )  # type: ignore[assignment]
        self.config_archive_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_archive_checkbox"
        )  # type: ignore[assignment]
        self.config_hostname_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_hostname_checkbox"
        )  # type: ignore[assignment]
        self.config_date_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_date_checkbox"
        )  # type: ignore[assignment]
        self.config_compression_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_compression_spinbox"
        )  # type: ignore[assignment]
        self.config_rotate_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_rotate_checkbox"
        )  # type: ignore[assignment]
        self.config_max_archives_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_max_archives_spinbox"
        )  # type: ignore[assignment]
        self.config_pre_restore_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_pre_restore_checkbox"
        )  # type: ignore[assignment]
        self.config_max_restore_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_max_restore_spinbox"
        )  # type: ignore[assignment]
        self.config_restore_path_edit: QLineEdit = ui_widget.findChild(
            QLineEdit, "config_restore_path_edit"
        )  # type: ignore[assignment]
        self.browse_restore_backup_btn: QPushButton = ui_widget.findChild(
            QPushButton, "browse_restore_btn"
        )  # type: ignore[assignment]
        self.save_config_btn: QPushButton = ui_widget.findChild(
            QPushButton, "saveConfigButton"
        )  # type: ignore[assignment]
        self.config_verify_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_verify_checkbox"
        )  # type: ignore[assignment]
        self.config_hash_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_hash_checkbox"
        )  # type: ignore[assignment]
        self.config_size_check_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_size_check_checkbox"
        )  # type: ignore[assignment]
        self.config_size_warning_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_size_warning_spinbox"
        )  # type: ignore[assignment]
        self.config_size_alert_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_size_alert_spinbox"
        )  # type: ignore[assignment]
        self.config_size_critical_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_size_critical_spinbox"
        )  # type: ignore[assignment]

    def _find_logs_tab_widgets(self, ui_widget: QWidget) -> None:
        """Find and store references to log pane widgets (split view)."""
        self.operation_log: QTextEdit = ui_widget.findChild(QTextEdit, "logPaneBox")  # type: ignore[assignment]

        if not self.operation_log:
            raise RuntimeError("logPaneBox widget not found in UI file!")

        self.verify_backup_btn: QPushButton = ui_widget.findChild(
            QPushButton, "logPaneVerifyButton"
        )  # type: ignore[assignment]
        self.save_log_btn: QPushButton = ui_widget.findChild(
            QPushButton, "logPaneSaveButton"
        )  # type: ignore[assignment]
        self._log_filter_all_btn: QPushButton = ui_widget.findChild(
            QPushButton, "logPaneFilterAllButton"
        )  # type: ignore[assignment]
        self._log_filter_info_btn: QPushButton = ui_widget.findChild(
            QPushButton, "logPaneFilterInfoButton"
        )  # type: ignore[assignment]
        self._log_filter_warning_btn: QPushButton = ui_widget.findChild(
            QPushButton, "logPaneFilterWarningButton"
        )  # type: ignore[assignment]
        self._log_filter_error_btn: QPushButton = ui_widget.findChild(
            QPushButton, "logPaneFilterErrorButton"
        )  # type: ignore[assignment]
        self._log_clear_btn: QPushButton = ui_widget.findChild(
            QPushButton, "logPaneClearButton"
        )  # type: ignore[assignment]
        self._log_verbose_btn: QPushButton = ui_widget.findChild(
            QPushButton, "logPaneVerboseButton"
        )  # type: ignore[assignment]

    def _find_status_widgets(self) -> None:
        """Find and store references to status bar widgets."""
        self.status_bar = self.statusBar()
        self.progress_bar: QProgressBar = self.status_bar.findChild(
            QProgressBar, "progress_bar"
        )  # type: ignore[assignment]

    def _find_header_widgets(self, ui_widget: QWidget) -> None:
        """Find and store references to header bar widgets."""
        self._help_btn: QPushButton = ui_widget.findChild(QPushButton, "helpButton")  # type: ignore[assignment]
        self._about_btn: QPushButton = ui_widget.findChild(QPushButton, "aboutButton")  # type: ignore[assignment]
        self._theme_toggle_btn: QPushButton | None = ui_widget.findChild(
            QPushButton, "themeToggleButton"
        )

    def _connect_ui_signals(self) -> None:
        """Connect UI element signals to handler methods."""
        self.add_dotfile_btn.clicked.connect(self._on_add_dotfile)
        self.update_dotfile_btn.clicked.connect(self._on_update_dotfile)
        self.remove_dotfile_btn.clicked.connect(self._on_remove_dotfile)
        self.toggle_enabled_btn.clicked.connect(self._on_toggle_dotfile_enabled)
        self.save_dotfiles_btn.clicked.connect(self._on_save_dotfile_config)
        self.mirror_checkbox.stateChanged.connect(self._on_mirror_checkbox_changed)
        self.archive_checkbox.stateChanged.connect(self._on_archive_checkbox_changed)
        self.backup_btn.clicked.connect(self._on_start_backup)
        self.dotfile_table.itemSelectionChanged.connect(
            self._on_dotfile_selection_changed
        )
        self.edit_config_btn.clicked.connect(self._on_edit_config)
        self.validate_config_btn.clicked.connect(self._on_validate_config)
        self.export_config_btn.clicked.connect(self._on_export_config)
        self.import_config_btn.clicked.connect(self._on_import_config)

        if self._filter_input:
            self._filter_input.textChanged.connect(self._apply_combined_filters)

        if self._hide_missing_checkbox:
            self._hide_missing_checkbox.stateChanged.connect(
                self._apply_combined_filters
            )

        if self._empty_state_add_btn:
            self._empty_state_add_btn.clicked.connect(self._on_add_dotfile)

        self.browse_restore_btn.clicked.connect(self._on_browse_restore_source)
        self.restore_btn.clicked.connect(self._on_start_restore)

        browse_mirror_btn: QPushButton = self.central_widget.findChild(
            QPushButton, "browse_mirror_btn"
        )  # type: ignore[assignment]
        browse_archive_btn: QPushButton = self.central_widget.findChild(
            QPushButton, "browseArchiveButton"
        )  # type: ignore[assignment]
        browse_mirror_btn.clicked.connect(self._on_browse_mirror_dir)
        browse_archive_btn.clicked.connect(self._on_browse_archive_dir)
        self.config_mirror_path_edit.textChanged.connect(self._on_config_changed)
        self.config_archive_path_edit.textChanged.connect(self._on_config_changed)
        self.config_mirror_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_archive_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_hostname_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_date_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_compression_spinbox.valueChanged.connect(self._on_config_changed)
        self.config_rotate_checkbox.stateChanged.connect(
            self._on_rotate_checkbox_changed
        )
        self.config_rotate_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_max_archives_spinbox.valueChanged.connect(self._on_config_changed)
        self.config_pre_restore_checkbox.stateChanged.connect(
            self._on_pre_restore_checkbox_changed
        )
        self.config_pre_restore_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_max_restore_spinbox.valueChanged.connect(self._on_config_changed)
        self.config_restore_path_edit.textChanged.connect(self._on_config_changed)
        self.browse_restore_backup_btn.clicked.connect(
            self._on_browse_restore_backup_dir
        )
        self.save_config_btn.clicked.connect(self._on_save_config)
        self.config_verify_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_hash_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_size_check_checkbox.stateChanged.connect(
            self._on_size_check_checkbox_changed
        )
        self.config_size_check_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_size_warning_spinbox.valueChanged.connect(self._on_config_changed)
        self.config_size_alert_spinbox.valueChanged.connect(self._on_config_changed)
        self.config_size_critical_spinbox.valueChanged.connect(self._on_config_changed)

        self.verify_backup_btn.clicked.connect(self._on_verify_backup)
        self.save_log_btn.clicked.connect(self._on_save_log)

        self._log_filter_all_btn.clicked.connect(self._on_log_filter_all)
        self._log_filter_info_btn.clicked.connect(self._on_log_filter_changed)
        self._log_filter_warning_btn.clicked.connect(self._on_log_filter_changed)
        self._log_filter_error_btn.clicked.connect(self._on_log_filter_changed)
        self._log_clear_btn.clicked.connect(self._on_clear_log)

        if self._help_btn:
            self._help_btn.clicked.connect(self._show_user_guide)
        if self._about_btn:
            self._about_btn.clicked.connect(self._show_about)
        if self._theme_toggle_btn:
            self._theme_toggle_btn.clicked.connect(self._on_toggle_theme)

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts for actions previously in menus."""
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F1"), self, self._show_user_guide)
        QShortcut(QKeySequence("Ctrl+B"), self, self._on_start_backup)
        QShortcut(QKeySequence("Ctrl+R"), self, self._on_start_restore)
        QShortcut(QKeySequence("Ctrl+V"), self, self._on_verify_backup)
        QShortcut(QKeySequence("Ctrl+T"), self, self._on_toggle_theme)

    def _configure_table_widget(self) -> None:
        """Configure the dotfile table widget properties.

        Column structure:
            0: Included (checkbox indicator)
            1: Status (file exists)
            2: Application
            3: Tags
            4: Size
            5: Path (stretch)
        """
        header = self.dotfile_table.horizontalHeader()
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )  # Included
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # Status
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # Application
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Tags
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Path

    def _connect_viewmodel_signals(self) -> None:
        """Connect ViewModel signals to View slots."""
        self.viewmodel.progress_updated.connect(self._on_progress_updated)
        self.viewmodel.item_processed.connect(self._on_item_processed)
        self.viewmodel.item_skipped.connect(self._on_item_skipped)
        self.viewmodel.operation_finished.connect(self._on_operation_finished)
        self.viewmodel.error_occurred.connect(self._on_error_occurred)
        self.viewmodel.config_loaded.connect(self._on_config_loaded)
        self.viewmodel.dotfiles_updated.connect(self._on_dotfiles_updated)
        self.viewmodel.exclusions_changed.connect(self._on_exclusions_changed)
        self.viewmodel.recovery_dialog_requested.connect(self._show_recovery_dialog)
        self.viewmodel.size_warning_requested.connect(self._show_size_warning_dialog)
        self.viewmodel.size_scan_progress.connect(self._on_size_scan_progress)

    def _load_settings(self) -> None:
        """Load persisted settings."""
        settings = self.viewmodel.load_settings()

        if settings.get("geometry"):
            self.restoreGeometry(settings["geometry"])
        if settings.get("window_state"):
            self.restoreState(settings["window_state"])

        if settings.get("restore_source"):
            self.restore_source_edit.setText(settings["restore_source"])
            self.restore_btn.setEnabled(True)

        self._update_theme_toggle_button()

    def _on_start_backup(self) -> None:
        """Handle start backup button click."""
        if self.viewmodel.get_dotfile_count() == 0:
            QMessageBox.warning(
                self, "No Configuration", "Please load a configuration file first."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Backup",
            "Start backup operation with current configuration?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._skipped_count = 0

            self.operation_log.clear()
            self._log_entries.clear()
            self._append_log("=== Backup Operation Started ===", "header")

            # Disable buttons during operation
            self.backup_btn.setEnabled(False)

            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            force_full = self.force_full_backup_checkbox.isChecked()

            if force_full:
                self._append_log(
                    "INFO: Force Full Backup - All files will be copied", "info"
                )
            else:
                self._append_log(
                    "INFO: Smart Backup - Only changed files will be copied", "info"
                )

            success = self.viewmodel.command_start_backup(force_full_backup=force_full)

            if not success:
                self.backup_btn.setEnabled(True)
                self.progress_bar.setVisible(False)
                self._append_log("✗ Failed to start backup operation", "error")

    def _on_browse_restore_source(self) -> None:
        """Handle browse restore source button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Restore Source Directory", str(Path.home())
        )

        if directory:
            self.restore_source_edit.setText(directory)

            if self.viewmodel.command_set_restore_source(Path(directory)):
                self.restore_btn.setEnabled(True)

                metadata = self.viewmodel.command_scan_restore_source(Path(directory))
                if metadata:
                    self._populate_restore_preview(metadata)
            else:
                QMessageBox.warning(
                    self, "Invalid Directory", "Selected path is not a valid directory."
                )
                self.restore_btn.setEnabled(False)

    def _populate_restore_preview(self, metadata: dict[str, Any]) -> None:
        """Populate the restore preview section with scan results."""
        self.restore_preview_host_label.setText(
            f"Hostname: {metadata['hostname'] or 'Unknown'}"
        )
        self.restore_preview_count_label.setText(f"Files: {metadata['file_count']}")
        self.restore_preview_size_label.setText(
            f"Size: {self._format_size(metadata['total_size'])}"
        )

        self.restore_preview_tree.clear()
        for entry in metadata["entries"]:
            file_count: int = entry["file_count"]
            app_item = QTreeWidgetItem(
                [
                    entry["application"],
                    f"{file_count} file{'s' if file_count != 1 else ''}",
                    self._format_size(entry["total_size"]),
                ]
            )

            for file_info in entry["files"]:
                QTreeWidgetItem(
                    app_item,
                    [
                        file_info["name"],
                        "",
                        self._format_size(file_info["size"]),
                    ],
                )

            self.restore_preview_tree.addTopLevelItem(app_item)

        self.restore_preview_tree.expandAll()
        self.restore_preview_group.setVisible(True)

    def _format_size(self, size_bytes: int) -> str:
        """Format a byte count as a human-readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _on_start_restore(self) -> None:
        """Handle start restore button click."""
        if not self.restore_source_edit.text():
            QMessageBox.warning(
                self, "No Source", "Please select a restore source directory first."
            )
            return

        reply = QMessageBox.warning(
            self,
            "Confirm Restore",
            "This operation will restore files to their original locations.\n"
            "Existing files will be overwritten.\n\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.restore_operation_log.clear()

            self.restore_btn.setEnabled(False)
            self.browse_restore_btn.setEnabled(False)

            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            self.viewmodel.command_start_restore()

    def _on_progress_updated(self, value: int) -> None:
        """Handle progress updates."""
        self.progress_bar.setValue(value)

    def _on_item_processed(self, source: str, destination: str) -> None:
        """Handle item processed signal."""
        if self._log_verbose_btn and self._log_verbose_btn.isChecked():
            log_message = f"✓ {Path(source).name} → {destination}"
        else:
            log_message = f"✓ {Path(source).name} → {Path(destination).name}"
        self._append_log(log_message, "success")

    def _on_item_skipped(self, path: str, reason: str) -> None:
        """Handle item skipped signal — log each file individually."""
        self._skipped_count += 1
        name = Path(path).name

        if self._log_verbose_btn and self._log_verbose_btn.isChecked():
            log_message = f"⊘ {name} ({reason}) [{path}]"
        else:
            log_message = f"⊘ {name} ({reason})"
        self._append_log(log_message, "skip")

    def _on_operation_finished(self, summary: str) -> None:
        """Handle operation finished signal."""
        self.progress_bar.setVisible(False)

        self.backup_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.browse_restore_btn.setEnabled(True)

        if (
            self.viewmodel.backup_worker
            and not self.viewmodel.backup_worker.isRunning()
        ):
            if self._skipped_count > 0:
                self._append_log(
                    f"⊘ Total unchanged files: {self._skipped_count}",
                    "skip",
                )
            self._append_log("=== Backup Operation Completed ===", "header")
            self._append_log(summary, "info")
            self.operation_log.verticalScrollBar().setValue(
                self.operation_log.verticalScrollBar().maximum()
            )
        elif (
            self.viewmodel.restore_worker
            and not self.viewmodel.restore_worker.isRunning()
        ):
            self._append_log("=== Restore Operation Completed ===", "header")
            self._append_log(summary, "info")
            self.operation_log.verticalScrollBar().setValue(
                self.operation_log.verticalScrollBar().maximum()
            )

    def _on_error_occurred(self, context: str, error_message: str) -> None:
        """Handle error signal."""
        log_message = f"✗ Error in {context}: {error_message}"
        self._append_log(log_message, "error")

        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

        self.backup_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.browse_restore_btn.setEnabled(True)

    def _on_config_loaded(self, dotfile_count: int) -> None:
        """Handle configuration loaded signal."""
        self.status_bar.showMessage(f"Configuration loaded: {dotfile_count} dotfiles")
        self.backup_btn.setEnabled(True)
        self.save_dotfiles_btn.setEnabled(True)

        self._update_dotfile_table()
        self._update_options_display()

    def _update_dotfile_table(self) -> None:
        """Update the dotfile table with current configuration (with full validation)."""
        dotfiles = self.viewmodel.get_dotfile_list()
        validation = self.viewmodel.get_dotfile_validation()
        sizes = self.viewmodel.get_dotfile_sizes()
        self._populate_dotfile_table(dotfiles, validation, sizes)

    def _update_dotfile_table_fast(self) -> None:
        """
        Fast update of dotfile table without filesystem validation.

        Used for operations that only change metadata (like toggling inclusion status)
        but don't affect file existence. Reuses cached validation and size data.

        Column structure:
            0: Included, 1: Status, 2: Application, 3: Tags, 4: Size, 5: Path
        """
        dotfiles = self.viewmodel.get_dotfile_list()

        # Reuses cached validation/size from current table to avoid filesystem re-validation
        validation: dict[int, tuple[bool, bool, str]] = {}
        sizes: dict[int, int] = {}

        idx_to_row: dict[int, int] = {}
        for row in range(self.dotfile_table.rowCount()):
            original_idx = self._get_original_dotfile_index(row)
            idx_to_row[original_idx] = row

        for i in range(len(dotfiles)):
            if i in idx_to_row:
                row = idx_to_row[i]
                status_item = self.dotfile_table.item(row, 1)  # column 1 = Status
                size_item = self.dotfile_table.item(row, 4)  # column 4 = Size

                if status_item and size_item:
                    exists = status_item.text() == "✓"
                    # is_dir not tracked per-row; defaults to False
                    validation[i] = (exists, False, "File")

                    size_data = size_item.data(Qt.ItemDataRole.UserRole)
                    sizes[i] = size_data if isinstance(size_data, int) else 0
                else:
                    validation[i] = (False, False, "File")
                    sizes[i] = 0
            else:
                # New item not yet in table
                validation[i] = (False, False, "File")
                sizes[i] = 0

        self._populate_dotfile_table(dotfiles, validation, sizes)

    def _populate_dotfile_table(
        self,
        dotfiles: list[LegacyDotFileDict],
        validation: dict[int, tuple[bool, bool, str]],
        sizes: dict[int, int],
    ) -> None:
        """
        Populate the dotfile table with given data.

        Args:
            dotfiles: List of dotfile dictionaries
            validation: Validation results mapping index to (exists, is_dir, type_str)
            sizes: Size results mapping index to size in bytes
        """
        # CONSTRAINT: sorting must be disabled during population to prevent row thrashing
        self.dotfile_table.setSortingEnabled(False)

        dotfile_data = [
            (i, dotfile, validation[i], sizes[i]) for i, dotfile in enumerate(dotfiles)
        ]

        self.dotfile_table.setRowCount(len(dotfiles))

        total_enabled_size = 0

        for row_idx, (
            original_idx,
            dotfile,
            (exists, _is_dir, _type_str),
            size,
        ) in enumerate(dotfile_data):
            self._create_table_row_items(row_idx, original_idx, dotfile, exists, size)

            enabled = dotfile.get("enabled", True)
            if enabled and exists:
                total_enabled_size += size

        self.total_size_label.setText(
            f"Total Size (enabled): {self.viewmodel.format_size(total_enabled_size)}"
        )

        self.dotfile_table.setSortingEnabled(True)

    def _create_table_row_items(
        self,
        row_idx: int,
        original_idx: int,
        dotfile: LegacyDotFileDict,
        exists: bool,
        size: int,
    ) -> None:
        """
        Create and populate table items for a single dotfile row.

        Column structure:
            0: Included (checkbox indicator) - checked = included, unchecked = excluded
            1: Status (file exists)
            2: Application
            3: Tags
            4: Size
            5: Path

        Args:
            row_idx: Row index in table
            original_idx: Original index in dotfiles list
            dotfile: Dotfile dictionary (LegacyDotFileDict with application key)
            exists: Whether the dotfile exists on filesystem
            size: Total size in bytes
        """
        application = dotfile["application"]

        # "enabled" in legacy format reflects "not excluded" — checked = included
        included = dotfile.get("enabled", True)
        indicator = "✓" if included else "✗"
        included_item = QTableWidgetItem(indicator)
        included_item.setData(
            Qt.ItemDataRole.UserRole, original_idx
        )  # Store original index
        if included:
            included_item.setForeground(QColor(DFBUColors.SUCCESS))
        else:
            included_item.setForeground(QColor(DFBUColors.TEXT_DISABLED))
        self.dotfile_table.setItem(row_idx, 0, included_item)

        status_item = QTableWidgetItem("✓" if exists else "✗")
        if exists:
            status_item.setForeground(QColor(DFBUColors.SUCCESS))
        else:
            status_item.setForeground(QColor(DFBUColors.CRITICAL))
        self.dotfile_table.setItem(row_idx, 1, status_item)

        self.dotfile_table.setItem(row_idx, 2, QTableWidgetItem(application))

        # 'category' serves as tags in legacy format
        tags = dotfile["category"]
        self.dotfile_table.setItem(row_idx, 3, QTableWidgetItem(tags))

        size_str = self.viewmodel.format_size(size)
        size_item = NumericTableWidgetItem(size_str)
        # UserRole stores raw int for numeric sort (NumericTableWidgetItem.__lt__ reads it)
        size_item.setData(Qt.ItemDataRole.UserRole, size)
        size_item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.dotfile_table.setItem(row_idx, 4, size_item)

        paths = dotfile.get("paths", [])
        if len(paths) == 1:
            path_display = paths[0]
        else:
            path_display = f"{paths[0]} (+{len(paths) - 1} more)"

        path_item = QTableWidgetItem(path_display)
        tooltip_text = f"{dotfile.get('description', '')}\n\nPaths:\n{'\n'.join(paths)}"
        path_item.setToolTip(tooltip_text)
        self.dotfile_table.setItem(row_idx, 5, path_item)

    def _update_options_display(self) -> None:
        """Update the options display with current configuration."""
        options = self.viewmodel.get_options()

        self.config_mirror_checkbox.setChecked(options["mirror"])
        self.config_archive_checkbox.setChecked(options["archive"])
        self.config_hostname_checkbox.setChecked(options["hostname_subdir"])
        self.config_date_checkbox.setChecked(options["date_subdir"])
        self.config_compression_spinbox.setValue(options["archive_compression_level"])
        self.config_rotate_checkbox.setChecked(options["rotate_archives"])
        self.config_max_archives_spinbox.setValue(options["max_archives"])

        mirror_path = str(self.viewmodel.model.mirror_base_dir)
        archive_path = str(self.viewmodel.model.archive_base_dir)
        restore_backup_path = str(self.viewmodel.model.restore_backup_dir)
        self.config_mirror_path_edit.setText(mirror_path)
        self.config_archive_path_edit.setText(archive_path)
        self.config_restore_path_edit.setText(restore_backup_path)

        self.config_max_archives_spinbox.setEnabled(options["rotate_archives"])

        self.config_pre_restore_checkbox.setChecked(options["pre_restore_backup"])
        self.config_max_restore_spinbox.setValue(options["max_restore_backups"])
        self.config_max_restore_spinbox.setEnabled(options["pre_restore_backup"])

        self.config_verify_checkbox.setChecked(
            options.get("verify_after_backup", False)
        )
        self.config_hash_checkbox.setChecked(options.get("hash_verification", False))

        size_check_enabled = options.get("size_check_enabled", True)
        self.config_size_check_checkbox.setChecked(size_check_enabled)
        self.config_size_warning_spinbox.setValue(
            options.get("size_warning_threshold_mb", 10)
        )
        self.config_size_alert_spinbox.setValue(
            options.get("size_alert_threshold_mb", 100)
        )
        self.config_size_critical_spinbox.setValue(
            options.get("size_critical_threshold_mb", 1024)
        )
        self.config_size_warning_spinbox.setEnabled(size_check_enabled)
        self.config_size_alert_spinbox.setEnabled(size_check_enabled)
        self.config_size_critical_spinbox.setEnabled(size_check_enabled)

        self.save_config_btn.setEnabled(True)

        self.mirror_checkbox.setChecked(options["mirror"])
        self.archive_checkbox.setChecked(options["archive"])

    def _on_mirror_checkbox_changed(self, state: int) -> None:
        """Handle mirror checkbox state change."""
        self.viewmodel.set_mirror_mode(bool(state))

    def _on_archive_checkbox_changed(self, state: int) -> None:
        """Handle archive checkbox state change."""
        self.viewmodel.set_archive_mode(bool(state))

    def _show_about(self) -> None:
        """Show about dialog with brand icon."""
        about_box = QMessageBox(self)
        about_box.setWindowTitle(f"About {self.PROJECT_NAME}")
        about_box.setText(
            f"{self.PROJECT_NAME} v{self.version}\n\n"
            "Dotfiles Backup and Restore Utility\n\n"
            "A desktop application for backing up and restoring\n"
            "configuration files with metadata preservation.\n\n"
            "Author: Chris Purcell\n"
            "Email: chris@l3digital.net\n"
            "GitHub: https://github.com/L3DigitalNet"
        )

        icon_path = (
            Path(__file__).resolve().parent.parent
            / "resources"
            / "icons"
            / "dfbu-256.png"
        )
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path)).scaled(
                64,
                64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            about_box.setIconPixmap(pixmap)

        about_box.exec()

    def _show_user_guide(self) -> None:
        """Show user guide help dialog."""
        dialog = HelpDialog(self)
        dialog.exec()

    def _on_toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        current = get_current_theme()
        new_theme = "dfbu_dark" if current == "dfbu_light" else "dfbu_light"
        app = QApplication.instance()
        if app:
            load_theme(app, new_theme)  # type: ignore[arg-type]
            self._update_theme_toggle_button()
            self.viewmodel.save_theme_preference(new_theme)

    def _update_theme_toggle_button(self) -> None:
        """Update theme toggle button text and tooltip to reflect current theme."""
        if not self._theme_toggle_btn:
            return
        is_dark = get_current_theme() == "dfbu_dark"
        self._theme_toggle_btn.setText("Light" if is_dark else "Dark")
        self._theme_toggle_btn.setToolTip(
            "Switch to light mode" if is_dark else "Switch to dark mode"
        )

    def _show_recovery_dialog(self, result: OperationResultDict) -> None:
        """Show recovery dialog when operation has failures.

        Args:
            result: Operation result with failures
        """
        try:
            dialog = RecoveryDialog(result, parent=self)
            dialog.exec()
        except RuntimeError as e:
            self._append_log(f"✗ Recovery dialog error: {e}", "error")
            return

        if dialog.action == "retry":
            paths_to_retry = dialog.get_retryable_paths()
            self._append_log(
                f"↻ Retrying {len(paths_to_retry)} failed item(s)...", "info"
            )
            # TODO: Implement retry logic in v0.9.1
        elif dialog.action == "continue":
            self._append_log("⊘ Skipping failed items, operation complete.", "skip")
        else:  # abort
            self._append_log("✗ Operation aborted by user.", "error")

    def _show_size_warning_dialog(self, report: SizeReportDict) -> None:
        """Show size warning dialog before backup when large files detected.

        Args:
            report: Size analysis report with large files
        """
        try:
            dialog = SizeWarningDialog(report, parent=self)
            dialog.exec()
        except RuntimeError as e:
            self._append_log(f"✗ Size warning dialog error: {e}", "error")
            self._reset_backup_ui()
            return

        if dialog.action == "continue":
            self._append_log(
                f"⚠️ Size warning acknowledged: {report['total_size_mb']:.1f} MB total",
                "warning",
            )
            self.viewmodel.command_proceed_after_size_warning()
        else:  # cancel
            self._append_log("✗ Backup cancelled due to size concerns.", "error")
            self._reset_backup_ui()

    def _on_size_scan_progress(self, progress: int) -> None:
        """Handle size scan progress updates.

        Args:
            progress: Progress percentage (0-100)
        """
        self.status_bar.showMessage(f"Analyzing file sizes... {progress}%")
        if progress >= 100:
            self.status_bar.showMessage(
                "Size analysis complete", STATUS_MESSAGE_TIMEOUT_MS
            )

    def _reset_backup_ui(self) -> None:
        """Reset UI state after backup cancellation."""
        self.progress_bar.setVisible(False)
        self.backup_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)

    def _on_browse_mirror_dir(self) -> None:
        """Handle browse mirror directory button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Mirror Backup Directory", str(Path.home())
        )

        if directory:
            self.config_mirror_path_edit.setText(directory)

    def _on_browse_archive_dir(self) -> None:
        """Handle browse archive directory button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Archive Backup Directory", str(Path.home())
        )

        if directory:
            self.config_archive_path_edit.setText(directory)

    def _on_config_changed(self) -> None:
        """Handle configuration option changes to enable save button."""
        self.save_config_btn.setEnabled(True)

    def _on_rotate_checkbox_changed(self, state: int) -> None:
        """Handle rotate archives checkbox state change."""
        self.config_max_archives_spinbox.setEnabled(bool(state))

    def _on_pre_restore_checkbox_changed(self, state: int) -> None:
        """Handle pre-restore backup checkbox state change."""
        self.config_max_restore_spinbox.setEnabled(bool(state))

    def _on_size_check_checkbox_changed(self, state: int) -> None:
        """Handle size check enabled checkbox state change."""
        enabled = bool(state)
        self.config_size_warning_spinbox.setEnabled(enabled)
        self.config_size_alert_spinbox.setEnabled(enabled)
        self.config_size_critical_spinbox.setEnabled(enabled)

    def _on_browse_restore_backup_dir(self) -> None:
        """Handle browse restore backup directory button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Pre-Restore Backup Directory", str(Path.home())
        )

        if directory:
            self.config_restore_path_edit.setText(directory)

    def _on_save_config(self) -> None:
        """Handle save configuration button click."""
        reply = QMessageBox.question(
            self,
            "Confirm Save",
            "Save configuration changes to file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Update model with all configuration values
            self.viewmodel.command_update_option(
                "mirror", self.config_mirror_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "archive", self.config_archive_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "hostname_subdir", self.config_hostname_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "date_subdir", self.config_date_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "archive_compression_level", self.config_compression_spinbox.value()
            )
            self.viewmodel.command_update_option(
                "rotate_archives", self.config_rotate_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "max_archives", self.config_max_archives_spinbox.value()
            )
            self.viewmodel.command_update_option(
                "pre_restore_backup", self.config_pre_restore_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "max_restore_backups", self.config_max_restore_spinbox.value()
            )
            self.viewmodel.command_update_option(
                "verify_after_backup", self.config_verify_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "hash_verification", self.config_hash_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "size_check_enabled", self.config_size_check_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "size_warning_threshold_mb", self.config_size_warning_spinbox.value()
            )
            self.viewmodel.command_update_option(
                "size_alert_threshold_mb", self.config_size_alert_spinbox.value()
            )
            self.viewmodel.command_update_option(
                "size_critical_threshold_mb", self.config_size_critical_spinbox.value()
            )

            self.viewmodel.command_update_path(
                "mirror_dir", self.config_mirror_path_edit.text()
            )
            self.viewmodel.command_update_path(
                "archive_dir", self.config_archive_path_edit.text()
            )
            self.viewmodel.command_update_path(
                "restore_backup_dir", self.config_restore_path_edit.text()
            )

            if self.viewmodel.command_save_config():
                self.status_bar.showMessage(
                    "✓ Configuration saved", STATUS_MESSAGE_TIMEOUT_MS
                )

                self.mirror_checkbox.setChecked(self.config_mirror_checkbox.isChecked())
                self.archive_checkbox.setChecked(
                    self.config_archive_checkbox.isChecked()
                )
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    "Failed to save configuration. Check file permissions.",
                )

    def _on_save_dotfile_config(self) -> None:
        """Handle save dotfile configuration button click from Backup tab."""
        reply = QMessageBox.question(
            self,
            "Confirm Save",
            "Save dotfile configuration changes (enable/disable settings) to file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.viewmodel.command_save_config():
                self.status_bar.showMessage(
                    "✓ Dotfile configuration saved", STATUS_MESSAGE_TIMEOUT_MS
                )
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    "Failed to save configuration. Check file permissions.",
                )

    def _on_edit_config(self) -> None:
        """Open dotfiles.yaml in the user's default text editor."""
        import subprocess

        config_dir = self.viewmodel.get_config_dir()
        dotfiles_path = config_dir / "dotfiles.yaml"

        if not dotfiles_path.exists():
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Configuration file not found:\n{dotfiles_path}",
            )
            return

        try:
            subprocess.Popen(["xdg-open", str(dotfiles_path)])
            self.status_bar.showMessage(
                "Opened dotfiles.yaml in external editor",
                STATUS_MESSAGE_TIMEOUT_MS,
            )
        except FileNotFoundError:
            QMessageBox.warning(
                self,
                "Editor Not Found",
                "Could not open file: xdg-open not found.\n"
                "Please open manually:\n" + str(dotfiles_path),
            )
        except OSError as e:
            QMessageBox.warning(
                self,
                "Cannot Open File",
                f"Failed to open external editor: {e}\n"
                f"Please open manually:\n{dotfiles_path}",
            )

    def _on_validate_config(self) -> None:
        """Validate YAML configuration files and show results."""
        success, message = self.viewmodel.command_validate_config()

        if success:
            reply = QMessageBox.information(
                self,
                "Validation Passed",
                f"{message}\n\nReload configuration from disk?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.viewmodel.command_load_config()
        else:
            QMessageBox.warning(self, "Validation Failed", message)

    def _on_export_config(self) -> None:
        """Export configuration files to a user-chosen directory."""
        dest_dir = QFileDialog.getExistingDirectory(
            self, "Select Export Destination", str(Path.home())
        )

        if not dest_dir:
            return

        success, message = self.viewmodel.command_export_config(Path(dest_dir))

        if success:
            self.status_bar.showMessage(message, STATUS_MESSAGE_TIMEOUT_MS)
        else:
            QMessageBox.warning(self, "Export Failed", message)

    def _on_import_config(self) -> None:
        """Import configuration files from a user-chosen directory."""
        source_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory Containing Configuration Files",
            str(Path.home()),
        )

        if not source_dir:
            return

        reply = QMessageBox.question(
            self,
            "Import Configuration",
            "This will replace your current configuration files with the "
            "imported ones.\n\nA backup of your current configuration will be "
            "created automatically.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        success, message = self.viewmodel.command_import_config(Path(source_dir))

        if success:
            self.status_bar.showMessage(message, STATUS_MESSAGE_TIMEOUT_MS)
            self._append_log(f"✓ Config imported: {message}")
            self.viewmodel.command_load_config()
        else:
            QMessageBox.warning(self, "Import Failed", message)

    def _get_original_dotfile_index(self, table_row: int) -> int:
        """
        Get the original dotfile index from a table row.

        Args:
            table_row: Row index in the table (after sorting)

        Returns:
            Original index in the dotfiles list

        Raises:
            ValueError: If unable to determine original index (data corruption)
        """
        item = self.dotfile_table.item(table_row, 0)
        if item:
            original_idx = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(original_idx, int):
                return original_idx

        # DANGER: Only possible if table was populated without storing UserRole index
        raise ValueError(
            f"Unable to determine original dotfile index for table row {table_row}. "
            "Table data may be corrupt."
        )

    def _on_dotfile_selection_changed(self) -> None:
        """Handle dotfile table selection change."""
        has_selection = len(self.dotfile_table.selectedItems()) > 0
        self.update_dotfile_btn.setEnabled(has_selection)
        self.toggle_enabled_btn.setEnabled(has_selection)
        self.remove_dotfile_btn.setEnabled(has_selection)

    def _on_add_dotfile(self) -> None:
        """Handle add dotfile button click."""
        dialog = AddDotfileDialog(self)

        if dialog.exec():
            tags = dialog.tags_edit.text().strip()
            application = dialog.application_edit.text()
            description = dialog.description_edit.text()
            paths = dialog.get_paths()
            enabled = dialog.enabled_checkbox.isChecked()

            if not all([application, description]) or not paths:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please fill in Application, Description, and add at least one path.",
                )
                return

            # tags passed as category for legacy format compatibility
            success = self.viewmodel.command_add_dotfile(
                tags, application, description, paths, enabled
            )

            if success:
                self.status_bar.showMessage(
                    "✓ Dotfile added", STATUS_MESSAGE_TIMEOUT_MS
                )
            else:
                QMessageBox.critical(self, "Add Failed", "Failed to add dotfile entry.")

    def _on_update_dotfile(self) -> None:
        """Handle update dotfile button click."""
        selected_rows = self.dotfile_table.selectionModel().selectedRows()

        if not selected_rows:
            return

        table_row = selected_rows[0].row()
        original_idx = self._get_original_dotfile_index(table_row)

        dotfile = self.viewmodel.get_dotfile_list()[original_idx]

        # dict(dotfile) converts TypedDict to plain dict for dialog compatibility
        dialog = AddDotfileDialog(
            self,
            dotfile_data=dict(dotfile),
        )

        if dialog.exec():
            tags = dialog.tags_edit.text().strip()
            application = dialog.application_edit.text()
            description = dialog.description_edit.text()
            paths = dialog.get_paths()
            enabled = dialog.enabled_checkbox.isChecked()

            if not all([application, description]) or not paths:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please fill in Application, Description, and add at least one path.",
                )
                return

            # tags passed as category for legacy format compatibility
            success = self.viewmodel.command_update_dotfile(
                original_idx,
                tags,
                application,
                description,
                paths,
                enabled,
            )

            if success:
                self.status_bar.showMessage(
                    "✓ Dotfile updated", STATUS_MESSAGE_TIMEOUT_MS
                )
            else:
                QMessageBox.critical(
                    self, "Update Failed", "Failed to update dotfile entry."
                )

    def _on_remove_dotfile(self) -> None:
        """Handle remove dotfile button click."""
        selected_rows = self.dotfile_table.selectionModel().selectedRows()

        if not selected_rows:
            return

        table_row = selected_rows[0].row()
        original_idx = self._get_original_dotfile_index(table_row)

        dotfile = self.viewmodel.get_dotfile_list()[original_idx]
        paths_display = "\n".join(dotfile.get("paths", []))

        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove dotfile entry for {dotfile.get('application', 'Unknown')}?\n\n"
            f"Paths:\n{paths_display}\n\n"
            "This will not delete the actual files, only the configuration entry.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.viewmodel.command_remove_dotfile(original_idx)

            if success:
                self.status_bar.showMessage(
                    "✓ Dotfile removed", STATUS_MESSAGE_TIMEOUT_MS
                )
            else:
                QMessageBox.critical(
                    self, "Remove Failed", "Failed to remove dotfile entry."
                )

    def _on_toggle_dotfile_enabled(self) -> None:
        """Handle toggle dotfile inclusion button click.

        Toggles the exclusion status for the selected dotfile. If included,
        it becomes excluded; if excluded, it becomes included.
        """
        selected_rows = self.dotfile_table.selectionModel().selectedRows()

        if not selected_rows:
            return

        table_row = selected_rows[0].row()
        original_idx = self._get_original_dotfile_index(table_row)

        dotfile = self.viewmodel.get_dotfile_list()[original_idx]
        application = dotfile["application"]

        if not application:
            return

        # SIDE-EFFECT: emits exclusions_changed -> _on_exclusions_changed -> _update_dotfile_table_fast
        self.viewmodel.command_toggle_exclusion(application)

        # Query post-toggle state: is_now_excluded=True means it was previously included
        is_now_excluded = self.viewmodel.is_excluded(application)
        status_text = "excluded" if is_now_excluded else "included"
        self.status_bar.showMessage(
            f"Dotfile '{application}' {status_text}",
            STATUS_MESSAGE_TIMEOUT_MS,
        )

    def _on_dotfiles_updated(self, dotfile_count: int) -> None:
        """Handle dotfiles updated signal."""
        self._update_dotfile_table()

        if self._backup_stacked_widget:
            self._backup_stacked_widget.setCurrentIndex(0 if dotfile_count == 0 else 1)

        self.status_bar.showMessage(f"Configuration updated: {dotfile_count} dotfiles")

    def _on_exclusions_changed(self) -> None:
        """Handle exclusions changed signal.

        Refreshes the dotfile table to reflect updated inclusion status.
        Uses fast update since only exclusion status changed, not file existence.
        """
        self._update_dotfile_table_fast()

    def _apply_combined_filters(self) -> None:
        """Apply all active filters (text search + hide missing) to the dotfile table.

        Combines text search filtering with hide-missing status filtering.
        Both filters must pass for a row to be visible.

        Column structure:
            0: Included, 1: Status, 2: Application, 3: Tags, 4: Size, 5: Path
        """
        text = ""
        if self._filter_input:
            text = self._filter_input.text().lower().strip()

        hide_missing = False
        if self._hide_missing_checkbox:
            hide_missing = self._hide_missing_checkbox.isChecked()

        for row in range(self.dotfile_table.rowCount()):
            text_matches = True
            if text:
                app_item = self.dotfile_table.item(row, 2)
                tags_item = self.dotfile_table.item(row, 3)
                path_item = self.dotfile_table.item(row, 5)
                app_text = app_item.text().lower() if app_item else ""
                tags_text = tags_item.text().lower() if tags_item else ""
                path_text = path_item.text().lower() if path_item else ""
                text_matches = (
                    text in app_text or text in tags_text or text in path_text
                )

            status_matches = True
            if hide_missing:
                status_item = self.dotfile_table.item(row, 1)
                if status_item and status_item.text() == "\u2717":
                    status_matches = False

            self.dotfile_table.setRowHidden(row, not (text_matches and status_matches))

    def _append_log(self, message: str, level: str = "info") -> None:
        """Append a color-coded log entry to the operation log.

        Args:
            message: The log message text
            level: Log level for color coding (success, error, warning, skip, info, header)
        """
        from html import escape

        color_map = {
            "success": DFBUColors.SUCCESS,
            "error": DFBUColors.CRITICAL,
            "warning": DFBUColors.WARNING,
            "skip": DFBUColors.TEXT_DISABLED,
            "info": DFBUColors.TEXT_SECONDARY,
            "header": DFBUColors.PRIMARY,
        }
        color = color_map.get(level, DFBUColors.TEXT_PRIMARY)
        escaped = escape(message.rstrip("\n"))
        html = f'<span style="color: {color};">{escaped}</span><br>'
        self.operation_log.moveCursor(QTextCursor.MoveOperation.End)
        self.operation_log.insertHtml(html)
        self.operation_log.ensureCursorVisible()
        self._log_entries.append((message, level))

    def _on_log_filter_all(self) -> None:
        """Handle All filter button toggle."""
        checked = self._log_filter_all_btn.isChecked()
        self._log_filter_info_btn.setChecked(checked)
        self._log_filter_warning_btn.setChecked(checked)
        self._log_filter_error_btn.setChecked(checked)
        self._rebuild_log_display()

    def _on_log_filter_changed(self) -> None:
        """Handle individual filter button toggle."""
        all_checked = (
            self._log_filter_info_btn.isChecked()
            and self._log_filter_warning_btn.isChecked()
            and self._log_filter_error_btn.isChecked()
        )
        self._log_filter_all_btn.setChecked(all_checked)
        self._rebuild_log_display()

    def _on_clear_log(self) -> None:
        """Clear the log display and entries list."""
        self.operation_log.clear()
        self._log_entries.clear()

    def _rebuild_log_display(self) -> None:
        """Rebuild the log display based on current filter state."""
        from html import escape

        show_info = self._log_filter_info_btn.isChecked()
        show_warning = self._log_filter_warning_btn.isChecked()
        show_error = self._log_filter_error_btn.isChecked()

        level_visible: dict[str, bool] = {
            "info": show_info,
            "success": show_info,
            "header": show_info,
            "skip": show_info,
            "warning": show_warning,
            "error": show_error,
        }

        color_map = {
            "success": DFBUColors.SUCCESS,
            "error": DFBUColors.CRITICAL,
            "warning": DFBUColors.WARNING,
            "skip": DFBUColors.TEXT_DISABLED,
            "info": DFBUColors.TEXT_SECONDARY,
            "header": DFBUColors.PRIMARY,
        }

        self.operation_log.clear()
        for message, level in self._log_entries:
            if level_visible.get(level, True):
                color = color_map.get(level, DFBUColors.TEXT_PRIMARY)
                escaped = escape(message.rstrip("\n"))
                html = f'<span style="color: {color};">{escaped}</span><br>'
                self.operation_log.moveCursor(QTextCursor.MoveOperation.End)
                self.operation_log.insertHtml(html)

        self.operation_log.ensureCursorVisible()

    def _on_verify_backup(self) -> None:
        """Handle verify backup button/menu action click."""
        report = self.viewmodel.command_verify_backup()

        if report is None:
            QMessageBox.information(
                self,
                "No Backup to Verify",
                "No backup has been performed yet in this session.\n\n"
                "Run a backup operation first, then verify.",
            )
            return

        self._append_log(report, "info")
        self.operation_log.verticalScrollBar().setValue(
            self.operation_log.verticalScrollBar().maximum()
        )

        self.status_bar.showMessage(
            "Verification complete - see log for details",
            STATUS_MESSAGE_TIMEOUT_MS,
        )

    def _on_save_log(self) -> None:
        """Handle save log button click."""
        log_content = self.operation_log.toPlainText()

        if not log_content.strip():
            QMessageBox.information(
                self,
                "Empty Log",
                "The log is currently empty. There is nothing to save.",
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log File",
            str(Path.home() / "dfbu_log.txt"),
            "Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                Path(file_path).write_text(log_content, encoding="utf-8")
                self.status_bar.showMessage(
                    f"Log saved to {Path(file_path).name}",
                    STATUS_MESSAGE_TIMEOUT_MS,
                )
            except (OSError, PermissionError) as e:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    f"Failed to save log file:\n{e}",
                )

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event."""
        self.viewmodel.save_settings(
            geometry=self.saveGeometry(), window_state=self.saveState()
        )
        event.accept()
