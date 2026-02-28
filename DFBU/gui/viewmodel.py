"""
DFBU ViewModel - Presentation Logic Layer

Description:
    ViewModel layer for DFBU GUI implementing MVVM pattern. Mediates between
    Model and View, managing worker threads, signals/slots, and exposing properties
    and commands. Handles presentation logic while keeping View and Model separated.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 02-01-2026
License: MIT

Features:
    - MVVM ViewModel layer separating presentation logic from View and Model
    - Signal-based communication with View for reactive updates
    - Worker thread management for non-blocking backup/restore operations
    - Command pattern for user actions (backup, restore, config load, etc.)
    - Property exposure for data binding and state queries
    - Settings persistence and restoration for UI state
    - Interactive dotfile management with add, update, and remove commands
    - Python standard library first approach with minimal dependencies
    - Clean architecture with confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - PySide6 framework for Qt signals and threading
    - model module for business logic

Classes:
    - BackupWorker: Worker thread for backup operations
    - RestoreWorker: Worker thread for restore operations
    - DFBUViewModel: ViewModel mediating between Model and View

Functions:
    None
"""

import shutil
import time
from pathlib import Path
from typing import Any, Final

from core.common_types import (
    LegacyDotFileDict,
    OperationResultDict,
    OptionsDict,
    SizeReportDict,
)
from core.yaml_config import YAMLConfigLoader
from PySide6.QtCore import QObject, QSettings, QThread, Signal
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from gui.config_manager import create_rotating_backup
from gui.config_workers import ConfigLoadWorker, ConfigSaveWorker
from gui.input_validation import InputValidator
from gui.model import DFBUModel


class BackupWorker(QThread):
    """
    Worker thread for backup operations to prevent UI blocking.

    Attributes:
        progress_updated: Signal emitted when progress percentage changes
        item_processed: Signal emitted when an item completes processing
        item_skipped: Signal emitted when an item is skipped
        backup_finished: Signal emitted when backup completes
        error_occurred: Signal emitted when an error occurs
        model: Reference to DFBUModel for data access
        mirror_mode: Whether to perform mirror backup
        archive_mode: Whether to create archive
        force_full_backup: Whether to disable skip_identical optimization

    Public methods:
        run: Main thread execution method
        set_model: Set the model reference
        set_modes: Set backup operation modes
        set_force_full_backup: Set force full backup mode

    Private methods:
        _process_mirror_backup: Process mirror backup for all dotfiles
        _process_archive_backup: Create compressed archive
        _process_file: Process individual file backup
        _process_directory: Process directory backup recursively
    """

    progress_updated = Signal(int)  # progress percentage
    item_processed = Signal(str, str)  # source_path, dest_path
    item_skipped = Signal(str, str)  # path, reason
    backup_finished = Signal()
    backup_finished_with_result = Signal(object)  # OperationResultDict
    error_occurred = Signal(str, str)  # context, error_message

    def __init__(self) -> None:
        """Initialize the BackupWorker."""
        super().__init__()
        self.model: DFBUModel | None = None
        self.mirror_mode: bool = True
        self.archive_mode: bool = False
        self.force_full_backup: bool = False
        self.operation_result: OperationResultDict | None = None

    def set_model(self, model: DFBUModel) -> None:
        """
        Set the model reference.

        Args:
            model: DFBUModel instance
        """
        self.model = model

    def set_modes(self, mirror: bool, archive: bool) -> None:
        """
        Set backup operation modes.

        Args:
            mirror: Whether to perform mirror backup
            archive: Whether to create archive
        """
        self.mirror_mode = mirror
        self.archive_mode = archive

    def set_force_full_backup(self, force_full: bool) -> None:
        """
        Set force full backup mode.

        Args:
            force_full: If True, disable skip_identical optimization
        """
        self.force_full_backup = force_full

    def _process_file(
        self, src_path: Path, dest_path: Path, skip_identical: bool = False
    ) -> bool:
        """
        Process individual file backup with comprehensive error handling.

        Args:
            src_path: Source file path
            dest_path: Destination file path
            skip_identical: Whether to skip copying if files are identical

        Returns:
            True if successful, False otherwise
        """
        # Model must be set before running
        if not self.model:
            self.error_occurred.emit(
                str(src_path), "Internal error: Model not initialized"
            )
            return False

        error_handler = self.model.get_error_handler()
        start_time = time.perf_counter()

        try:
            if not src_path.exists():
                self.item_skipped.emit(str(src_path), "File not found")
                self.model.record_item_skipped()
                if self.operation_result:
                    result = error_handler.create_path_result(
                        str(src_path),
                        str(dest_path),
                        "skipped",
                        error_type="not_found",
                        error_message="File not found",
                    )
                    self.operation_result["skipped"].append(result)
                return False

            if not self.model.check_readable(src_path):
                self.item_skipped.emit(
                    str(src_path), "Permission denied (no read access)"
                )
                self.model.record_item_skipped()
                if self.operation_result:
                    result = error_handler.create_path_result(
                        str(src_path),
                        str(dest_path),
                        "skipped",
                        error_type="permission",
                        error_message="Permission denied (no read access)",
                        can_retry=True,
                    )
                    self.operation_result["skipped"].append(result)
                return False

            # Check if file is identical before copying (optimization for mirror mode)
            if skip_identical and self.model.files_are_identical(src_path, dest_path):
                self.item_skipped.emit(str(src_path), "File unchanged")
                self.model.record_item_skipped()
                # Track skipped files for verification (they should still verify OK)
                self.model.register_backed_up_file(src_path, dest_path)
                # unchanged files are "completed" in operation result, not "skipped"
                if self.operation_result:
                    result = error_handler.create_path_result(
                        str(src_path), str(dest_path), "success"
                    )
                    self.operation_result["completed"].append(result)
                return True

            success: bool = self.model.copy_file(
                src_path, dest_path, create_parent=True, skip_identical=skip_identical
            )

            if success:
                elapsed = time.perf_counter() - start_time
                self.model.record_item_processed(elapsed)
                self.item_processed.emit(str(src_path), str(dest_path))
                # Track successfully backed up file for verification
                self.model.register_backed_up_file(src_path, dest_path)
                if self.operation_result:
                    result = error_handler.create_path_result(
                        str(src_path), str(dest_path), "success"
                    )
                    self.operation_result["completed"].append(result)
            else:
                self.model.record_item_failed()
                self.error_occurred.emit(
                    str(src_path), "Failed to copy file (unknown error)"
                )
                if self.operation_result:
                    result = error_handler.create_path_result(
                        str(src_path),
                        str(dest_path),
                        "failed",
                        error_type="unknown",
                        error_message="Failed to copy file (unknown error)",
                    )
                    self.operation_result["failed"].append(result)

            return success

        except PermissionError as e:
            self.item_skipped.emit(str(src_path), f"Permission denied: {e}")
            self.model.record_item_skipped()
            if self.operation_result:
                result = error_handler.handle_exception(
                    e, str(src_path), str(dest_path)
                )
                self.operation_result["failed"].append(result)
            return False
        except FileNotFoundError as e:
            self.item_skipped.emit(str(src_path), f"File not found: {e}")
            self.model.record_item_skipped()
            if self.operation_result:
                result = error_handler.handle_exception(
                    e, str(src_path), str(dest_path)
                )
                self.operation_result["failed"].append(result)
            return False
        except OSError as e:
            # Disk full, read-only filesystem, etc.
            self.error_occurred.emit(str(src_path), f"Filesystem error: {e}")
            self.model.record_item_failed()
            if self.operation_result:
                result = error_handler.handle_exception(
                    e, str(src_path), str(dest_path)
                )
                self.operation_result["failed"].append(result)
            return False
        except Exception as e:
            self.error_occurred.emit(
                str(src_path), f"Unexpected error: {type(e).__name__}: {e}"
            )
            self.model.record_item_failed()
            if self.operation_result:
                result = error_handler.handle_exception(
                    e, str(src_path), str(dest_path)
                )
                self.operation_result["failed"].append(result)
            return False

    def _process_directory(
        self, src_path: Path, dest_path: Path, skip_identical: bool = False
    ) -> int:
        """
        Process directory backup recursively with comprehensive error handling.

        Args:
            src_path: Source directory path
            dest_path: Destination directory path
            skip_identical: Whether to skip copying if files are identical

        Returns:
            Number of successfully copied files
        """
        # Model must be set before running
        if not self.model:
            self.error_occurred.emit(
                str(src_path), "Internal error: Model not initialized"
            )
            return 0

        error_handler = self.model.get_error_handler()

        try:
            if not src_path.exists():
                self.item_skipped.emit(str(src_path), "Directory not found")
                self.model.record_item_skipped()
                if self.operation_result:
                    result = error_handler.create_path_result(
                        str(src_path),
                        str(dest_path),
                        "skipped",
                        error_type="not_found",
                        error_message="Directory not found",
                    )
                    self.operation_result["skipped"].append(result)
                return 0

            if not src_path.is_dir():
                self.item_skipped.emit(str(src_path), "Not a directory")
                self.model.record_item_skipped()
                if self.operation_result:
                    result = error_handler.create_path_result(
                        str(src_path),
                        str(dest_path),
                        "skipped",
                        error_type="invalid_path",
                        error_message="Not a directory",
                    )
                    self.operation_result["skipped"].append(result)
                return 0

            if not self.model.check_readable(src_path):
                self.item_skipped.emit(
                    str(src_path), "Permission denied (no read access)"
                )
                self.model.record_item_skipped()
                if self.operation_result:
                    result = error_handler.create_path_result(
                        str(src_path),
                        str(dest_path),
                        "skipped",
                        error_type="permission",
                        error_message="Permission denied (no read access)",
                        can_retry=True,
                    )
                    self.operation_result["skipped"].append(result)
                return 0

            results = self.model.copy_directory(
                src_path, dest_path, skip_identical=skip_identical
            )

            success_count = 0
            skipped_count = 0
            for src_file, dest_file, success, skipped in results:
                dest_str = str(dest_file) if dest_file else None
                if success:
                    if skipped:
                        skipped_count += 1
                        self.item_skipped.emit(str(src_file), "File unchanged")
                        # Track skipped files for verification
                        if dest_file is not None:
                            self.model.register_backed_up_file(src_file, dest_file)
                        # unchanged files are "completed" in operation result, not "skipped"
                        if self.operation_result:
                            result = error_handler.create_path_result(
                                str(src_file), dest_str, "success"
                            )
                            self.operation_result["completed"].append(result)
                    else:
                        success_count += 1
                        self.item_processed.emit(str(src_file), str(dest_file))
                        # Track successfully backed up files for verification
                        if dest_file is not None:
                            self.model.register_backed_up_file(src_file, dest_file)
                        if self.operation_result:
                            result = error_handler.create_path_result(
                                str(src_file), dest_str, "success"
                            )
                            self.operation_result["completed"].append(result)
                elif dest_file is None:
                    self.item_skipped.emit(
                        str(src_file), "Permission denied or read error"
                    )
                    if self.operation_result:
                        result = error_handler.create_path_result(
                            str(src_file),
                            dest_str,
                            "skipped",
                            error_type="permission",
                            error_message="Permission denied or read error",
                            can_retry=True,
                        )
                        self.operation_result["skipped"].append(result)
                else:
                    self.error_occurred.emit(str(src_file), "Failed to copy file")
                    if self.operation_result:
                        result = error_handler.create_path_result(
                            str(src_file),
                            dest_str,
                            "failed",
                            error_type="unknown",
                            error_message="Failed to copy file",
                        )
                        self.operation_result["failed"].append(result)

            return success_count

        except PermissionError as e:
            self.item_skipped.emit(str(src_path), f"Permission denied: {e}")
            self.model.record_item_skipped()
            if self.operation_result:
                result = error_handler.handle_exception(
                    e, str(src_path), str(dest_path)
                )
                self.operation_result["failed"].append(result)
            return 0
        except FileNotFoundError as e:
            self.item_skipped.emit(str(src_path), f"Directory not found: {e}")
            self.model.record_item_skipped()
            if self.operation_result:
                result = error_handler.handle_exception(
                    e, str(src_path), str(dest_path)
                )
                self.operation_result["failed"].append(result)
            return 0
        except OSError as e:
            # Disk full, read-only filesystem, etc.
            self.error_occurred.emit(str(src_path), f"Filesystem error: {e}")
            self.model.record_item_failed()
            if self.operation_result:
                result = error_handler.handle_exception(
                    e, str(src_path), str(dest_path)
                )
                self.operation_result["failed"].append(result)
            return 0
        except Exception as e:
            self.error_occurred.emit(
                str(src_path), f"Unexpected error: {type(e).__name__}: {e}"
            )
            self.model.record_item_failed()
            if self.operation_result:
                result = error_handler.handle_exception(
                    e, str(src_path), str(dest_path)
                )
                self.operation_result["failed"].append(result)
            return 0

    def _process_mirror_backup(self) -> None:
        """Process mirror backup for all configured dotfiles."""
        # Model must be set before running (architectural guarantee)
        if not self.model:
            return

        # Returns dict mapping index -> (exists, is_dir, type_str) tuple
        validation_results = self.model.validate_dotfile_paths()

        total_items = len([v for v in validation_results.values() if v[0]])

        if total_items == 0:
            self.error_occurred.emit("Mirror Backup", "No items found to backup")
            return

        processed_count = 0

        for i in range(self.model.get_dotfile_count()):
            dotfile = self.model.get_dotfile_by_index(i)
            if not dotfile:
                continue

            if not dotfile.get("enabled", True):
                continue

            # Note: GUI supports multiple paths per dotfile entry (unlike CLI)
            for path_str in dotfile["paths"]:
                # Skip empty path strings (validation should prevent this, but be safe)
                if not path_str:
                    continue

                src_path = self.model.expand_path(path_str)

                # Non-existent paths are skipped silently (already reported in validation)
                if not src_path.exists():
                    continue

                is_dir = src_path.is_dir()

                dest_path = self.model.assemble_dest_path(
                    self.model.mirror_base_dir,
                    src_path,
                    self.model.options["hostname_subdir"],
                    self.model.options["date_subdir"],
                )

                # Process based on type with skip_identical optimization
                # skip_identical can be disabled by force_full_backup setting
                # When force_full_backup=True, all files are copied regardless of changes
                skip_identical = not self.force_full_backup

                if is_dir:
                    file_count = self._process_directory(
                        src_path, dest_path, skip_identical=skip_identical
                    )
                    # Only increment processed_count if at least one file was copied
                    if file_count > 0:
                        processed_count += 1
                elif self._process_file(
                    src_path, dest_path, skip_identical=skip_identical
                ):
                    processed_count += 1

                if total_items > 0:
                    progress = int((processed_count / total_items) * 100)
                    self.progress_updated.emit(progress)

    def _process_archive_backup(self) -> None:
        """Create compressed archive of configured dotfiles."""
        # Model must be set before running (architectural guarantee)
        if not self.model:
            return

        # Tuple format: (path, exists, is_dir) for model.create_archive()
        items_to_archive: list[tuple[Path, bool, bool]] = []

        for i in range(self.model.get_dotfile_count()):
            dotfile = self.model.get_dotfile_by_index(i)
            if not dotfile:
                continue

            if not dotfile.get("enabled", True):
                continue

            # Note: Archives can contain multiple paths per dotfile entry
            for path_str in dotfile["paths"]:
                if not path_str:
                    continue

                src_path = self.model.expand_path(path_str)

                # Non-existent paths are silently skipped from archive
                if src_path.exists():
                    is_dir = src_path.is_dir()
                    items_to_archive.append((src_path, True, is_dir))

        if not items_to_archive:
            self.error_occurred.emit("Archive Backup", "No items found to archive")
            return

        # Returns Path to created archive or None on failure
        archive_path = self.model.create_archive(items_to_archive)

        if archive_path:
            self.item_processed.emit("Archive created", str(archive_path))

            # Rotate (delete) old archives if rotation is enabled
            # Maintains max_archives limit by deleting oldest archives first
            if self.model.options["rotate_archives"]:
                deleted = self.model.rotate_archives()
                for deleted_path in deleted:
                    self.item_processed.emit("Archive deleted", str(deleted_path))
        else:
            self.error_occurred.emit("Archive Backup", "Failed to create archive")

    def run(self) -> None:
        """Main thread execution method for backup operations."""
        # Model must be set before running (architectural guarantee)
        if not self.model:
            return

        start_time = time.perf_counter()

        self.model.reset_statistics()
        self.model.clear_backup_tracking()

        error_handler = self.model.get_error_handler()
        operation_type = "mirror_backup" if self.mirror_mode else "archive_backup"
        self.operation_result = error_handler.create_operation_result(operation_type)

        # mirror_backup = uncompressed file copies maintaining directory structure
        if self.mirror_mode:
            self._process_mirror_backup()

        # archive_backup = compressed TAR.GZ with timestamped filename
        if self.archive_mode:
            self._process_archive_backup()

        end_time = time.perf_counter()
        self.model.statistics.total_time = end_time - start_time

        if self.operation_result:
            self.operation_result = error_handler.finalize_result(self.operation_result)
            self.backup_finished_with_result.emit(self.operation_result)

        # ViewModel disconnects signals and displays statistics summary on this signal
        self.backup_finished.emit()


class RestoreWorker(QThread):
    """
    Worker thread for restore operations to prevent UI blocking.

    Attributes:
        progress_updated: Signal emitted when progress percentage changes
        item_processed: Signal emitted when an item completes processing
        restore_finished: Signal emitted when restore completes
        error_occurred: Signal emitted when an error occurs
        model: Reference to DFBUModel for data access
        source_directory: Source directory containing backups

    Public methods:
        run: Main thread execution method
        set_model: Set the model reference
        set_source_directory: Set source directory for restore
    """

    progress_updated = Signal(int)  # progress percentage
    item_processed = Signal(str, str)  # source_path, dest_path
    restore_finished = Signal()
    restore_finished_with_result = Signal(object)  # OperationResultDict
    error_occurred = Signal(str, str)  # context, error_message

    def __init__(self) -> None:
        """Initialize the RestoreWorker."""
        super().__init__()
        self.model: DFBUModel | None = None
        self.source_directory: Path | None = None
        self.operation_result: OperationResultDict | None = None

    def set_model(self, model: DFBUModel) -> None:
        """
        Set the model reference.

        Args:
            model: DFBUModel instance
        """
        self.model = model

    def set_source_directory(self, directory: Path) -> None:
        """
        Set source directory for restore.

        Args:
            directory: Source directory containing backups
        """
        self.source_directory = directory

    def run(self) -> None:
        """Main thread execution method for restore operations."""
        # Model and source directory must be set before running (architectural guarantee)
        if not self.model or not self.source_directory:
            return

        start_time = time.perf_counter()

        self.model.reset_statistics()

        error_handler = self.model.get_error_handler()
        self.operation_result = error_handler.create_operation_result("restore")

        restored_files: list[tuple[str, str]] = []

        def track_item(src: str, dest: str) -> None:
            """Callback to track restored items."""
            self.item_processed.emit(src, dest)
            restored_files.append((src, dest))

        # execute_restore includes pre-restore backup if enabled in config
        processed, total = self.model.execute_restore(
            src_dir=self.source_directory,
            progress_callback=lambda pct: self.progress_updated.emit(pct),
            item_processed_callback=track_item,
        )

        if self.operation_result:
            for src, dest in restored_files:
                result = error_handler.create_path_result(src, dest, "success")
                self.operation_result["completed"].append(result)

            # total - processed = failed/skipped count
            failed_count = total - processed
            if failed_count > 0 and total > 0:
                self.operation_result["warnings"].append(
                    f"{failed_count} files could not be restored"
                )

        if total == 0:
            self.error_occurred.emit("Restore", "No files found in source directory")
            if self.operation_result:
                self.operation_result["warnings"].append(
                    "No files found in source directory"
                )
            if self.operation_result:
                self.operation_result = error_handler.finalize_result(
                    self.operation_result
                )
                self.restore_finished_with_result.emit(self.operation_result)
            return

        if processed == 0 and total > 0:
            self.error_occurred.emit("Restore", "Restore operation failed")
            if self.operation_result:
                result = error_handler.create_path_result(
                    str(self.source_directory),
                    None,
                    "failed",
                    error_type="unknown",
                    error_message="Restore operation failed",
                )
                self.operation_result["failed"].append(result)
            if self.operation_result:
                self.operation_result = error_handler.finalize_result(
                    self.operation_result
                )
                self.restore_finished_with_result.emit(self.operation_result)
            return

        end_time = time.perf_counter()
        self.model.statistics.total_time = end_time - start_time

        if self.operation_result:
            self.operation_result = error_handler.finalize_result(self.operation_result)
            self.restore_finished_with_result.emit(self.operation_result)

        self.restore_finished.emit()


class SizeScanWorker(QThread):
    """
    Worker thread for pre-backup size analysis to prevent UI blocking.

    Analyzes dotfile sizes in background to warn about large files
    before backup operations.

    Attributes:
        progress_updated: Signal emitted when progress percentage changes
        scan_finished: Signal emitted when scan completes with SizeReportDict
        error_occurred: Signal emitted when an error occurs
        model: Reference to DFBUModel for data access

    Public methods:
        run: Main thread execution method
        set_model: Set the model reference
    """

    progress_updated = Signal(int)  # progress percentage
    scan_finished = Signal(object)  # SizeReportDict
    error_occurred = Signal(str, str)  # context, error_message

    def __init__(self) -> None:
        """Initialize the SizeScanWorker."""
        super().__init__()
        self.model: DFBUModel | None = None

    def set_model(self, model: DFBUModel) -> None:
        """
        Set the model reference.

        Args:
            model: DFBUModel instance
        """
        self.model = model

    def run(self) -> None:
        """Main thread execution method for size scanning."""
        if not self.model:
            return

        try:
            self.progress_updated.emit(0)

            report = self.model.analyze_backup_size(
                progress_callback=lambda pct: self.progress_updated.emit(pct)
            )

            self.progress_updated.emit(100)
            self.scan_finished.emit(report)

        except Exception as e:
            self.error_occurred.emit("Size Scan", str(e))


class PreviewWorker(QThread):
    """
    Worker thread for generating backup preview.

    Runs preview generation in background to prevent UI blocking.

    Attributes:
        progress_updated: Signal for progress percentage
        preview_finished: Signal emitted with BackupPreviewDict on completion
        error_occurred: Signal emitted on error
        model: Reference to DFBUModel for data access
    """

    progress_updated = Signal(int)  # progress percentage
    preview_finished = Signal(object)  # BackupPreviewDict
    error_occurred = Signal(str, str)  # context, error_message

    def __init__(self) -> None:
        """Initialize the PreviewWorker."""
        super().__init__()
        self.model: DFBUModel | None = None

    def set_model(self, model: DFBUModel) -> None:
        """
        Set the model reference.

        Args:
            model: DFBUModel instance
        """
        self.model = model

    def run(self) -> None:
        """Main thread execution method for preview generation."""
        if not self.model:
            return

        try:
            self.progress_updated.emit(0)

            preview = self.model.generate_backup_preview(
                progress_callback=lambda pct: self.progress_updated.emit(pct)
            )

            self.progress_updated.emit(100)
            self.preview_finished.emit(preview)

        except Exception as e:
            self.error_occurred.emit("Preview", str(e))


class DFBUViewModel(QObject):
    """
    ViewModel mediating between Model and View in MVVM pattern.

    Attributes:
        model: DFBUModel instance managing state
        backup_worker: Worker thread for backup operations
        restore_worker: Worker thread for restore operations
        config_load_worker: Worker thread for loading configuration
        config_save_worker: Worker thread for saving configuration
        settings: QSettings for persistence
        progress_updated: Signal for progress changes
        item_processed: Signal for individual item completion
        item_skipped: Signal for skipped items
        operation_finished: Signal for operation completion
        error_occurred: Signal for error notifications
        config_loaded: Signal when configuration loads
        dotfiles_updated: Signal when dotfile list changes

    Public methods:
        command_load_config: Load YAML configuration directory
        command_save_config: Save configuration changes to YAML files
        command_update_option: Update a configuration option
        command_update_path: Update mirror_dir or archive_dir path
        command_add_dotfile: Add a new dotfile entry to configuration
        command_update_dotfile: Update an existing dotfile entry in configuration
        command_remove_dotfile: Remove a dotfile entry from configuration
        command_start_backup: Start backup operation
        command_start_restore: Start restore operation
        command_set_restore_source: Set restore source directory
        get_dotfile_count: Get number of configured dotfiles
        get_dotfile_list: Get list of dotfile metadata
        get_dotfile_validation: Get validation status for all dotfiles
        get_statistics_summary: Get formatted statistics
        get_options: Get backup operation options
        load_settings: Load persisted settings
        save_settings: Save current settings

    Private methods:
        _on_worker_progress: Handle worker progress updates
        _on_item_processed: Handle worker item completion
        _on_item_skipped: Handle worker item skipped
        _on_backup_finished: Handle backup completion
        _on_restore_finished: Handle restore completion
        _on_worker_error: Handle worker errors
    """

    progress_updated = Signal(int)
    item_processed = Signal(str, str)
    item_skipped = Signal(str, str)
    operation_finished = Signal(str)  # statistics summary
    error_occurred = Signal(str, str)
    config_loaded = Signal(int)  # dotfile count
    dotfiles_updated = Signal(int)
    exclusions_changed = Signal()  # emitted when exclusion list changes
    recovery_dialog_requested = Signal(object)  # OperationResultDict
    size_warning_requested = Signal(object)  # SizeReportDict
    size_scan_progress = Signal(int)  # progress percentage during size scan

    # Profile signals (v1.1.0)
    profile_switched = Signal(str)  # profile_name (empty string for default)
    profiles_changed = Signal()  # emitted when profile list changes

    # Preview signals (v1.1.0)
    preview_ready = Signal(object)  # BackupPreviewDict
    preview_progress = Signal(int)  # progress percentage (0-100)

    SETTINGS_ORG: Final[str] = "L3DigitalNet"
    SETTINGS_APP: Final[str] = "dfbu_gui_settings"

    def __init__(self, model: DFBUModel) -> None:
        """
        Initialize the DFBUViewModel.

        Args:
            model: DFBUModel instance
        """
        super().__init__()
        self.model: DFBUModel = model
        self.backup_worker: BackupWorker | None = None
        self.restore_worker: RestoreWorker | None = None
        self.config_load_worker: ConfigLoadWorker | None = None
        self.config_save_worker: ConfigSaveWorker | None = None
        self.size_scan_worker: SizeScanWorker | None = None
        self._preview_worker: PreviewWorker | None = None
        self.settings: QSettings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        self.restore_source_directory: Path | None = None
        self._pending_backup_force_full: bool = False  # Track force_full for after scan

    def command_load_config(self) -> bool:
        """
        Command to load YAML configuration directory asynchronously.

        Uses ConfigLoadWorker to prevent UI blocking during file I/O.

        Returns:
            True if load operation started successfully
        """
        # Don't start new load if one is already in progress
        if self.config_load_worker is not None:
            return False

        self.config_load_worker = ConfigLoadWorker()
        self.config_load_worker.set_config_manager(self.model.get_config_manager())

        self.config_load_worker.progress_updated.connect(self._on_config_progress)
        self.config_load_worker.load_finished.connect(self._on_config_load_finished)
        self.config_load_worker.error_occurred.connect(self._on_worker_error)

        self.config_load_worker.start()
        return True

    def command_save_config(self) -> bool:
        """
        Command to save configuration changes to YAML files asynchronously.

        Uses ConfigSaveWorker to prevent UI blocking during file I/O.

        Returns:
            True if save operation started successfully
        """
        # Don't start new save if one is already in progress
        if self.config_save_worker is not None:
            return False

        self.config_save_worker = ConfigSaveWorker()
        self.config_save_worker.set_config_manager(self.model.get_config_manager())

        self.config_save_worker.progress_updated.connect(self._on_config_progress)
        self.config_save_worker.save_finished.connect(self._on_config_save_finished)
        self.config_save_worker.error_occurred.connect(self._on_worker_error)

        self.config_save_worker.start()
        return True

    def command_update_option(self, key: str, value: bool | int | str) -> bool:
        """
        Command to update a configuration option with type safety.

        Args:
            key: Option key to update
            value: New value for the option (bool, int, or str only)

        Returns:
            True if option updated successfully
        """
        valid_options: dict[str, type] = {
            "mirror": bool,
            "archive": bool,
            "hostname_subdir": bool,
            "date_subdir": bool,
            "archive_format": str,
            "archive_compression_level": int,
            "rotate_archives": bool,
            "max_archives": int,
            "pre_restore_backup": bool,
            "max_restore_backups": int,
            "verify_after_backup": bool,
            "hash_verification": bool,
        }

        if key not in valid_options:
            return False

        if not isinstance(value, valid_options[key]):
            return False

        return self.model.update_option(key, value)

    def command_update_path(self, path_type: str, value: str) -> bool:
        """
        Command to update mirror_dir, archive_dir, or restore_backup_dir path.

        Args:
            path_type: One of "mirror_dir", "archive_dir", or "restore_backup_dir"
            value: New path value

        Returns:
            True if path updated successfully
        """
        return self.model.update_path(path_type, value)

    def command_start_backup(self, force_full_backup: bool = False) -> bool:
        """
        Command to start backup operation.

        If size checking is enabled, performs size scan first and may show
        warning dialog before proceeding.

        Args:
            force_full_backup: If True, disable skip_identical optimization to copy all files

        Returns:
            True if backup/scan started successfully
        """
        if self.model.get_dotfile_count() == 0:
            self.error_occurred.emit("Backup", "No configuration loaded")
            return False

        # Stored for use after size scan completes
        self._pending_backup_force_full = force_full_backup

        if self.model.is_size_check_enabled():
            return self._start_size_scan()
        return self._start_backup_directly(force_full_backup)

    def _start_size_scan(self) -> bool:
        """
        Start size scanning in background thread.

        Returns:
            True if scan started successfully
        """
        # Don't start new scan if one is already in progress
        if self.size_scan_worker is not None and self.size_scan_worker.isRunning():
            return False

        self.size_scan_worker = SizeScanWorker()
        self.size_scan_worker.set_model(self.model)

        self.size_scan_worker.progress_updated.connect(self._on_size_scan_progress)
        self.size_scan_worker.scan_finished.connect(self._on_size_scan_finished)
        self.size_scan_worker.error_occurred.connect(self._on_size_scan_error)

        self.size_scan_worker.start()
        return True

    def _start_backup_directly(self, force_full_backup: bool) -> bool:
        """
        Start backup operation directly without size checking.

        Args:
            force_full_backup: If True, disable skip_identical optimization

        Returns:
            True if backup started successfully
        """

        self.backup_worker = BackupWorker()
        self.backup_worker.set_model(self.model)
        self.backup_worker.set_modes(
            self.model.options["mirror"], self.model.options["archive"]
        )
        self.backup_worker.set_force_full_backup(force_full_backup)

        self.backup_worker.progress_updated.connect(self._on_worker_progress)
        self.backup_worker.item_processed.connect(self._on_item_processed)
        self.backup_worker.item_skipped.connect(self._on_item_skipped)
        self.backup_worker.backup_finished.connect(self._on_backup_finished)
        self.backup_worker.backup_finished_with_result.connect(
            self._on_backup_finished_with_result
        )
        self.backup_worker.error_occurred.connect(self._on_worker_error)

        self.backup_worker.start()
        return True

    def command_proceed_after_size_warning(self) -> bool:
        """
        Continue with backup after user acknowledges size warning.

        Called by View when user clicks "Continue Anyway" in size warning dialog.

        Returns:
            True if backup started successfully
        """
        return self._start_backup_directly(self._pending_backup_force_full)

    def _on_size_scan_progress(self, progress: int) -> None:
        """
        Handle size scan progress updates.

        Args:
            progress: Progress percentage (0-100)
        """
        self.size_scan_progress.emit(progress)

    def _on_size_scan_error(self, context: str, error_message: str) -> None:
        """
        Handle size scan worker errors with cleanup.

        Args:
            context: Error context
            error_message: Error message
        """
        if self.size_scan_worker is not None:
            self.size_scan_worker.wait()
            self.size_scan_worker.deleteLater()
            self.size_scan_worker = None

        self.error_occurred.emit(context, error_message)

    def _on_size_scan_finished(self, report: SizeReportDict) -> None:
        """
        Handle size scan completion.

        If large files detected, emit signal for View to show warning dialog.
        Otherwise, proceed directly to backup.

        Args:
            report: Size analysis report
        """
        if self.size_scan_worker is not None:
            self.size_scan_worker.wait()
            self.size_scan_worker.deleteLater()
            self.size_scan_worker = None

        if report["has_warning"] or report["has_alert"] or report["has_critical"]:
            self.size_warning_requested.emit(report)
        else:
            self._start_backup_directly(self._pending_backup_force_full)

    def command_start_restore(self) -> bool:
        """
        Command to start restore operation.

        Returns:
            True if restore started successfully
        """
        if not self.restore_source_directory:
            self.error_occurred.emit("Restore", "No source directory set")
            return False

        self.restore_worker = RestoreWorker()
        self.restore_worker.set_model(self.model)
        self.restore_worker.set_source_directory(self.restore_source_directory)

        self.restore_worker.progress_updated.connect(self._on_worker_progress)
        self.restore_worker.item_processed.connect(self._on_item_processed)
        self.restore_worker.restore_finished.connect(self._on_restore_finished)
        self.restore_worker.error_occurred.connect(self._on_worker_error)

        self.restore_worker.start()
        return True

    def command_set_restore_source(self, directory: Path) -> bool:
        """
        Command to set restore source directory.

        Args:
            directory: Source directory path

        Returns:
            True if valid directory
        """
        if directory.exists() and directory.is_dir():
            self.restore_source_directory = directory
            return True
        return False

    def command_scan_restore_source(self, path: Path) -> dict[str, Any] | None:
        """Scan a backup directory and return metadata preview.

        Walks the backup directory structure to gather information about
        what would be restored. Expects the hostname subfolder pattern.

        Args:
            path: Path to the backup source directory

        Returns:
            Dictionary with hostname, file_count, total_size, entries list,
            or None if the directory is invalid.
        """
        if not path.exists() or not path.is_dir():
            return None

        hostname = ""
        scan_root = path
        subdirs = [d for d in path.iterdir() if d.is_dir()]

        # Single subdir is likely the hostname folder
        if len(subdirs) == 1:
            hostname = subdirs[0].name
            scan_root = subdirs[0]
        elif len(subdirs) > 1:
            # Multiple subdirs: date-based or multiple hostnames — use as-is
            hostname = path.name

        entries: list[dict[str, Any]] = []
        total_size = 0
        total_files = 0

        for app_dir in sorted(scan_root.iterdir()):
            if not app_dir.is_dir():
                continue

            app_files: list[dict[str, str | int]] = []
            app_size = 0

            for file_path in app_dir.rglob("*"):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    app_files.append(
                        {
                            "name": file_path.name,
                            "path": str(file_path.relative_to(scan_root)),
                            "size": size,
                        }
                    )
                    app_size += size
                    total_files += 1

            if app_files:
                entries.append(
                    {
                        "application": app_dir.name,
                        "files": app_files,
                        "file_count": len(app_files),
                        "total_size": app_size,
                    }
                )
                total_size += app_size

        return {
            "hostname": hostname,
            "file_count": total_files,
            "total_size": total_size,
            "entries": entries,
        }

    def command_add_dotfile(
        self,
        category: str,
        application: str,
        description: str,
        paths: list[str],
        enabled: bool = True,
    ) -> bool:
        """
        Command to add a new dotfile entry.

        Args:
            category: Category for the dotfile
            application: Application name
            description: Description of the dotfile
            paths: List of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was added successfully
        """
        success: bool = self.model.add_dotfile(
            category, application, description, paths, enabled
        )

        if success:
            dotfile_count = self.model.get_dotfile_count()
            self.dotfiles_updated.emit(dotfile_count)

        return success

    def command_update_dotfile(
        self,
        index: int,
        category: str,
        application: str,
        description: str,
        paths: list[str],
        enabled: bool = True,
    ) -> bool:
        """
        Command to update an existing dotfile entry.

        Args:
            index: Index of dotfile to update
            category: Updated category
            application: Updated application name
            description: Updated description
            paths: List of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was updated successfully
        """
        success: bool = self.model.update_dotfile(
            index, category, application, description, paths, enabled
        )

        if success:
            dotfile_count = self.model.get_dotfile_count()
            self.dotfiles_updated.emit(dotfile_count)

        return success

    def command_remove_dotfile(self, index: int) -> bool:
        """
        Command to remove a dotfile entry by index.

        Args:
            index: Index of dotfile to remove

        Returns:
            True if dotfile was removed successfully
        """
        success: bool = self.model.remove_dotfile(index)

        if success:
            dotfile_count = self.model.get_dotfile_count()
            self.dotfiles_updated.emit(dotfile_count)

        return success

    def command_toggle_dotfile_enabled(self, index: int) -> bool:
        """
        Command to toggle the enabled status of a dotfile entry.

        Args:
            index: Index of dotfile to toggle

        Returns:
            New enabled status
        """
        # Note: Don't emit dotfiles_updated here - the list hasn't changed,
        # only the enabled status of one entry. The View will update locally.

        return self.model.toggle_dotfile_enabled(index)

    def command_toggle_exclusion(self, application: str) -> None:
        """Toggle exclusion status for a dotfile.

        Args:
            application: Application name to toggle
        """
        self.model.get_config_manager().toggle_exclusion(application)
        self.exclusions_changed.emit()

    def command_verify_backup(self) -> str | None:
        """
        Command to verify integrity of the last backup operation.

        Returns:
            Formatted verification report for log display, or None if no backup to verify
        """
        file_count = self.model.get_last_backup_file_count()
        if file_count == 0:
            return None
        return self.model.verify_last_backup()

    def command_validate_config(self) -> tuple[bool, str]:
        """
        Validate the dotfiles.yaml and settings.yaml configuration files.

        Returns:
            Tuple of (success, message). Message contains error details on failure.
        """
        config_dir = self.model.config_path
        errors: list[str] = []

        loader = YAMLConfigLoader(config_dir)

        dotfiles_path = config_dir / "dotfiles.yaml"
        if dotfiles_path.exists():
            try:
                loader.load_dotfiles()
            except (ValueError, KeyError, TypeError, OSError, YAMLError) as e:
                errors.append(f"dotfiles.yaml: {e}")
        else:
            errors.append("dotfiles.yaml: File not found")

        settings_path = config_dir / "settings.yaml"
        if settings_path.exists():
            try:
                loader.load_settings()
            except (ValueError, KeyError, TypeError, OSError, YAMLError) as e:
                errors.append(f"settings.yaml: {e}")
        else:
            errors.append("settings.yaml: File not found")

        if errors:
            return False, "Validation errors:\n" + "\n".join(errors)
        return True, "Configuration is valid. No errors found."

    def command_export_config(self, dest_dir: Path) -> tuple[bool, str]:
        """
        Export all configuration files to the specified directory.

        Exports dotfiles.yaml, settings.yaml, session.yaml, and .dfbuignore.

        Args:
            dest_dir: Destination directory for the exported files

        Returns:
            Tuple of (success, message)
        """
        if not dest_dir.exists():
            return False, f"Destination directory does not exist: {dest_dir}"

        if not dest_dir.is_dir():
            return False, f"Destination is not a directory: {dest_dir}"

        config_dir = self.model.config_path
        files_to_export = [
            "dotfiles.yaml",
            "settings.yaml",
            "session.yaml",
            ".dfbuignore",
        ]
        copied: list[str] = []
        errors: list[str] = []

        for filename in files_to_export:
            src = config_dir / filename
            dest = dest_dir / filename
            if src.exists():
                try:
                    shutil.copy2(src, dest)
                    copied.append(filename)
                except OSError as e:  # Includes PermissionError
                    errors.append(f"{filename}: {e}")
            # session.yaml and .dfbuignore are optional
            elif filename in ("dotfiles.yaml", "settings.yaml"):
                errors.append(f"{filename}: Source file not found")

        if errors:
            return False, f"Exported {len(copied)} file(s), errors:\n" + "\n".join(
                errors
            )
        return True, f"Exported {len(copied)} file(s) to {dest_dir}"

    def command_import_config(self, source_dir: Path) -> tuple[bool, str]:
        """
        Import configuration files from a directory.

        Validates source files, creates backups of current configs, then
        copies the imported files into the config directory and reloads.

        Imports: dotfiles.yaml, settings.yaml, and optionally session.yaml
        and .dfbuignore.

        Args:
            source_dir: Directory containing configuration files to import

        Returns:
            Tuple of (success, message)
        """
        if not source_dir.exists():
            return False, f"Source directory does not exist: {source_dir}"

        if not source_dir.is_dir():
            return False, f"Source is not a directory: {source_dir}"

        importable_files = [
            "dotfiles.yaml",
            "settings.yaml",
            "session.yaml",
            ".dfbuignore",
        ]
        available = [f for f in importable_files if (source_dir / f).exists()]

        if not available:
            return False, (
                "No configuration files found in the selected directory.\n"
                "Expected: dotfiles.yaml, settings.yaml, session.yaml, or .dfbuignore"
            )

        yaml_files = [f for f in available if f.endswith(".yaml")]
        validation_errors: list[str] = []
        for filename in yaml_files:
            try:
                temp_yaml = YAML()
                temp_yaml.preserve_quotes = True
                temp_yaml.allow_duplicate_keys = True
                with (source_dir / filename).open("r", encoding="utf-8") as fh:
                    data: Any = temp_yaml.load(fh)  # pyright: ignore[reportUnknownMemberType]
                if data is None and filename in ("dotfiles.yaml", "settings.yaml"):
                    validation_errors.append(f"{filename}: File is empty")
            except Exception as e:
                validation_errors.append(f"{filename}: {e}")

        if validation_errors:
            return False, "Validation errors in source files:\n" + "\n".join(
                validation_errors
            )

        config_dir = self.model.config_path
        backup_errors: list[str] = []
        for filename in available:
            current_file = config_dir / filename
            if current_file.exists():
                try:
                    create_rotating_backup(current_file)
                except Exception as e:
                    backup_errors.append(f"Backup of {filename} failed: {e}")

        if backup_errors:
            return False, (
                "Failed to create backups of current configs:\n"
                + "\n".join(backup_errors)
                + "\nImport aborted to protect existing configuration."
            )

        imported: list[str] = []
        copy_errors: list[str] = []
        for filename in available:
            src = source_dir / filename
            dest = config_dir / filename
            try:
                shutil.copy2(src, dest)
                imported.append(filename)
            except OSError as e:
                copy_errors.append(f"{filename}: {e}")

        if copy_errors:
            return False, (
                f"Imported {len(imported)} file(s), errors:\n" + "\n".join(copy_errors)
            )

        return True, f"Imported {len(imported)} file(s): {', '.join(imported)}"

    def get_config_dir(self) -> Path:
        """Return the path to the configuration directory."""
        return self.model.config_path

    def command_create_profile(
        self,
        name: str,
        description: str,
        excluded: list[str],
        options_overrides: dict[str, bool | int | str] | None = None,
    ) -> bool:
        """
        Command to create a new backup profile.

        Args:
            name: Unique profile name
            description: Human-readable description
            excluded: List of application names to exclude
            options_overrides: Optional settings overrides

        Returns:
            True if profile was created successfully
        """
        success = self.model.create_profile(
            name, description, excluded, options_overrides
        )
        if success:
            self.profiles_changed.emit()
        return success

    def command_delete_profile(self, name: str) -> bool:
        """
        Command to delete a profile.

        Args:
            name: Profile name to delete

        Returns:
            True if profile was deleted
        """
        success = self.model.delete_profile(name)
        if success:
            self.profiles_changed.emit()
        return success

    def command_switch_profile(self, name: str | None) -> bool:
        """
        Command to switch active profile.

        Args:
            name: Profile name to switch to, or None for default

        Returns:
            True if switch was successful
        """
        success = self.model.switch_profile(name)
        if success:
            profile_name = name if name else ""
            self.profile_switched.emit(profile_name)
            self.exclusions_changed.emit()  # SIDE-EFFECT: profile switch also changes active exclusions
        return success

    def get_profile_names(self) -> list[str]:
        """Get list of all profile names."""
        return self.model.get_profile_names()

    def get_active_profile_name(self) -> str | None:
        """Get name of currently active profile."""
        return self.model.get_active_profile_name()

    def command_generate_preview(self) -> bool:
        """
        Command to generate backup preview asynchronously.

        Uses PreviewWorker to prevent UI blocking during preview generation.

        Returns:
            True if preview generation started successfully
        """
        if self._preview_worker is not None and self._preview_worker.isRunning():
            return False

        self._preview_worker = PreviewWorker()
        self._preview_worker.set_model(self.model)
        self._preview_worker.progress_updated.connect(self._on_preview_progress)
        self._preview_worker.preview_finished.connect(self._on_preview_finished)
        self._preview_worker.error_occurred.connect(self._on_worker_error)
        self._preview_worker.start()
        return True

    def _on_preview_progress(self, progress: int) -> None:
        """Handle preview progress updates."""
        self.preview_progress.emit(progress)

    def _on_preview_finished(self, preview: Any) -> None:
        """Handle preview completion."""
        if self._preview_worker:
            self._preview_worker.wait()
            self._preview_worker.deleteLater()
            self._preview_worker = None
        self.preview_ready.emit(preview)

    def get_exclusions(self) -> list[str]:
        """Get current exclusion list.

        Returns:
            List of excluded application names
        """
        return self.model.get_config_manager().get_exclusions()

    def is_excluded(self, application: str) -> bool:
        """Check if application is excluded.

        Args:
            application: Application name

        Returns:
            True if excluded
        """
        return self.model.get_config_manager().is_excluded(application)

    def get_dotfile_count(self) -> int:
        """
        Get number of configured dotfiles.

        Returns:
            Dotfile count
        """
        return self.model.get_dotfile_count()

    def get_dotfile_list(self) -> list[LegacyDotFileDict]:
        """
        Get list of dotfile metadata.

        Returns:
            List of dotfile dictionaries
        """
        return self.model.dotfiles.copy()

    def get_dotfile_validation(self) -> dict[int, tuple[bool, bool, str]]:
        """
        Get validation status for all dotfiles.

        Returns:
            Dict mapping index to (exists, is_dir, type_str) tuple
        """
        return self.model.validate_dotfile_paths()

    def get_dotfile_sizes(self) -> dict[int, int]:
        """
        Get sizes for all dotfiles in bytes.

        Returns:
            Dict mapping index to size in bytes
        """
        return self.model.get_dotfile_sizes()

    def get_unique_categories(self) -> list[str]:
        """
        Get sorted list of unique categories from all dotfiles.

        Returns:
            Sorted list of unique category names
        """
        categories: set[str] = set()
        for dotfile in self.model.dotfiles:
            if dotfile.get("category"):
                categories.add(dotfile["category"])
        return sorted(categories)

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format size in bytes to human-readable string with appropriate units.

        Args:
            size_bytes: Size in bytes to format

        Returns:
            Formatted size string (e.g., "0 B", "1.5 KB", "2.3 MB", "5.7 GB")
        """
        if size_bytes == 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)

        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1

        if unit_index == 0:  # Bytes — no decimal needed
            return f"{int(size)} {units[unit_index]}"
        return f"{size:.1f} {units[unit_index]}"

    def get_statistics_summary(self) -> str:
        """
        Get formatted statistics summary.

        Returns:
            Formatted statistics string with enhanced clarity
        """
        stats = self.model.statistics

        message_parts = [
            "Backup Operation Completed!\n",
            "=" * 50,
        ]

        total_items = stats.processed_items + stats.skipped_items + stats.failed_items

        message_parts.append(
            f"\n📊 Summary: {stats.processed_items} copied, "
            f"{stats.skipped_items} skipped, "
            f"{stats.failed_items} failed (Total: {total_items})"
        )

        message_parts.append("\n📋 Details:")

        if stats.processed_items > 0:
            message_parts.append(
                f"  ✓ Files copied: {stats.processed_items} "
                f"(new or modified files backed up)"
            )
        else:
            message_parts.append("  ✓ Files copied: 0 (all files already up to date)")

        if stats.skipped_items > 0:
            message_parts.append(
                f"  ⊘ Files skipped: {stats.skipped_items} "
                f"(unchanged since last backup)"
            )

        if stats.failed_items > 0:
            message_parts.append(
                f"  ✗ Files failed: {stats.failed_items} (check log for details)"
            )

        message_parts.append(f"\n⏱️  Total time: {stats.total_time:.2f} seconds")

        if stats.processing_times and stats.processed_items > 0:
            message_parts.extend(
                [
                    "\n📈 Performance:",
                    f"  Average: {stats.average_time:.4f} seconds per file",
                    f"  Fastest: {stats.min_time:.4f} seconds",
                    f"  Slowest: {stats.max_time:.4f} seconds",
                ]
            )

        return "\n".join(message_parts)

    def get_options(self) -> OptionsDict:
        """
        Get backup operation options.

        Returns:
            Options dictionary with proper typing
        """
        # CONSTRAINT: copy prevents external mutation (TypedDict is backed by a plain dict)
        return dict(self.model.options)  # type: ignore[return-value]

    def set_mirror_mode(self, enabled: bool) -> None:
        """
        Set mirror backup mode.

        Args:
            enabled: Whether mirror backup is enabled
        """
        self.model.options["mirror"] = enabled

    def set_archive_mode(self, enabled: bool) -> None:
        """
        Set archive backup mode.

        Args:
            enabled: Whether archive backup is enabled
        """
        self.model.options["archive"] = enabled

    def load_settings(self) -> dict[str, Any]:
        """
        Load persisted settings from QSettings with validation.

        Returns:
            Dictionary of loaded settings (safe/validated values only)
        """
        restore_source_str: str = str(self.settings.value("restoreSource", ""))

        settings_dict: dict[str, Any] = {
            "restore_source": restore_source_str,
            "geometry": self.settings.value("geometry"),
            "window_state": self.settings.value("windowState"),
        }

        if restore_source_str:
            validation_result = InputValidator.validate_path(
                restore_source_str, must_exist=True
            )
            if validation_result.success:
                restore_path = Path(restore_source_str)
                if restore_path.exists():
                    self.restore_source_directory = restore_path
            # Invalid paths silently ignored — no error state for last-session paths

        return settings_dict

    def save_settings(self, geometry: Any = None, window_state: Any = None) -> None:
        """
        Save current settings to QSettings.

        Args:
            geometry: Window geometry to save
            window_state: Window state to save
        """
        if geometry:
            self.settings.setValue("geometry", geometry)
        if window_state:
            self.settings.setValue("windowState", window_state)

        if self.restore_source_directory:
            self.settings.setValue("restoreSource", str(self.restore_source_directory))

    def save_theme_preference(self, theme_name: str) -> None:
        """Save the user's theme preference to QSettings.

        Args:
            theme_name: Theme name to persist (e.g., "dfbu_light", "dfbu_dark")
        """
        self.settings.setValue("appearance/theme", theme_name)

    def load_theme_preference(self) -> str:
        """Load the user's theme preference from QSettings.

        Returns:
            Theme name string, defaults to "dfbu_light" if not set.
        """
        return str(self.settings.value("appearance/theme", "dfbu_light"))

    def _on_worker_progress(self, value: int) -> None:
        """
        Handle worker progress updates.

        Args:
            value: Progress percentage
        """
        self.progress_updated.emit(value)

    def _on_item_processed(self, source: str, destination: str) -> None:
        """
        Handle worker item completion.

        Args:
            source: Source path
            destination: Destination path
        """
        self.item_processed.emit(source, destination)

    def _on_item_skipped(self, path: str, reason: str) -> None:
        """
        Handle worker item skipped.

        Args:
            path: Path that was skipped
            reason: Reason for skipping
        """
        self.item_skipped.emit(path, reason)

    def _on_backup_finished(self) -> None:
        """Handle backup completion and cleanup worker."""
        stats = self.model.statistics
        success = stats.failed_items == 0
        backup_type = "mirror" if self.model.options.get("mirror", True) else "archive"
        self.model.record_backup_history(
            items_backed=stats.processed_items,
            size_bytes=0,  # TODO: Track actual size in StatisticsTracker
            duration_seconds=stats.total_time,
            success=success,
            backup_type=backup_type,
        )

        summary = self.get_statistics_summary()
        self.operation_finished.emit(summary)

        if self.backup_worker:
            self.backup_worker.progress_updated.disconnect(self._on_worker_progress)
            self.backup_worker.item_processed.disconnect(self._on_item_processed)
            self.backup_worker.item_skipped.disconnect(self._on_item_skipped)
            self.backup_worker.backup_finished.disconnect(self._on_backup_finished)
            self.backup_worker.backup_finished_with_result.disconnect(
                self._on_backup_finished_with_result
            )
            self.backup_worker.error_occurred.disconnect(self._on_worker_error)
            self.backup_worker.deleteLater()
            self.backup_worker = None

    def _on_backup_finished_with_result(self, result: OperationResultDict) -> None:
        """Handle backup completion with structured result.

        Emits recovery_dialog_requested signal if there are failures.

        Args:
            result: Structured operation result
        """
        if result["status"] != "success" and result["can_retry"]:
            self.recovery_dialog_requested.emit(result)

    def _on_restore_finished(self) -> None:
        """Handle restore completion and cleanup worker."""
        summary = self.get_statistics_summary()
        self.operation_finished.emit(summary)

        if self.restore_worker:
            self.restore_worker.progress_updated.disconnect(self._on_worker_progress)
            self.restore_worker.item_processed.disconnect(self._on_item_processed)
            self.restore_worker.restore_finished.disconnect(self._on_restore_finished)
            self.restore_worker.error_occurred.disconnect(self._on_worker_error)
            self.restore_worker.deleteLater()
            self.restore_worker = None

    def _on_worker_error(self, context: str, error_message: str) -> None:
        """
        Handle worker errors.

        Args:
            context: Error context
            error_message: Error message
        """
        self.error_occurred.emit(context, error_message)

    def _on_config_progress(self, value: int) -> None:
        """
        Handle config worker progress updates.

        Args:
            value: Progress percentage
        """
        self.progress_updated.emit(value)

    def _on_config_load_finished(
        self, success: bool, error_message: str, dotfile_count: int
    ) -> None:
        """
        Handle config load completion and cleanup worker.

        Args:
            success: Whether load was successful
            error_message: Error message if failed
            dotfile_count: Number of dotfiles loaded
        """
        if success:
            self.config_loaded.emit(dotfile_count)
            self.dotfiles_updated.emit(dotfile_count)
        else:
            self.error_occurred.emit("Configuration", error_message)

        if self.config_load_worker:
            self.config_load_worker.progress_updated.disconnect(
                self._on_config_progress
            )
            self.config_load_worker.load_finished.disconnect(
                self._on_config_load_finished
            )
            self.config_load_worker.error_occurred.disconnect(self._on_worker_error)
            self.config_load_worker.deleteLater()
            self.config_load_worker = None

    def _on_config_save_finished(self, success: bool, error_message: str) -> None:
        """
        Handle config save completion and cleanup worker.

        Args:
            success: Whether save was successful
            error_message: Error message if failed
        """
        if not success:
            self.error_occurred.emit("Configuration Save", error_message)

        if self.config_save_worker:
            self.config_save_worker.progress_updated.disconnect(
                self._on_config_progress
            )
            self.config_save_worker.save_finished.disconnect(
                self._on_config_save_finished
            )
            self.config_save_worker.error_occurred.disconnect(self._on_worker_error)
            self.config_save_worker.deleteLater()
            self.config_save_worker = None
