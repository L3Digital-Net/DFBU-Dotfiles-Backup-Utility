"""
DFBU ErrorHandler - Structured Error Handling Component

Description:
    Handles error categorization, user-friendly message formatting, and
    structured operation result tracking for backup/restore operations.
    Part of the MVVM architecture following Single Responsibility Principle.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 02-01-2026
Date Changed: 02-01-2026
License: MIT

Features:
    - Error categorization (recoverable, non-recoverable, warnings)
    - User-friendly error message generation
    - Structured operation result tracking
    - Retry eligibility determination
    - Log-friendly result formatting

Requirements:
    - Python 3.14+ for latest typing features
    - Standard library only (no external dependencies)

Classes:
    - ErrorHandler: Manages structured error handling

Functions:
    None
"""

import errno
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Final


sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import OperationResultDict, PathResultDict


RETRYABLE_ERROR_TYPES: Final[frozenset[str]] = frozenset(
    {
        "permission",
        "locked",
        "busy",
        "timeout",
        "temp_failure",
    }
)

NON_RETRYABLE_ERROR_TYPES: Final[frozenset[str]] = frozenset(
    {
        "not_found",
        "invalid_path",
        "disk_full",
        "read_only",
        "config_corrupt",
    }
)

ERRNO_TO_ERROR_TYPE: Final[dict[int, str]] = {
    errno.EACCES: "permission",
    errno.EPERM: "permission",
    errno.ENOENT: "not_found",
    errno.ENOSPC: "disk_full",
    errno.EROFS: "read_only",
    errno.EBUSY: "busy",
    errno.ETXTBSY: "busy",
    errno.EAGAIN: "temp_failure",
    errno.EWOULDBLOCK: "temp_failure",
    errno.EEXIST: "already_exists",
    errno.ENOTDIR: "invalid_path",
    errno.EISDIR: "invalid_path",
    errno.ENAMETOOLONG: "invalid_path",
    errno.ELOOP: "symlink_loop",
    errno.EIO: "io_error",
    errno.EMFILE: "too_many_files",
    errno.ENFILE: "too_many_files",
}

USER_MESSAGE_TEMPLATES: Final[dict[str, str]] = {
    "permission": (
        "Cannot access '{path}' - permission denied. "
        "Check file permissions or run with elevated privileges."
    ),
    "not_found": (
        "File or directory '{path}' no longer exists. "
        "It may have been deleted or moved."
    ),
    "disk_full": (
        "Cannot write to '{path}' - disk is full. "
        "Free up space on the destination drive."
    ),
    "read_only": (
        "Cannot write to '{path}' - filesystem is read-only. "
        "Check if the drive is mounted as read-only."
    ),
    "locked": (
        "File '{path}' is locked by another process. "
        "Close any applications using this file and try again."
    ),
    "busy": (
        "File '{path}' is currently in use. "
        "Wait for the operation to complete or close the application using it."
    ),
    "temp_failure": (
        "Temporary failure accessing '{path}'. "
        "This may resolve if you retry the operation."
    ),
    "already_exists": (
        "'{path}' already exists. The file was not overwritten to prevent data loss."
    ),
    "invalid_path": (
        "'{path}' is not a valid path. "
        "Check that the path is correctly specified in your configuration."
    ),
    "symlink_loop": (
        "'{path}' contains a symbolic link loop. "
        "Check for circular symlinks in the path."
    ),
    "io_error": (
        "I/O error reading or writing '{path}'. "
        "Check the drive for errors or try again."
    ),
    "too_many_files": (
        "Too many files open while processing '{path}'. "
        "Close some applications and try again."
    ),
    "unknown": ("Error processing '{path}': {error}. Check the log for more details."),
}


class ErrorHandler:
    """
    Manages structured error handling for DFBU operations.

    Handles error categorization, user-friendly message formatting, and
    operation result tracking. Provides clean separation between error
    handling logic and business operations.

    Attributes:
        None (stateless)

    Public methods:
        create_path_result: Create structured result for single path operation
        create_operation_result: Create new empty operation result for tracking
        handle_exception: Convert exception to structured PathResultDict
        format_user_message: Format technical error into user-friendly message
        finalize_result: Finalize operation result with status determination
        format_summary_for_log: Format operation result for log display
        get_retryable_paths: Get list of paths that can be retried

    Private methods:
        _categorize_exception: Determine error type from exception
        _is_retryable: Check if error type is potentially recoverable
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
        return PathResultDict(
            path=path,
            dest_path=dest_path,
            status=status,
            error_type=error_type,
            error_message=error_message,
            can_retry=can_retry,
        )

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
        return OperationResultDict(
            status="pending",  # CONSTRAINT: finalize_result() must be called to set final status
            operation_type=operation_type,
            total_items=0,
            completed=[],
            failed=[],
            skipped=[],
            warnings=[],
            can_retry=[],
            timestamp=datetime.now(UTC).isoformat(),
        )

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
        error_type = self._categorize_exception(exception)
        can_retry = self._is_retryable(error_type)
        error_message = self.format_user_message(error_type, path, str(exception))

        return self.create_path_result(
            path=path,
            dest_path=dest_path,
            status="failed",
            error_type=error_type,
            error_message=error_message,
            can_retry=can_retry,
        )

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
        template = USER_MESSAGE_TEMPLATES.get(
            error_type, USER_MESSAGE_TEMPLATES["unknown"]
        )
        return template.format(path=path, error=original_error)

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
        result["total_items"] = (
            len(result["completed"]) + len(result["failed"]) + len(result["skipped"])
        )

        result["can_retry"] = [
            item["path"] for item in result["failed"] if item["can_retry"]
        ]

        if len(result["failed"]) == 0:
            result["status"] = "success"
        elif len(result["completed"]) == 0:
            result["status"] = "failed"
        else:
            result["status"] = "partial"

        return result

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
        lines: list[str] = []

        operation_name = result["operation_type"].replace("_", " ").title()
        status_emoji = {
            "success": "✓",
            "partial": "⚠",
            "failed": "✗",
        }.get(result["status"], "?")

        lines.append(f"{status_emoji} {operation_name} - {result['status'].upper()}")
        lines.append("=" * 50)

        lines.append(f"\nTotal items: {result['total_items']}")
        lines.append(f"  Completed: {len(result['completed'])}")
        lines.append(f"  Failed: {len(result['failed'])}")
        lines.append(f"  Skipped: {len(result['skipped'])}")

        if result["failed"]:
            lines.append("\nFailed Items:")
            for item in result["failed"]:
                retry_note = " [can retry]" if item["can_retry"] else ""
                lines.append(f"  ✗ {item['path']}{retry_note}")
                lines.append(f"    {item['error_message']}")

        if result["skipped"]:
            lines.append("\nSkipped Items:")
            for item in result["skipped"]:
                reason = item["error_message"] or "No changes needed"
                lines.append(f"  ⊘ {item['path']}: {reason}")

        if result["warnings"]:
            lines.append("\nWarnings:")
            for warning in result["warnings"]:
                lines.append(f"  ⚠ {warning}")

        if result["can_retry"]:
            lines.append(f"\n{len(result['can_retry'])} items may succeed if retried.")

        return "\n".join(lines)

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
        return result["can_retry"].copy()

    def _categorize_exception(self, exception: Exception) -> str:
        """
        Determine error type from exception.

        Args:
            exception: The exception to categorize

        Returns:
            Error type string
        """
        if isinstance(exception, PermissionError):
            return "permission"

        if isinstance(exception, FileNotFoundError):
            return "not_found"

        if isinstance(exception, FileExistsError):
            return "already_exists"

        if isinstance(exception, IsADirectoryError):
            return "invalid_path"

        if isinstance(exception, NotADirectoryError):
            return "invalid_path"

        # CONSTRAINT: OSError checked last — subclasses (PermissionError, etc.) matched above first
        if isinstance(exception, OSError) and exception.errno:
            return ERRNO_TO_ERROR_TYPE.get(exception.errno, "unknown")

        return "unknown"

    def _is_retryable(self, error_type: str) -> bool:
        """
        Check if error type is potentially recoverable with retry.

        Args:
            error_type: Error category to check

        Returns:
            True if the error might resolve on retry
        """
        return error_type in RETRYABLE_ERROR_TYPES
