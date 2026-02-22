"""
DFBU Model - Facade for Application Components

Description:
    Facade pattern implementation providing unified interface to DFBU components.
    Coordinates ConfigManager, FileOperations, BackupOrchestrator, and
    StatisticsTracker. Maintains backward compatibility with existing ViewModel.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 02-01-2026
License: MIT

Features:
    - Facade pattern for clean component composition
    - Maintains public API for backward compatibility
    - Delegates operations to focused components
    - Single entry point for ViewModel layer
    - Significantly reduced code (~300 lines vs ~1179 lines)

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - Component modules: config_manager, file_operations, backup_orchestrator, statistics_tracker

Classes:
    - DFBUModel: Facade coordinating all components

Functions:
    None
"""

import sys
from collections.abc import Callable
from pathlib import Path
from socket import gethostname
from typing import Any


# SIDE-EFFECT: Mutates sys.path — must execute before any local module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import (
    BackupHistoryEntry,
    BackupPreviewDict,
    DashboardMetrics,
    DotFileDict,
    LegacyDotFileDict,
    OptionsDict,
    SizeReportDict,
)

from gui.backup_history import BackupHistoryManager
from gui.backup_orchestrator import BackupOrchestrator
from gui.config_manager import ConfigManager
from gui.error_handler import ErrorHandler
from gui.file_operations import FileOperations
from gui.preview_generator import PreviewGenerator
from gui.profile_manager import ProfileManager
from gui.restore_backup_manager import RestoreBackupManager
from gui.size_analyzer import SizeAnalyzer
from gui.statistics_tracker import BackupStatistics, StatisticsTracker
from gui.verification_manager import VerificationManager


class DFBUModel:
    """
    Facade coordinating DFBU application components.

    Provides unified interface to ConfigManager, FileOperations, BackupOrchestrator,
    and StatisticsTracker. Maintains backward compatibility with existing ViewModel
    by exposing the same public API.

    Attributes:
        config_path: Path to YAML configuration directory
        options: Backup operation options from configuration
        dotfiles: List of dotfile metadata from configuration
        statistics: Backup/restore operation statistics
        hostname: Current system hostname
        mirror_base_dir: Base directory for mirror backups
        archive_base_dir: Base directory for archive backups

    Public methods:
        load_config: Load and validate YAML configuration
        save_config: Save configuration changes back to YAML files
        add_dotfile: Add a new dotfile entry to configuration
        update_dotfile: Update an existing dotfile entry in configuration
        remove_dotfile: Remove a dotfile entry from configuration by index
        toggle_dotfile_enabled: Toggle enabled status of dotfile
        get_dotfile_by_index: Get dotfile metadata by index
        get_dotfile_count: Get number of configured dotfiles
        get_dotfile_sizes: Calculate sizes for all dotfiles
        validate_dotfile_paths: Check which dotfiles exist on system
        expand_path: Expand user home directory in path
        check_readable: Check if path has read permissions
        create_directory: Create directory with permissions
        files_are_identical: Compare files using metadata
        copy_file: Copy file with metadata preservation
        copy_directory: Copy directory recursively
        calculate_path_size: Calculate total size of file or directory
        assemble_dest_path: Build destination path for backup
        create_archive: Create compressed TAR.GZ archive
        rotate_archives: Delete oldest archives exceeding limit
        discover_restore_files: Find all files in restore source
        reconstruct_restore_paths: Build original paths from backup structure
        record_item_processed: Record successful item processing
        record_item_skipped: Record skipped item
        record_item_failed: Record failed item
        reset_statistics: Reset operation statistics
        update_option: Update a single configuration option
        update_path: Update mirror_dir or archive_dir path
        analyze_backup_size: Analyze sizes of all configured dotfiles
        is_size_check_enabled: Check if pre-backup size checking is enabled
        set_size_check_enabled: Enable or disable pre-backup size checking
        format_size_report: Format a size report for display

    Private methods:
        None (delegation only)
    """

    def __init__(self, config_path: Path) -> None:
        """
        Initialize DFBUModel facade with all components.

        Args:
            config_path: Path to YAML configuration directory
        """
        self.hostname: str = gethostname()

        self._file_ops: FileOperations = FileOperations(self.hostname)

        self._config_manager: ConfigManager = ConfigManager(
            config_path, expand_path_callback=self._file_ops.expand_path
        )

        self._stats_tracker: StatisticsTracker = StatisticsTracker()

        self._restore_backup_manager: RestoreBackupManager = RestoreBackupManager(
            backup_base_dir=self._config_manager.restore_backup_dir,
            max_backups=self._config_manager.options.get("max_restore_backups", 5),
        )

        self._verification_manager: VerificationManager = VerificationManager(
            hash_verification_enabled=self._config_manager.options.get(
                "hash_verification", False
            ),
        )

        self._backup_orchestrator: BackupOrchestrator = BackupOrchestrator(
            file_ops=self._file_ops,
            stats_tracker=self._stats_tracker,
            mirror_base_dir=self._config_manager.mirror_base_dir,
            archive_base_dir=self._config_manager.archive_base_dir,
            restore_backup_manager=self._restore_backup_manager,
            verification_manager=self._verification_manager,
        )

        # SIDE-EFFECT: Populated by BackupWorker via register_backed_up_file(); consumed by verify_last_backup() — cleared by clear_backup_tracking() before each run
        self._last_backup_files: list[tuple[Path, Path]] = []

        self._error_handler: ErrorHandler = ErrorHandler()

        self._size_analyzer: SizeAnalyzer = SizeAnalyzer(
            file_operations=self._file_ops,
            warning_threshold_mb=self._config_manager.options.get(
                "size_warning_threshold_mb", 10
            ),
            alert_threshold_mb=self._config_manager.options.get(
                "size_alert_threshold_mb", 100
            ),
            critical_threshold_mb=self._config_manager.options.get(
                "size_critical_threshold_mb", 1024
            ),
            size_check_enabled=self._config_manager.options.get(
                "size_check_enabled", True
            ),
        )

        self._profile_manager: ProfileManager = ProfileManager(config_path)

        self._history_manager: BackupHistoryManager = BackupHistoryManager(config_path)

        # CONSTRAINT: None until _init_preview_generator() call — avoids importing heavyweight generator at startup
        self._preview_generator: PreviewGenerator | None = None

    @property
    def config_path(self) -> Path:
        """Get current configuration file path."""
        return self._config_manager.config_path

    @property
    def options(self) -> OptionsDict:
        """Get current options configuration."""
        return self._config_manager.options

    @property
    def dotfiles(self) -> list[LegacyDotFileDict]:
        """Get current dotfiles list."""
        return self._config_manager.dotfiles

    @property
    def statistics(self) -> BackupStatistics:
        """Get current operation statistics."""
        return self._stats_tracker.statistics

    @property
    def mirror_base_dir(self) -> Path:
        """Get mirror backup base directory."""
        return self._config_manager.mirror_base_dir

    @mirror_base_dir.setter
    def mirror_base_dir(self, path: Path) -> None:
        """Set mirror backup base directory."""
        self._config_manager.mirror_base_dir = path
        self._backup_orchestrator.mirror_base_dir = path

    @property
    def archive_base_dir(self) -> Path:
        """Get archive backup base directory."""
        return self._config_manager.archive_base_dir

    @archive_base_dir.setter
    def archive_base_dir(self, path: Path) -> None:
        """Set archive backup base directory."""
        self._config_manager.archive_base_dir = path
        self._backup_orchestrator.archive_base_dir = path

    @property
    def restore_backup_dir(self) -> Path:
        """Get pre-restore backup directory."""
        return self._config_manager.restore_backup_dir

    @restore_backup_dir.setter
    def restore_backup_dir(self, path: Path) -> None:
        """Set pre-restore backup directory."""
        self._config_manager.restore_backup_dir = path
        self._restore_backup_manager.backup_base_dir = path

    def get_config_manager(self) -> ConfigManager:
        """
        Get the ConfigManager instance for worker threads.

        Returns:
            ConfigManager instance
        """
        return self._config_manager

    def get_error_handler(self) -> ErrorHandler:
        """
        Get the ErrorHandler instance for structured error handling.

        Returns:
            ErrorHandler instance
        """
        return self._error_handler

    def get_size_analyzer(self) -> SizeAnalyzer:
        """
        Get the SizeAnalyzer instance for pre-backup size checking.

        Returns:
            SizeAnalyzer instance
        """
        return self._size_analyzer

    def load_config(self) -> tuple[bool, str]:
        """
        Load and validate YAML configuration files.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        success, error = self._config_manager.load_config()

        if success:
            self._backup_orchestrator.mirror_base_dir = (
                self._config_manager.mirror_base_dir
            )
            self._backup_orchestrator.archive_base_dir = (
                self._config_manager.archive_base_dir
            )
            self._restore_backup_manager.backup_base_dir = (
                self._config_manager.restore_backup_dir
            )
            self._restore_backup_manager.max_backups = self._config_manager.options.get(
                "max_restore_backups", 5
            )
            self._size_analyzer.size_check_enabled = self._config_manager.options.get(
                "size_check_enabled", True
            )
            self._size_analyzer.warning_threshold_mb = self._config_manager.options.get(
                "size_warning_threshold_mb", 10
            )
            self._size_analyzer.alert_threshold_mb = self._config_manager.options.get(
                "size_alert_threshold_mb", 100
            )
            self._size_analyzer.critical_threshold_mb = (
                self._config_manager.options.get("size_critical_threshold_mb", 1024)
            )

            self._profile_manager.load_profiles()

        return success, error

    def save_config(self) -> tuple[bool, str]:
        """
        Save current configuration back to YAML files with automatic rotating backups.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        return self._config_manager.save_config()

    def add_dotfile(
        self,
        category: str,
        application: str,
        description: str,
        paths: list[str],
        enabled: bool = True,
    ) -> bool:
        """
        Add a new dotfile entry to the configuration.

        Args:
            category: Category for the dotfile
            application: Application name
            description: Description of the dotfile
            paths: List of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was added successfully
        """
        return self._config_manager.add_dotfile(
            category, application, description, paths, enabled
        )

    def update_dotfile(
        self,
        index: int,
        category: str,
        application: str,
        description: str,
        paths: list[str],
        enabled: bool = True,
    ) -> bool:
        """
        Update an existing dotfile entry in the configuration.

        Args:
            index: Index of dotfile to update
            category: Updated category
            application: Updated application name
            description: Updated description
            paths: Updated list of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was updated successfully
        """
        return self._config_manager.update_dotfile(
            index, category, application, description, paths, enabled
        )

    def remove_dotfile(self, index: int) -> bool:
        """
        Remove a dotfile entry from the configuration by index.

        Args:
            index: Index of dotfile to remove

        Returns:
            True if dotfile was removed successfully
        """
        return self._config_manager.remove_dotfile(index)

    def toggle_dotfile_enabled(self, index: int) -> bool:
        """
        Toggle the enabled status of a dotfile entry.

        Args:
            index: Index of dotfile to toggle

        Returns:
            New enabled status if successful, current status otherwise
        """
        return self._config_manager.toggle_dotfile_enabled(index)

    def update_option(self, key: str, value: bool | int | str) -> bool:
        """
        Update a single configuration option.

        Args:
            key: Option key to update
            value: New value for the option

        Returns:
            True if option was updated successfully
        """
        return self._config_manager.update_option(key, value)

    def update_path(self, path_type: str, value: str) -> bool:
        """
        Update mirror_dir, archive_dir, or restore_backup_dir path.

        Args:
            path_type: One of "mirror_dir", "archive_dir", or "restore_backup_dir"
            value: New path value

        Returns:
            True if path was updated successfully
        """
        success: bool = self._config_manager.update_path(path_type, value)

        if success:
            self._backup_orchestrator.mirror_base_dir = (
                self._config_manager.mirror_base_dir
            )
            self._backup_orchestrator.archive_base_dir = (
                self._config_manager.archive_base_dir
            )
            self._restore_backup_manager.backup_base_dir = (
                self._config_manager.restore_backup_dir
            )

        return success

    def get_dotfile_by_index(self, index: int) -> LegacyDotFileDict | None:
        """
        Get dotfile metadata by index.

        Args:
            index: Index in dotfiles list

        Returns:
            Dotfile dictionary or None if invalid index
        """
        return self._config_manager.get_dotfile_by_index(index)

    def get_dotfile_count(self) -> int:
        """
        Get number of configured dotfiles.

        Returns:
            Number of dotfiles in configuration
        """
        return self._config_manager.get_dotfile_count()

    def expand_path(self, path_str: str) -> Path:
        """
        Expand user home directory in path string.

        Args:
            path_str: Path string potentially containing ~

        Returns:
            Expanded Path object
        """
        return self._file_ops.expand_path(path_str)

    def check_readable(self, path: Path) -> bool:
        """
        Check if path has read permissions.

        Args:
            path: Path to check

        Returns:
            True if readable, False otherwise
        """
        return self._file_ops.check_readable(path)

    def create_directory(self, path: Path, mode: int = 0o755) -> None:
        """
        Create directory with proper permissions.

        Args:
            path: Directory path to create
            mode: Directory permissions mode
        """
        self._file_ops.create_directory(path, mode)

    def files_are_identical(self, src_path: Path, dest_path: Path) -> bool:
        """
        Compare two files to determine if they are identical.

        Args:
            src_path: Source file path
            dest_path: Destination file path

        Returns:
            True if files are identical (same size and mtime), False otherwise
        """
        return self._file_ops.files_are_identical(src_path, dest_path)

    def copy_file(
        self,
        src_path: Path,
        dest_path: Path,
        create_parent: bool = True,
        skip_identical: bool = False,
    ) -> bool:
        """
        Copy file with metadata preservation.

        Args:
            src_path: Source file path
            dest_path: Destination file path
            create_parent: Whether to create parent directories
            skip_identical: Whether to skip copying if files are identical

        Returns:
            True if copied successfully or skipped due to identical files
        """
        return self._file_ops.copy_file(
            src_path, dest_path, create_parent, skip_identical
        )

    def copy_directory(
        self, src_path: Path, dest_base: Path, skip_identical: bool = False
    ) -> list[tuple[Path, Path | None, bool, bool]]:
        """
        Copy directory recursively with all files.

        Args:
            src_path: Source directory path
            dest_base: Destination base path
            skip_identical: Whether to skip copying if files are identical

        Returns:
            List of (src_file, dest_file, success, skipped) tuples for each file
        """
        return self._file_ops.copy_directory(src_path, dest_base, skip_identical)

    def calculate_path_size(self, path: Path) -> int:
        """
        Calculate total size of a file or directory in bytes.

        Args:
            path: Path to file or directory

        Returns:
            Total size in bytes, 0 if path doesn't exist or permission denied
        """
        return self._file_ops.calculate_path_size(path)

    def get_dotfile_sizes(self) -> dict[int, int]:
        """
        Calculate sizes for all configured dotfiles.

        Returns:
            Dict mapping dotfile index to total size in bytes
        """
        size_results: dict[int, int] = {}

        for i, dotfile in enumerate(self.dotfiles):
            total_size = 0
            for path_str in dotfile["paths"]:
                if path_str:
                    path = self.expand_path(path_str)
                    total_size += self.calculate_path_size(path)
            size_results[i] = total_size

        return size_results

    def assemble_dest_path(
        self,
        base_path: Path,
        src_path: Path,
        hostname_subdir: bool,
        date_subdir: bool,
    ) -> Path:
        """
        Assemble destination path based on source and options.

        Args:
            base_path: Base destination directory
            src_path: Source file/directory path
            hostname_subdir: Include hostname subdirectory
            date_subdir: Include date subdirectory

        Returns:
            Assembled destination path
        """
        return self._file_ops.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

    def create_archive(
        self, dotfiles_to_archive: list[tuple[Path, bool, bool]]
    ) -> Path | None:
        """
        Create compressed TAR.GZ archive of existing dotfiles.

        Args:
            dotfiles_to_archive: List of (path, exists, is_dir) tuples

        Returns:
            Path to created archive file, or None if operation failed
        """
        return self._file_ops.create_archive(
            dotfiles_to_archive,
            self.archive_base_dir,
            self.options["hostname_subdir"],
        )

    def rotate_archives(self) -> list[Path]:
        """
        Delete oldest archives exceeding maximum retention limit.

        Returns:
            List of deleted archive paths
        """
        return self._file_ops.rotate_archives(
            self.archive_base_dir,
            self.options["hostname_subdir"],
            self.options["max_archives"],
        )

    def discover_restore_files(self, src_dir: Path) -> list[Path]:
        """
        Find all files in restore source directory recursively.

        Args:
            src_dir: Source directory containing backup files

        Returns:
            List of all file paths found
        """
        return self._file_ops.discover_restore_files(src_dir)

    def reconstruct_restore_paths(
        self, src_files: list[Path]
    ) -> list[tuple[Path, Path | None]]:
        """
        Build original destination paths from backup structure.

        Args:
            src_files: List of source files from backup

        Returns:
            List of (src_path, dest_path) tuples
        """
        return self._file_ops.reconstruct_restore_paths(src_files)

    def validate_dotfile_paths(self) -> dict[int, tuple[bool, bool, str]]:
        """
        Validate all dotfile paths exist and determine their types.

        Returns:
            Dict mapping dotfile index to (exists, is_dir, type_str) tuple
        """
        # CONSTRAINT: LegacyDotFileDict is structurally compatible with DotFileDict — cast is safe; type: ignore avoids spurious mypy error
        dotfiles_for_validation: list[DotFileDict] = self.dotfiles  # type: ignore[assignment]
        return self._backup_orchestrator.validate_dotfile_paths(dotfiles_for_validation)

    def execute_restore(
        self,
        src_dir: Path,
        progress_callback: Callable[[int], None] | None = None,
        item_processed_callback: Callable[[str, str], None] | None = None,
    ) -> tuple[int, int]:
        """
        Execute restore operation with pre-restore safety backup.

        Delegates to BackupOrchestrator which handles pre-restore backup
        if enabled in configuration.

        Args:
            src_dir: Source backup directory to restore from
            progress_callback: Optional callback for progress updates (percent)
            item_processed_callback: Optional callback for processed items (src, dest)

        Returns:
            Tuple of (successful_items, total_items)
        """
        pre_restore_enabled = self._config_manager.options.get(
            "pre_restore_backup", True
        )
        return self._backup_orchestrator.execute_restore(
            src_dir,
            pre_restore_enabled=pre_restore_enabled,
            progress_callback=progress_callback,
            item_processed_callback=item_processed_callback,
        )

    def record_item_processed(self, processing_time: float) -> None:
        """
        Record successfully processed item.

        Args:
            processing_time: Time taken to process item
        """
        self._stats_tracker.record_item_processed(processing_time)

    def record_item_skipped(self) -> None:
        """Record skipped item (not exist or no permission)."""
        self._stats_tracker.record_item_skipped()

    def record_item_failed(self) -> None:
        """Record failed item."""
        self._stats_tracker.record_item_failed()

    def reset_statistics(self) -> None:
        """Reset operation statistics for new run."""
        self._stats_tracker.reset_statistics()

    def verify_last_backup(self) -> str | None:
        """
        Verify integrity of the last backup operation.

        Uses the Model's tracked file pairs (populated by BackupWorker)
        rather than BackupOrchestrator's tracking (which BackupWorker bypasses).

        Returns:
            Formatted verification report for log display, or None if no backup to verify
        """
        if not self._last_backup_files:
            return None

        report = self._verification_manager.verify_backup(
            backup_path=self.mirror_base_dir,
            source_paths=self._last_backup_files,
            backup_type="mirror",
        )
        return self._verification_manager.format_report_for_log(report)

    def get_last_backup_file_count(self) -> int:
        """
        Get the number of files from the last backup operation.

        Returns:
            Number of files tracked for verification
        """
        return len(self._last_backup_files)

    def register_backed_up_file(self, source: Path, backup: Path) -> None:
        """
        Register a successfully backed up file for verification tracking.

        Called by BackupWorker after each successful file copy.

        Args:
            source: Original source file path
            backup: Backup destination file path
        """
        self._last_backup_files.append((source, backup))

    def clear_backup_tracking(self) -> None:
        """
        Clear the tracked backup files list.

        Should be called at the start of a new backup operation.
        """
        self._last_backup_files.clear()

    def set_hash_verification_enabled(self, enabled: bool) -> None:
        """
        Enable or disable SHA-256 hash verification.

        Args:
            enabled: Whether to enable hash verification
        """
        self._verification_manager.hash_verification_enabled = enabled

    def analyze_backup_size(
        self,
        progress_callback: Callable[[int], None] | None = None,
    ) -> SizeReportDict:
        """
        Analyze sizes of all configured dotfiles before backup.

        Loads .dfbuignore patterns and analyzes enabled dotfiles.

        Args:
            progress_callback: Optional callback for progress updates (0-100)

        Returns:
            SizeReportDict with analysis results
        """
        ignore_file = self._config_manager.config_path / ".dfbuignore"
        patterns = self._size_analyzer.load_ignore_patterns(ignore_file)

        enabled_dotfiles = [df for df in self.dotfiles if df.get("enabled", True)]
        # CONSTRAINT: LegacyDotFileDict is structurally compatible with DotFileDict for size analysis — cast is safe
        dotfiles_for_analysis: list[DotFileDict] = enabled_dotfiles  # type: ignore[assignment]

        return self._size_analyzer.analyze_dotfiles(
            dotfiles=dotfiles_for_analysis,
            progress_callback=progress_callback,
            ignore_patterns=patterns,
        )

    def is_size_check_enabled(self) -> bool:
        """
        Check if pre-backup size checking is enabled.

        Returns:
            True if size checking is enabled
        """
        return self._size_analyzer.size_check_enabled

    def set_size_check_enabled(self, enabled: bool) -> None:
        """
        Enable or disable pre-backup size checking.

        Args:
            enabled: Whether to enable size checking
        """
        self._size_analyzer.size_check_enabled = enabled

    def format_size_report(self, report: SizeReportDict) -> str:
        """
        Format a size report for display in the log viewer.

        Args:
            report: Size analysis report dictionary

        Returns:
            Human-readable formatted string for log output
        """
        return self._size_analyzer.format_report_for_log(report)

    def get_profile_count(self) -> int:
        """Get number of saved profiles."""
        return self._profile_manager.get_profile_count()

    def get_profile_names(self) -> list[str]:
        """Get list of all profile names."""
        return self._profile_manager.get_profile_names()

    def get_active_profile_name(self) -> str | None:
        """Get name of currently active profile."""
        return self._profile_manager.get_active_profile_name()

    def create_profile(
        self,
        name: str,
        description: str,
        excluded: list[str],
        options_overrides: dict[str, bool | int | str] | None = None,
    ) -> bool:
        """Create a new backup profile."""
        success = self._profile_manager.create_profile(
            name, description, excluded, options_overrides
        )
        if success:
            self._profile_manager.save_profiles()
        return success

    def delete_profile(self, name: str) -> bool:
        """Delete a profile by name."""
        success = self._profile_manager.delete_profile(name)
        if success:
            self._profile_manager.save_profiles()
        return success

    def switch_profile(self, name: str | None) -> bool:
        """Switch to a different profile."""
        success = self._profile_manager.switch_profile(name)
        if success:
            self._profile_manager.save_profiles()
        return success

    def get_profile_manager(self) -> ProfileManager:
        """Get ProfileManager instance for advanced operations."""
        return self._profile_manager

    def get_backup_history_count(self) -> int:
        """
        Get number of backup history entries.

        Returns:
            Number of recorded backup operations
        """
        return self._history_manager.get_entry_count()

    def record_backup_history(
        self,
        items_backed: int,
        size_bytes: int,
        duration_seconds: float,
        success: bool,
        backup_type: str,
    ) -> None:
        """
        Record a backup operation to history.

        Args:
            items_backed: Number of items backed up
            size_bytes: Total size backed up in bytes
            duration_seconds: Duration of backup operation
            success: Whether backup completed successfully
            backup_type: Type of backup ("mirror" or "archive")
        """
        profile = self.get_active_profile_name() or "Default"
        self._history_manager.record_backup(
            items_backed=items_backed,
            size_bytes=size_bytes,
            duration_seconds=duration_seconds,
            success=success,
            backup_type=backup_type,
            profile=profile,
        )

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """
        Get dashboard metrics from backup history.

        Returns:
            DashboardMetrics with aggregate statistics
        """
        return self._history_manager.get_metrics()

    def get_recent_backup_history(self, count: int = 10) -> list[BackupHistoryEntry]:
        """
        Get recent backup history entries.

        Args:
            count: Number of entries to return

        Returns:
            List of recent history entries (newest first)
        """
        return self._history_manager.get_recent_history(count)

    def _init_preview_generator(self) -> None:
        """
        Lazy initialize PreviewGenerator.

        Creates PreviewGenerator on first use to ensure config is loaded first.
        """
        if self._preview_generator is None:
            self._preview_generator = PreviewGenerator(
                file_ops=self._file_ops,
                mirror_base_dir=self._config_manager.mirror_base_dir,
            )

    def generate_backup_preview(
        self,
        progress_callback: Callable[[int], None] | None = None,
    ) -> BackupPreviewDict:
        """
        Generate preview of what would be backed up.

        Args:
            progress_callback: Optional callback for progress updates (0-100)

        Returns:
            BackupPreviewDict with preview results
        """
        self._init_preview_generator()

        enabled_dotfiles = [df for df in self.dotfiles if df.get("enabled", True)]

        hostname_subdir = self._config_manager.options.get("hostname_subdir", True)
        date_subdir = self._config_manager.options.get("date_subdir", False)

        # CONSTRAINT: assert satisfies mypy after _init_preview_generator(); LegacyDotFileDict is compatible with dict[str, Any]
        assert self._preview_generator is not None
        dotfiles_for_preview: list[dict[str, Any]] = enabled_dotfiles  # type: ignore[assignment]
        return self._preview_generator.generate_preview(
            dotfiles=dotfiles_for_preview,
            hostname_subdir=hostname_subdir,
            date_subdir=date_subdir,
            progress_callback=progress_callback,
        )
