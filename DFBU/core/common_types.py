"""
Shared Type Definitions for DFBU

Description:
    Common TypedDict definitions used across CLI and GUI modules.
    Centralizes type definitions to eliminate duplication and ensure
    consistency across the application.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 02-01-2026
License: MIT

Features:
    - Centralized TypedDict definitions for dotfile configuration
    - Shared type definitions for backup options and settings
    - Type safety across CLI and GUI modules
    - Support for YAML configuration format migration
    - Standard library only (no external dependencies)

Requirements:
    - Python 3.14+ for latest typing features

Classes:
    - PathsDict: TypedDict for backup directory paths
    - OptionsDict: TypedDict for backup options configuration
    - SettingsDict: TypedDict combining paths and options
    - DotFileDict: TypedDict for dotfile configuration (YAML format)
    - SessionDict: TypedDict for session-specific exclusions
    - LegacyDotFileDict: TypedDict for TOML migration support
    - SizeItemDict: TypedDict for individual file/directory size entry
    - SizeReportDict: TypedDict for backup size analysis report
    - ProfileDict: TypedDict for backup profile configuration (v1.1.0)
    - PreviewItemDict: TypedDict for individual backup preview item (v1.1.0)
    - BackupPreviewDict: TypedDict for backup preview result (v1.1.0)
"""

from typing import Required, TypedDict


class PathsDict(TypedDict):
    """
    Type definition for backup directory paths configuration.

    Contains all directory paths used for backup operations.
    """

    mirror_dir: str
    archive_dir: str
    restore_backup_dir: str


class OptionsDict(TypedDict):
    """
    Type definition for backup options configuration dictionary.

    Contains all backup operation settings and preferences.
    All fields are required to ensure type safety.
    """

    mirror: bool
    archive: bool
    hostname_subdir: bool
    date_subdir: bool
    archive_format: str
    archive_compression_level: int
    rotate_archives: bool
    max_archives: int
    pre_restore_backup: bool
    max_restore_backups: int
    verify_after_backup: bool
    hash_verification: bool
    # CONSTRAINT: All three threshold fields required; size_analyzer.py reads all three to classify items
    size_check_enabled: bool
    size_warning_threshold_mb: int
    size_alert_threshold_mb: int
    size_critical_threshold_mb: int


class SettingsDict(TypedDict):
    """
    Type definition for combined settings configuration.

    Contains both paths and options in a single structure,
    matching the top-level settings section in YAML config.
    """

    paths: PathsDict
    options: OptionsDict


class DotFileDict(TypedDict, total=False):
    """
    Type definition for dotfile configuration dictionary (YAML format).

    Contains metadata and path information for individual dotfile entries.
    Supports both single path (path) and multiple paths (paths) per entry.
    All fields are optional (total=False) except description.

    Fields:
        description: Human-readable description of the dotfile (required)
        path: Single path string (optional, mutually exclusive with paths)
        paths: List of path strings (optional, mutually exclusive with path)
        tags: Comma-separated tags for categorization (optional)
    """

    description: Required[str]
    path: str
    paths: list[str]
    tags: str


class SessionDict(TypedDict):
    """
    Type definition for session-specific exclusions.

    Contains the list of applications excluded from the current session.
    """

    excluded: list[str]


class LegacyDotFileDict(TypedDict):
    """
    Type definition for legacy TOML dotfile configuration.

    Used for migration from TOML to YAML format. Contains all fields
    from the original TOML [[dotfile]] entries.

    Fields:
        category: Category grouping (e.g., "Shell", "Editor")
        application: Application name (e.g., "Bash", "Vim")
        description: Human-readable description
        paths: List of file/directory paths
        mirror_dir: Override mirror directory (optional in TOML)
        archive_dir: Override archive directory (optional in TOML)
        enabled: Whether dotfile is enabled for backup
    """

    category: str
    application: str
    description: str
    paths: list[str]
    mirror_dir: str
    archive_dir: str
    enabled: bool


class VerificationResultDict(TypedDict):
    """
    Type definition for individual file verification result.

    Contains verification status and details for a single file.

    Fields:
        path: Original source path that was backed up
        backup_path: Path in the backup directory
        status: Verification status ("ok", "size_mismatch", "hash_mismatch", "missing", "error")
        size_match: Whether file sizes match
        hash_match: Whether SHA-256 hashes match (None if not checked)
        expected_size: Expected file size in bytes
        actual_size: Actual file size in bytes (None if file missing)
        error: Error message if status is "error"
    """

    path: str
    backup_path: str
    status: str
    size_match: bool
    hash_match: bool | None
    expected_size: int
    actual_size: int | None
    error: str


class VerificationReportDict(TypedDict):
    """
    Type definition for backup verification report.

    Contains overall verification summary and individual file results.

    Fields:
        timestamp: ISO format timestamp of verification
        backup_type: Type of backup verified ("mirror" or "archive")
        backup_path: Path to the backup that was verified
        total_files: Total number of files checked
        verified_ok: Number of files that passed verification
        verified_failed: Number of files that failed verification
        hash_verified: Whether SHA-256 hash verification was performed
        results: List of individual file verification results
    """

    timestamp: str
    backup_type: str
    backup_path: str
    total_files: int
    verified_ok: int
    verified_failed: int
    hash_verified: bool
    results: list[VerificationResultDict]


# Error result types — returned by model.py operations; consumed by view.py error handlers and viewmodel.py


class PathResultDict(TypedDict):
    """
    Type definition for individual path operation result.

    Contains the result of an operation on a single file or directory path.

    Fields:
        path: The file or directory path that was processed
        dest_path: Destination path (for copy operations, None if not applicable)
        status: Result status ("success", "failed", "skipped", "warning")
        error_type: Error category if failed (None if success)
        error_message: Human-readable error message (empty if success)
        can_retry: Whether this operation might succeed on retry
    """

    path: str
    dest_path: str | None
    status: str  # "success", "failed", "skipped", "warning"
    error_type: str | None  # "permission", "not_found", "disk_full", "locked", etc.
    error_message: str
    can_retry: bool


class OperationResultDict(TypedDict):
    """
    Type definition for structured operation result.

    Contains comprehensive result information for backup/restore operations,
    replacing simple success/fail returns with detailed tracking.

    Fields:
        status: Overall operation status ("success", "partial", "failed")
        operation_type: Type of operation ("mirror_backup", "archive_backup", "restore")
        total_items: Total number of items attempted
        completed: List of successfully processed paths
        failed: List of paths that failed with error details
        skipped: List of paths that were skipped with reasons
        warnings: List of non-fatal warning messages
        can_retry: List of paths that might succeed on retry
        timestamp: ISO format timestamp of operation
    """

    status: str  # "success", "partial", "failed"
    operation_type: str  # "mirror_backup", "archive_backup", "restore"
    total_items: int
    completed: list[PathResultDict]
    failed: list[PathResultDict]
    skipped: list[PathResultDict]
    warnings: list[str]
    can_retry: list[str]  # List of path strings that can be retried
    timestamp: str


# Size analysis types — populated by size_analyzer.py; consumed by size_warning_dialog.py


class SizeItemDict(TypedDict):
    """
    Type definition for individual file/directory size entry.

    Contains size information and threshold level for a single path.

    Fields:
        path: Absolute path to the file or directory
        size_bytes: Total size in bytes
        size_mb: Size in megabytes (for display)
        level: Threshold level ("info", "warning", "alert", "critical")
        is_dir: Whether the path is a directory
        application: Name of the dotfile application this belongs to
    """

    path: str
    size_bytes: int
    size_mb: float
    level: str  # "info", "warning", "alert", "critical"
    is_dir: bool
    application: str


class SizeReportDict(TypedDict):
    """
    Type definition for backup size analysis report.

    Contains overall size summary and individual large item details.

    Fields:
        timestamp: ISO format timestamp of analysis
        total_files: Total number of files analyzed
        total_size_bytes: Total size of all files in bytes
        total_size_mb: Total size in megabytes (for display)
        items_by_level: Count of items at each threshold level
        large_items: List of items exceeding warning threshold
        has_critical: Whether any item exceeds critical threshold
        has_alert: Whether any item exceeds alert threshold
        has_warning: Whether any item exceeds warning threshold
        excluded_patterns: List of patterns from .dfbuignore that were applied
    """

    timestamp: str
    total_files: int
    total_size_bytes: int
    total_size_mb: float
    items_by_level: dict[str, int]  # {"warning": 3, "alert": 1, "critical": 0}
    large_items: list[SizeItemDict]
    has_critical: bool
    has_alert: bool
    has_warning: bool
    excluded_patterns: list[str]


# Profile types — stored in profiles.yaml; loaded by profile_manager.py; options_overrides merged at backup time


class ProfileDict(TypedDict):
    """
    Type definition for backup profile configuration.

    Contains named preset for different backup configurations.

    Fields:
        name: Display name for the profile
        description: Human-readable description
        excluded: List of application names to exclude
        options_overrides: Partial OptionsDict with overridden settings
        created_at: ISO format timestamp of creation
        modified_at: ISO format timestamp of last modification
    """

    name: str
    description: str
    excluded: list[str]
    options_overrides: dict[str, bool | int | str]
    created_at: str
    modified_at: str


# Backup preview types — generated by preview_generator.py; rendered in view.py preview tab


class PreviewItemDict(TypedDict):
    """
    Type definition for individual backup preview item.

    Contains information about a single file/directory in preview.

    Fields:
        path: Source path of the file
        dest_path: Destination path in backup
        size_bytes: Size in bytes
        status: Preview status ("new", "changed", "unchanged", "error")
        application: Name of the dotfile application
    """

    path: str
    dest_path: str
    size_bytes: int
    status: str  # "new", "changed", "unchanged", "error"
    application: str


class BackupPreviewDict(TypedDict):
    """
    Type definition for backup preview result.

    Contains summary and details of what would be backed up.

    Fields:
        items: List of individual preview items
        total_size_bytes: Total size of all items
        new_count: Number of new files
        changed_count: Number of changed files
        unchanged_count: Number of unchanged files
        error_count: Number of files with errors
    """

    items: list[PreviewItemDict]
    total_size_bytes: int
    new_count: int
    changed_count: int
    unchanged_count: int
    error_count: int


# Dashboard types — written to backup_history.yaml by backup_history.py; read by viewmodel.py get_metrics()


class BackupHistoryEntry(TypedDict):
    """
    Type definition for a single backup history entry.

    Records details of a completed backup operation for dashboard metrics.

    Fields:
        timestamp: ISO format timestamp of backup
        profile: Profile name used (or "Default")
        items_backed: Number of items backed up
        size_bytes: Total size backed up
        duration_seconds: Time taken for backup
        success: Whether backup completed successfully
        backup_type: Type of backup ("mirror" or "archive")
    """

    timestamp: str
    profile: str
    items_backed: int
    size_bytes: int
    duration_seconds: float
    success: bool
    backup_type: str


class DashboardMetrics(TypedDict):
    """
    Type definition for dashboard metrics summary.

    Aggregates backup history for display in dashboard view.

    Fields:
        total_backups: Total number of backups recorded
        successful_backups: Number of successful backups
        failed_backups: Number of failed backups
        success_rate: Success rate (0.0 to 1.0)
        total_size_backed_bytes: Total size of all backups
        average_duration_seconds: Average backup duration
        last_backup_timestamp: Timestamp of most recent backup (None if no history)
    """

    total_backups: int
    successful_backups: int
    failed_backups: int
    success_rate: float
    total_size_backed_bytes: int
    average_duration_seconds: float
    last_backup_timestamp: str | None
