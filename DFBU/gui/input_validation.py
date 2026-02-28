"""
DFBU Input Validation Module

Description:
    Centralized input validation for DFBU GUI application.
    Provides validators for dialog fields, settings, file paths,
    and configuration data.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-03-2025
Date Changed: 11-03-2025
License: MIT

Features:
    - Path validation and sanitization
    - String input validation (length, characters)
    - Numeric range validation
    - Boolean validation
    - Type-safe validation with error messages

Requirements:
    - Python 3.14+ for latest language features
    - pathlib for path operations

Classes:
    - ValidationResult: Result of validation with success/error message
    - InputValidator: Static methods for input validation
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final


MAX_PATH_LENGTH: Final[int] = 4096  # Linux PATH_MAX
MAX_STRING_LENGTH: Final[int] = 256  # Maximum string field length
MIN_STRING_LENGTH: Final[int] = 1  # Minimum string field length

VALID_FILENAME_PATTERN: Final[str] = (
    r'^[^<>:"/\\|?*\x00-\x1f]+$'  # No illegal filename chars
)
VALID_PATH_CHARS: Final[str] = r"^[a-zA-Z0-9_./ \-~]+$"  # Allow tilde for home dir


@dataclass
class ValidationResult:
    """
    Result of validation operation.

    Attributes:
        success: Whether validation passed
        error_message: Error message if validation failed (empty if success)
        sanitized_value: Sanitized/normalized value if applicable
    """

    success: bool
    error_message: str = ""
    sanitized_value: str | None = None


class InputValidator:
    """
    Static methods for input validation.

    Provides validation for various input types with clear error messages.
    """

    @staticmethod
    def validate_path(path_str: str, must_exist: bool = False) -> ValidationResult:
        """
        Validate file or directory path string.

        Args:
            path_str: Path string to validate
            must_exist: Whether path must exist on filesystem

        Returns:
            ValidationResult with success status and error message
        """
        if not path_str or not path_str.strip():
            return ValidationResult(False, "Path cannot be empty")

        if len(path_str) > MAX_PATH_LENGTH:
            return ValidationResult(
                False, f"Path exceeds maximum length ({MAX_PATH_LENGTH} characters)"
            )

        # CONSTRAINT: Null bytes are a path injection vector — reject before any filesystem call
        if "\x00" in path_str:
            return ValidationResult(False, "Path contains invalid null bytes")

        try:
            path = Path(path_str).expanduser()
        except (ValueError, RuntimeError) as e:
            return ValidationResult(False, f"Invalid path format: {e}")

        if must_exist and not path.exists():
            return ValidationResult(False, f"Path does not exist: {path_str}")

        try:
            sanitized = str(path.expanduser())
        except Exception as e:
            return ValidationResult(False, f"Could not sanitize path: {e}")

        return ValidationResult(True, "", sanitized)

    @staticmethod
    def validate_string(
        value: str,
        field_name: str = "Field",
        min_length: int = MIN_STRING_LENGTH,
        max_length: int = MAX_STRING_LENGTH,
        allow_empty: bool = False,
    ) -> ValidationResult:
        """
        Validate string input.

        Args:
            value: String value to validate
            field_name: Name of field for error messages
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            allow_empty: Whether empty strings are allowed

        Returns:
            ValidationResult with success status and error message
        """
        if not value or not value.strip():
            if allow_empty:
                return ValidationResult(True, "", "")
            return ValidationResult(False, f"{field_name} cannot be empty")

        value_stripped = value.strip()

        if len(value_stripped) < min_length:
            return ValidationResult(
                False, f"{field_name} must be at least {min_length} characters"
            )

        if len(value_stripped) > max_length:
            return ValidationResult(
                False, f"{field_name} exceeds maximum length ({max_length} characters)"
            )

        # CONSTRAINT: Control chars (ord < 32) are input sanitization bypass vector — reject
        if any(ord(c) < 32 for c in value_stripped):
            return ValidationResult(
                False, f"{field_name} contains invalid control characters"
            )

        return ValidationResult(True, "", value_stripped)

    @staticmethod
    def validate_integer(
        value: int | str,
        field_name: str = "Value",
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> ValidationResult:
        """
        Validate integer input.

        Args:
            value: Integer value or string representation
            field_name: Name of field for error messages
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)

        Returns:
            ValidationResult with success status and error message
        """
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return ValidationResult(False, f"{field_name} must be a valid integer")

        if min_value is not None and value < min_value:
            return ValidationResult(False, f"{field_name} must be at least {min_value}")

        if max_value is not None and value > max_value:
            return ValidationResult(False, f"{field_name} must be at most {max_value}")

        return ValidationResult(True, "", str(value))

    @staticmethod
    def validate_boolean(
        value: bool | str, field_name: str = "Value"
    ) -> ValidationResult:
        """
        Validate boolean input.

        Args:
            value: Boolean value or string representation
            field_name: Name of field for error messages

        Returns:
            ValidationResult with success status and error message
        """
        if isinstance(value, bool):
            return ValidationResult(True, "", str(value).lower())

        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ("true", "1", "yes", "on"):
                return ValidationResult(True, "", "true")
            if value_lower in ("false", "0", "no", "off"):
                return ValidationResult(True, "", "false")

        return ValidationResult(False, f"{field_name} must be a valid boolean value")

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing/replacing illegal characters.

        Args:
            filename: Filename to sanitize

        Returns:
            Sanitized filename safe for filesystem use
        """
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename)
        sanitized = sanitized.strip(". ")

        # CONSTRAINT: Empty after sanitization means all chars were illegal — use safe default
        if not sanitized:
            sanitized = "unnamed_file"

        if len(sanitized) > 255:  # 255 = NAME_MAX on most Linux filesystems
            sanitized = sanitized[:255]

        return sanitized

    @staticmethod
    def validate_archive_compression_level(level: int | str) -> ValidationResult:
        """
        Validate archive compression level (0-9).

        Args:
            level: Compression level to validate

        Returns:
            ValidationResult with success status and error message
        """
        return InputValidator.validate_integer(
            level, "Compression level", min_value=0, max_value=9
        )

    @staticmethod
    def validate_max_archives(count: int | str) -> ValidationResult:
        """
        Validate max archives count (1-100).

        Args:
            count: Max archives count to validate

        Returns:
            ValidationResult with success status and error message
        """
        return InputValidator.validate_integer(
            count, "Max archives", min_value=1, max_value=100
        )
