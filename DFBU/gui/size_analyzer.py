#!/usr/bin/env python3
"""
DFBU SizeAnalyzer - File Size Analysis Component

Description:
    Analyzes file and directory sizes before backup operations to warn users
    about large files that may exceed Git repository size limits. Supports
    exclusion patterns via .dfbuignore files and configurable size thresholds.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 2026-02-01
Date Changed: 02-01-2026
License: MIT

Features:
    - Pre-backup size analysis for all configured dotfiles
    - Configurable size thresholds (warning, alert, critical)
    - .dfbuignore pattern support (gitignore-style exclusions)
    - Progress callbacks for non-blocking UI updates
    - Human-readable log output formatting

Requirements:
    - Linux environment
    - Python 3.14+
    - No Qt dependencies (pure model layer)

Classes:
    - SizeAnalyzer: Manages file size analysis operations
"""

from __future__ import annotations

import fnmatch
import logging
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Final


# SIDE-EFFECT: Mutates sys.path — must execute before any local module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import DotFileDict, SizeItemDict, SizeReportDict


if TYPE_CHECKING:
    from gui.protocols import FileOperationsProtocol


logger = logging.getLogger(__name__)


TIMESTAMP_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S"
BYTES_PER_MB: Final[int] = 1024 * 1024

DEFAULT_WARNING_THRESHOLD_MB: Final[int] = 10
DEFAULT_ALERT_THRESHOLD_MB: Final[int] = 100
DEFAULT_CRITICAL_THRESHOLD_MB: Final[int] = 1024


class SizeAnalyzer:
    """
    Manages file size analysis operations for pre-backup warnings.

    Analyzes dotfile sizes to warn users about large files or directories
    that may exceed Git repository size limits. Supports exclusion patterns
    and configurable thresholds.

    Attributes:
        warning_threshold_mb: Size threshold for warning level (default: 10 MB)
        alert_threshold_mb: Size threshold for alert level (default: 100 MB)
        critical_threshold_mb: Size threshold for critical level (default: 1024 MB)
        size_check_enabled: Whether size checking is enabled

    Public methods:
        analyze_dotfiles: Analyze sizes of all configured dotfiles
        load_ignore_patterns: Load patterns from .dfbuignore file
        matches_ignore_pattern: Check if path matches exclusion pattern
        categorize_size: Categorize size by threshold level
        format_report_for_log: Format report for log viewer display
    """

    def __init__(
        self,
        file_operations: FileOperationsProtocol,
        warning_threshold_mb: int = DEFAULT_WARNING_THRESHOLD_MB,
        alert_threshold_mb: int = DEFAULT_ALERT_THRESHOLD_MB,
        critical_threshold_mb: int = DEFAULT_CRITICAL_THRESHOLD_MB,
        size_check_enabled: bool = True,
    ) -> None:
        """
        Initialize SizeAnalyzer.

        Args:
            file_operations: FileOperations instance for size calculations
            warning_threshold_mb: Size threshold for warning level (default: 10 MB)
            alert_threshold_mb: Size threshold for alert level (default: 100 MB)
            critical_threshold_mb: Size threshold for critical level (default: 1024 MB)
            size_check_enabled: Whether size checking is enabled (default: True)
        """
        self._file_operations = file_operations
        self._warning_threshold_mb = warning_threshold_mb
        self._alert_threshold_mb = alert_threshold_mb
        self._critical_threshold_mb = critical_threshold_mb
        self._size_check_enabled = size_check_enabled

    @property
    def warning_threshold_mb(self) -> int:
        """Get warning threshold in megabytes."""
        return self._warning_threshold_mb

    @warning_threshold_mb.setter
    def warning_threshold_mb(self, value: int) -> None:
        """Set warning threshold in megabytes."""
        self._warning_threshold_mb = max(1, value)

    @property
    def alert_threshold_mb(self) -> int:
        """Get alert threshold in megabytes."""
        return self._alert_threshold_mb

    @alert_threshold_mb.setter
    def alert_threshold_mb(self, value: int) -> None:
        """Set alert threshold in megabytes."""
        self._alert_threshold_mb = max(1, value)

    @property
    def critical_threshold_mb(self) -> int:
        """Get critical threshold in megabytes."""
        return self._critical_threshold_mb

    @critical_threshold_mb.setter
    def critical_threshold_mb(self, value: int) -> None:
        """Set critical threshold in megabytes."""
        self._critical_threshold_mb = max(1, value)

    @property
    def size_check_enabled(self) -> bool:
        """Get whether size checking is enabled."""
        return self._size_check_enabled

    @size_check_enabled.setter
    def size_check_enabled(self, value: bool) -> None:
        """Set whether size checking is enabled."""
        self._size_check_enabled = value

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
            ignore_patterns: Optional list of exclusion patterns

        Returns:
            SizeReportDict with analysis results
        """
        patterns = ignore_patterns or []
        large_items: list[SizeItemDict] = []
        total_size_bytes = 0
        total_files = 0
        items_by_level: dict[str, int] = {
            "info": 0,
            "warning": 0,
            "alert": 0,
            "critical": 0,
        }

        total_paths = sum(len(self._get_dotfile_paths(df)) for df in dotfiles)
        processed_paths = 0

        for dotfile in dotfiles:
            app_name = dotfile.get("description", "Unknown")
            paths = self._get_dotfile_paths(dotfile)

            for path_str in paths:
                processed_paths += 1
                if progress_callback and total_paths > 0:
                    progress = int((processed_paths / total_paths) * 100)
                    progress_callback(progress)

                path = self._file_operations.expand_path(path_str)

                if self.matches_ignore_pattern(path, patterns):
                    logger.debug(f"Skipping ignored path: {path}")
                    continue

                if not path.exists():
                    continue

                size_bytes = self._file_operations.calculate_path_size(path)
                total_size_bytes += size_bytes
                total_files += 1

                level = self.categorize_size(size_bytes)
                items_by_level[level] += 1

                if level != "info":
                    size_item: SizeItemDict = {
                        "path": str(path),
                        "size_bytes": size_bytes,
                        "size_mb": size_bytes / BYTES_PER_MB,
                        "level": level,
                        "is_dir": path.is_dir(),
                        "application": app_name,
                    }
                    large_items.append(size_item)

        large_items.sort(key=lambda x: x["size_bytes"], reverse=True)

        report: SizeReportDict = {
            "timestamp": datetime.now(UTC).strftime(TIMESTAMP_FORMAT),
            "total_files": total_files,
            "total_size_bytes": total_size_bytes,
            "total_size_mb": total_size_bytes / BYTES_PER_MB,
            "items_by_level": items_by_level,
            "large_items": large_items,
            "has_critical": items_by_level["critical"] > 0,
            "has_alert": items_by_level["alert"] > 0,
            "has_warning": items_by_level["warning"] > 0,
            "excluded_patterns": patterns,
        }

        logger.info(
            f"Size analysis complete: {total_files} files, "
            f"{report['total_size_mb']:.1f} MB total, "
            f"{len(large_items)} items above warning threshold"
        )

        return report

    def load_ignore_patterns(self, ignore_file: Path) -> list[str]:
        """
        Load exclusion patterns from .dfbuignore file.

        Parses gitignore-style patterns, skipping comments and blank lines.

        Args:
            ignore_file: Path to .dfbuignore file

        Returns:
            List of gitignore-style patterns
        """
        patterns: list[str] = []

        if not ignore_file.exists():
            logger.debug(f"Ignore file not found: {ignore_file}")
            return patterns

        try:
            with Path(ignore_file).open(encoding="utf-8") as f:
                for raw_line in f:
                    stripped = raw_line.strip()
                    if not stripped or stripped.startswith(
                        "#"
                    ):  # skip blank and comment lines
                        continue
                    patterns.append(stripped)

            logger.info(f"Loaded {len(patterns)} patterns from {ignore_file}")
            return patterns

        except OSError as e:
            logger.warning(f"Cannot read ignore file {ignore_file}: {e}")
            return patterns

    def matches_ignore_pattern(self, path: Path, patterns: list[str]) -> bool:
        """
        Check if a path matches any exclusion pattern.

        Supports gitignore-style patterns:
        - **/cache/ matches any cache directory
        - *.log matches any .log file
        - /specific/path matches exact path

        Limitations:
            This is a simplified implementation using fnmatch. It handles
            common patterns from .dfbuignore but has limitations:
            - Negation patterns (starting with !) are not supported
            - Complex patterns like **/cache/**/*.log may not match exactly
              as gitignore would (** is converted to single *)
            - For full gitignore compatibility, consider the 'pathspec' library

        Args:
            path: Path to check
            patterns: List of gitignore-style patterns

        Returns:
            True if path should be excluded, False otherwise
        """
        if not patterns:
            return False

        path_str = str(path)

        for pattern in patterns:
            # CONSTRAINT: ** not natively supported by fnmatch — converted to * (approximate match)
            if "**" in pattern:
                fnmatch_pattern = pattern.replace("**", "*")
                if fnmatch.fnmatch(path_str, fnmatch_pattern):
                    return True
                # directory patterns like **/cache/ — check each path component
                if pattern.endswith("/"):
                    dir_name = pattern.rstrip("/").split("/")[-1]
                    if any(part == dir_name for part in path.parts):
                        return True
            else:
                if fnmatch.fnmatch(path_str, pattern):
                    return True
                if fnmatch.fnmatch(path.name, pattern):
                    return True

        return False

    def categorize_size(self, size_bytes: int) -> str:
        """
        Categorize a size by threshold level.

        Args:
            size_bytes: Size in bytes

        Returns:
            Threshold level: "info", "warning", "alert", or "critical"
        """
        size_mb = size_bytes / BYTES_PER_MB

        if size_mb >= self._critical_threshold_mb:
            return "critical"
        if size_mb >= self._alert_threshold_mb:
            return "alert"
        if size_mb >= self._warning_threshold_mb:
            return "warning"
        return "info"

    def format_report_for_log(self, report: SizeReportDict) -> str:
        """
        Format a size report for display in the log viewer.

        Args:
            report: Size analysis report dictionary

        Returns:
            Human-readable formatted string for log output
        """
        lines: list[str] = []

        lines.append("=" * 60)
        lines.append("BACKUP SIZE ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append("")

        lines.append(f"Timestamp:    {report['timestamp']}")
        lines.append(f"Total Files:  {report['total_files']}")
        lines.append(f"Total Size:   {report['total_size_mb']:.1f} MB")
        lines.append("")

        by_level = report["items_by_level"]
        lines.append("Items by threshold:")
        lines.append(
            f"  Info (<{self._warning_threshold_mb} MB):     {by_level['info']}"
        )
        lines.append(
            f"  Warning ({self._warning_threshold_mb}-{self._alert_threshold_mb} MB):  {by_level['warning']}"
        )
        lines.append(
            f"  Alert ({self._alert_threshold_mb}-{self._critical_threshold_mb} MB):   {by_level['alert']}"
        )
        lines.append(
            f"  Critical (>{self._critical_threshold_mb} MB): {by_level['critical']}"
        )
        lines.append("")

        if report["large_items"]:
            lines.append("-" * 60)
            lines.append("LARGE ITEMS (above warning threshold):")
            lines.append("-" * 60)

            for item in report["large_items"]:
                level_icon = {
                    "warning": "\u26a0\ufe0f",  # Warning sign
                    "alert": "\U0001f536",  # Orange diamond
                    "critical": "\U0001f534",  # Red circle
                }.get(item["level"], "")

                item_type = "DIR" if item["is_dir"] else "FILE"
                lines.append(
                    f"  {level_icon} [{item['level'].upper()}] {item['size_mb']:.1f} MB - "
                    f"{item['path']} ({item_type})"
                )
                lines.append(f"      Application: {item['application']}")

            lines.append("")

        if report["excluded_patterns"]:
            lines.append("-" * 60)
            lines.append("EXCLUDED PATTERNS:")
            lines.append("-" * 60)
            for pattern in report["excluded_patterns"]:
                lines.append(f"  {pattern}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _get_dotfile_paths(self, dotfile: DotFileDict) -> list[str]:
        """
        Extract path list from dotfile dictionary.

        Handles both 'path' (single) and 'paths' (multiple) fields.

        Args:
            dotfile: Dotfile configuration dictionary

        Returns:
            List of path strings
        """
        paths = dotfile.get("paths")  # 'paths': list of strings (current schema)
        if paths:
            return list(paths)

        path = dotfile.get("path")  # 'path': single string (legacy schema)
        if path:
            return [path]

        return []
