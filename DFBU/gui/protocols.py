"""
DFBU Protocol Definitions - Interface Abstractions for Dependency Inversion

Description:
    Protocol definitions for DFBU GUI application following the Dependency
    Inversion Principle (DIP). Defines interfaces that allow components to
    depend on abstractions rather than concrete implementations, improving
    testability and maintainability.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-05-2025
Date Changed: 02-01-2026
License: MIT

Features:
    - Protocol definitions for service layer interfaces
    - Enables dependency injection with type safety
    - Facilitates mocking in tests without complex class hierarchies
    - Follows Interface Segregation Principle (ISP)
    - Pure Python typing without runtime overhead

Requirements:
    - Python 3.14+ for Protocol support
    - typing module from standard library

Classes:
    - FileOperationsProtocol: Interface for file system operations
    - ConfigManagerProtocol: Interface for configuration management
    - StatisticsTrackerProtocol: Interface for statistics tracking
    - BackupOrchestratorProtocol: Interface for backup orchestration
    - RestoreBackupManagerProtocol: Interface for pre-restore backup management
    - VerificationManagerProtocol: Interface for backup verification
    - ErrorHandlerProtocol: Interface for structured error handling
    - SizeAnalyzerProtocol: Interface for file size analysis and management

Functions:
    None
"""

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Protocol


sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import (
    DotFileDict,
    LegacyDotFileDict,
    OperationResultDict,
    OptionsDict,
    PathResultDict,
    SizeReportDict,
    VerificationReportDict,
)

from gui.statistics_tracker import BackupStatistics


class FileOperationsProtocol(Protocol):
    """
    Protocol defining interface for file system operations.

    Implementations must provide file/directory operations including
    path expansion, permission checking, copying, and size calculation.
    """

    def expand_path(self, path_str: str) -> Path:
        """
        Expand user home directory in path string.

        Args:
            path_str: Path string potentially containing ~

        Returns:
            Expanded Path object
        """
        ...

    def check_readable(self, path: Path) -> bool:
        """
        Check if path has read permissions.

        Args:
            path: Path to check

        Returns:
            True if readable, False otherwise
        """
        ...

    def create_directory(self, path: Path, mode: int = 0o755) -> None:
        """
        Create directory with proper permissions.

        Args:
            path: Directory path to create
            mode: Directory permissions mode
        """
        ...

    def files_are_identical(self, src_path: Path, dest_path: Path) -> bool:
        """
        Compare two files to determine if they are identical.

        Args:
            src_path: Source file path
            dest_path: Destination file path

        Returns:
            True if files are identical (same size and mtime), False otherwise
        """
        ...

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
        ...

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
        ...

    def calculate_path_size(self, path: Path) -> int:
        """
        Calculate total size of a file or directory in bytes.

        Args:
            path: Path to file or directory

        Returns:
            Total size in bytes, 0 if path doesn't exist or permission denied
        """
        ...

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
        ...

    def create_archive(
        self,
        dotfiles_to_archive: list[tuple[Path, bool, bool]],
        archive_base_dir: Path,
        hostname_subdir: bool,
    ) -> Path | None:
        """
        Create compressed TAR.GZ archive of existing dotfiles.

        Args:
            dotfiles_to_archive: List of (path, exists, is_dir) tuples
            archive_base_dir: Base directory for archives
            hostname_subdir: Include hostname subdirectory in archive path

        Returns:
            Path to created archive file, or None if operation failed
        """
        ...

    def rotate_archives(
        self, archive_base_dir: Path, hostname_subdir: bool, max_archives: int
    ) -> list[Path]:
        """
        Delete oldest archives exceeding maximum retention limit.

        Args:
            archive_base_dir: Base directory for archives
            hostname_subdir: Whether archives are in hostname subdirectory
            max_archives: Maximum number of archives to retain

        Returns:
            List of deleted archive paths
        """
        ...

    def discover_restore_files(self, src_dir: Path) -> list[Path]:
        """
        Find all files in restore source directory recursively.

        Args:
            src_dir: Source directory containing backup files

        Returns:
            List of all file paths found
        """
        ...

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
        ...


class ConfigManagerProtocol(Protocol):
    """
    Protocol defining interface for configuration management.

    Implementations must provide configuration loading, saving, validation,
    and manipulation operations.
    """

    @property
    def config_path(self) -> Path:
        """Get current configuration file path."""
        ...

    @property
    def options(self) -> OptionsDict:
        """Get current options configuration."""
        ...

    @property
    def dotfiles(self) -> list[LegacyDotFileDict]:
        """Get current dotfiles list."""
        ...

    @property
    def mirror_base_dir(self) -> Path:
        """Get mirror backup base directory."""
        ...

    @mirror_base_dir.setter
    def mirror_base_dir(self, path: Path) -> None:
        """Set mirror backup base directory."""
        ...

    @property
    def archive_base_dir(self) -> Path:
        """Get archive backup base directory."""
        ...

    @archive_base_dir.setter
    def archive_base_dir(self, path: Path) -> None:
        """Set archive backup base directory."""
        ...

    def load_config(self) -> tuple[bool, str]:
        """
        Load and validate YAML configuration files.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        ...

    def save_config(self) -> tuple[bool, str]:
        """
        Save current configuration back to YAML files with automatic rotating backups.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        ...

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
        ...

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
        ...

    def remove_dotfile(self, index: int) -> bool:
        """
        Remove a dotfile entry from the configuration by index.

        Args:
            index: Index of dotfile to remove

        Returns:
            True if dotfile was removed successfully
        """
        ...

    def toggle_dotfile_enabled(self, index: int) -> bool:
        """
        Toggle the enabled status of a dotfile entry.

        Args:
            index: Index of dotfile to toggle

        Returns:
            New enabled status if successful, current status otherwise
        """
        ...

    def update_option(self, key: str, value: bool | int | str) -> bool:
        """
        Update a single configuration option.

        Args:
            key: Option key to update
            value: New value for the option

        Returns:
            True if option was updated successfully
        """
        ...

    def update_path(self, path_type: str, value: str) -> bool:
        """
        Update mirror_dir, archive_dir, or restore_backup_dir path.

        Args:
            path_type: One of "mirror_dir", "archive_dir", or "restore_backup_dir"
            value: New path value

        Returns:
            True if path was updated successfully
        """
        ...

    def get_dotfile_by_index(self, index: int) -> LegacyDotFileDict | None:
        """
        Get dotfile metadata by index.

        Args:
            index: Index in dotfiles list

        Returns:
            Dotfile dictionary or None if invalid index
        """
        ...

    def get_dotfile_count(self) -> int:
        """
        Get number of configured dotfiles.

        Returns:
            Number of dotfiles in configuration
        """
        ...


class StatisticsTrackerProtocol(Protocol):
    """
    Protocol defining interface for backup/restore statistics tracking.

    Implementations must provide statistics recording and retrieval.
    """

    @property
    def statistics(self) -> BackupStatistics:
        """Get current operation statistics."""
        ...

    def record_item_processed(self, processing_time: float) -> None:
        """
        Record successfully processed item.

        Args:
            processing_time: Time taken to process item
        """
        ...

    def record_item_skipped(self) -> None:
        """Record skipped item (not exist or no permission)."""
        ...

    def record_item_failed(self) -> None:
        """Record failed item."""
        ...

    def reset_statistics(self) -> None:
        """Reset operation statistics for new run."""
        ...


class BackupOrchestratorProtocol(Protocol):
    """
    Protocol defining interface for backup orchestration.

    Implementations must coordinate backup operations across components.
    """

    @property
    def mirror_base_dir(self) -> Path:
        """Get mirror backup base directory."""
        ...

    @mirror_base_dir.setter
    def mirror_base_dir(self, path: Path) -> None:
        """Set mirror backup base directory."""
        ...

    @property
    def archive_base_dir(self) -> Path:
        """Get archive backup base directory."""
        ...

    @archive_base_dir.setter
    def archive_base_dir(self, path: Path) -> None:
        """Set archive backup base directory."""
        ...

    def validate_dotfile_paths(
        self, dotfiles: list[DotFileDict]
    ) -> dict[int, tuple[bool, bool, str]]:
        """
        Validate all dotfile paths exist and determine their types.

        Args:
            dotfiles: List of dotfile dictionaries to validate

        Returns:
            Dict mapping dotfile index to (exists, is_dir, type_str) tuple
        """
        ...


class RestoreBackupManagerProtocol(Protocol):
    """
    Protocol defining interface for pre-restore backup management.

    Implementations must provide backup creation before restore operations,
    manifest tracking, and retention policy enforcement.
    """

    @property
    def backup_base_dir(self) -> Path:
        """Get base directory for restore backups."""
        ...

    @property
    def max_backups(self) -> int:
        """Get maximum number of restore backups to retain."""
        ...

    @max_backups.setter
    def max_backups(self, value: int) -> None:
        """Set maximum number of restore backups to retain."""
        ...

    def backup_before_restore(
        self,
        files_to_overwrite: list[Path],
        source_backup_path: str,
    ) -> tuple[bool, str, Path | None]:
        """
        Create backup of files that will be overwritten during restore.

        Args:
            files_to_overwrite: List of destination paths that will be overwritten
            source_backup_path: Path to the backup being restored from

        Returns:
            Tuple of (success, error_message, backup_directory)
        """
        ...

    def get_backup_count(self) -> int:
        """
        Get number of existing restore backups.

        Returns:
            Number of backup directories in backup_base_dir
        """
        ...

    def cleanup_old_backups(self) -> list[Path]:
        """
        Remove oldest backups exceeding max_backups limit.

        Returns:
            List of removed backup directory paths
        """
        ...

    def list_backups(self) -> list[tuple[Path, str]]:
        """
        List all restore backups with their timestamps.

        Returns:
            List of (backup_path, timestamp_str) tuples, newest first
        """
        ...


class VerificationManagerProtocol(Protocol):
    """
    Protocol defining interface for backup verification management.

    Implementations must provide file verification (size and hash comparison)
    and report generation for backup integrity checking.
    """

    @property
    def hash_verification_enabled(self) -> bool:
        """Get whether SHA-256 hash verification is enabled."""
        ...

    @hash_verification_enabled.setter
    def hash_verification_enabled(self, value: bool) -> None:
        """Set whether SHA-256 hash verification is enabled."""
        ...

    def verify_backup(
        self,
        backup_path: Path,
        source_paths: list[tuple[Path, Path]],
        backup_type: str = "mirror",
    ) -> VerificationReportDict:
        """
        Verify integrity of a backup by comparing files against sources.

        Args:
            backup_path: Base path of the backup to verify
            source_paths: List of (source_path, backup_path) tuples to verify
            backup_type: Type of backup ("mirror" or "archive")

        Returns:
            VerificationReportDict with verification results
        """
        ...

    def verify_file(
        self,
        source_path: Path,
        backup_path: Path,
    ) -> tuple[bool, bool | None, str]:
        """
        Verify a single file's integrity.

        Args:
            source_path: Original source file path
            backup_path: File path in the backup

        Returns:
            Tuple of (size_match, hash_match, error_message)
            hash_match is None if hash verification is disabled
        """
        ...

    def format_report_for_log(self, report: VerificationReportDict) -> str:
        """
        Format a verification report for display in the log viewer.

        Args:
            report: Verification report dictionary

        Returns:
            Human-readable formatted string for log output
        """
        ...


class ErrorHandlerProtocol(Protocol):
    """
    Protocol defining interface for structured error handling.

    Implementations must provide error categorization, user-friendly message
    formatting, and operation result tracking for backup/restore operations.
    """

    def create_path_result(
        self,
        path: str,
        dest_path: str | None,
        status: str,
        error_type: str | None = None,
        error_message: str = "",
        can_retry: bool = False,
    ) -> PathResultDict:
        """
        Create a structured result for a single path operation.

        Args:
            path: The file or directory path that was processed
            dest_path: Destination path for copy operations
            status: Result status ("success", "failed", "skipped", "warning")
            error_type: Error category if failed
            error_message: Human-readable error message
            can_retry: Whether this operation might succeed on retry

        Returns:
            PathResultDict with operation result
        """
        ...

    def create_operation_result(
        self,
        operation_type: str,
    ) -> OperationResultDict:
        """
        Create a new empty operation result for tracking.

        Args:
            operation_type: Type of operation ("mirror_backup", "archive_backup", "restore")

        Returns:
            OperationResultDict initialized for tracking
        """
        ...

    def handle_exception(
        self,
        exception: Exception,
        path: str,
        dest_path: str | None = None,
    ) -> PathResultDict:
        """
        Convert an exception to a structured PathResultDict.

        Categorizes exceptions and generates user-friendly error messages.

        Args:
            exception: The exception that occurred
            path: Path where the error occurred
            dest_path: Destination path if applicable

        Returns:
            PathResultDict with categorized error information
        """
        ...

    def format_user_message(
        self,
        error_type: str,
        path: str,
        original_error: str = "",
    ) -> str:
        """
        Format a technical error into a user-friendly message.

        Args:
            error_type: Error category (e.g., "permission", "not_found", "disk_full")
            path: Path where the error occurred
            original_error: Original technical error message

        Returns:
            User-friendly error message with actionable guidance
        """
        ...

    def finalize_result(
        self,
        result: OperationResultDict,
    ) -> OperationResultDict:
        """
        Finalize an operation result, determining overall status.

        Sets the status field based on completed/failed/skipped counts
        and populates the can_retry list.

        Args:
            result: The operation result to finalize

        Returns:
            Finalized OperationResultDict with status determined
        """
        ...

    def format_summary_for_log(
        self,
        result: OperationResultDict,
    ) -> str:
        """
        Format an operation result for display in the log viewer.

        Args:
            result: Operation result to format

        Returns:
            Human-readable formatted string for log output
        """
        ...

    def get_retryable_paths(
        self,
        result: OperationResultDict,
    ) -> list[str]:
        """
        Get list of paths that can be retried.

        Args:
            result: Operation result containing failed paths

        Returns:
            List of path strings that might succeed on retry
        """
        ...


class SizeAnalyzerProtocol(Protocol):
    """
    Protocol defining interface for file size analysis and management.

    Implementations must provide size calculation, threshold checking,
    exclusion pattern parsing, and report generation for pre-backup
    size warnings.
    """

    @property
    def warning_threshold_mb(self) -> int:
        """Get warning threshold in megabytes (default: 10)."""
        ...

    @warning_threshold_mb.setter
    def warning_threshold_mb(self, value: int) -> None:
        """Set warning threshold in megabytes."""
        ...

    @property
    def alert_threshold_mb(self) -> int:
        """Get alert threshold in megabytes (default: 100)."""
        ...

    @alert_threshold_mb.setter
    def alert_threshold_mb(self, value: int) -> None:
        """Set alert threshold in megabytes."""
        ...

    @property
    def critical_threshold_mb(self) -> int:
        """Get critical threshold in megabytes (default: 1024)."""
        ...

    @critical_threshold_mb.setter
    def critical_threshold_mb(self, value: int) -> None:
        """Set critical threshold in megabytes."""
        ...

    @property
    def size_check_enabled(self) -> bool:
        """Get whether size checking is enabled."""
        ...

    @size_check_enabled.setter
    def size_check_enabled(self, value: bool) -> None:
        """Set whether size checking is enabled."""
        ...

    def analyze_dotfiles(
        self,
        dotfiles: list[DotFileDict],
        progress_callback: Callable[[int], None] | None = None,
        ignore_patterns: list[str] | None = None,
    ) -> SizeReportDict:
        """
        Analyze sizes of all configured dotfiles.

        Args:
            dotfiles: List of dotfile dictionaries to analyze
            progress_callback: Optional callback for progress updates (0-100)
            ignore_patterns: Optional list of gitignore-style exclusion patterns

        Returns:
            SizeReportDict with analysis results
        """
        ...

    def load_ignore_patterns(self, ignore_file: Path) -> list[str]:
        """
        Load exclusion patterns from .dfbuignore file.

        Args:
            ignore_file: Path to .dfbuignore file

        Returns:
            List of gitignore-style patterns
        """
        ...

    def matches_ignore_pattern(self, path: Path, patterns: list[str]) -> bool:
        """
        Check if a path matches any exclusion pattern.

        Args:
            path: Path to check
            patterns: List of gitignore-style patterns

        Returns:
            True if path should be excluded, False otherwise
        """
        ...

    def categorize_size(self, size_bytes: int) -> str:
        """
        Categorize a size by threshold level.

        Args:
            size_bytes: Size in bytes

        Returns:
            Threshold level: "info", "warning", "alert", or "critical"
        """
        ...

    def format_report_for_log(self, report: SizeReportDict) -> str:
        """
        Format a size report for display in the log viewer.

        Args:
            report: Size analysis report dictionary

        Returns:
            Human-readable formatted string for log output
        """
        ...
