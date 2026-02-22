#!/usr/bin/env python3
"""
DFBU VerificationManager - Backup Verification Component

Description:
    Verifies integrity of backup files by comparing against source files.
    Supports size verification and optional SHA-256 hash comparison.
    Generates reports for display in the log viewer.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 2026-02-01
Date Changed: 02-01-2026
License: MIT

Features:
    - Size verification (fast, catches truncation)
    - SHA-256 hash verification (thorough, catches corruption)
    - Structured verification reports
    - Human-readable log output formatting

Requirements:
    - Linux environment
    - Python 3.14+
    - No Qt dependencies (pure model layer)

Classes:
    - VerificationManager: Manages backup verification operations
"""

import hashlib
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Final


sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import VerificationReportDict, VerificationResultDict


logger = logging.getLogger(__name__)

HASH_CHUNK_SIZE: Final[int] = (
    65536  # 64KB chunks — balances memory use vs read overhead
)
TIMESTAMP_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S"


class VerificationManager:
    """
    Manages backup verification operations for data integrity.

    Compares backup files against source files to verify successful backup.
    Supports both fast size verification and thorough hash verification.
    Generates formatted reports for display in the application log viewer.

    Attributes:
        hash_verification_enabled: Whether to perform SHA-256 hash comparison

    Public methods:
        verify_backup: Verify all files in a backup
        verify_file: Verify a single file's integrity
        format_report_for_log: Format report for log viewer display
    """

    def __init__(self, hash_verification_enabled: bool = False) -> None:
        """
        Initialize VerificationManager.

        Args:
            hash_verification_enabled: Enable SHA-256 hash verification (default: False)
        """
        self._hash_verification_enabled = hash_verification_enabled

    @property
    def hash_verification_enabled(self) -> bool:
        """Get whether SHA-256 hash verification is enabled."""
        return self._hash_verification_enabled

    @hash_verification_enabled.setter
    def hash_verification_enabled(self, value: bool) -> None:
        """Set whether SHA-256 hash verification is enabled."""
        self._hash_verification_enabled = value

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
            source_paths: List of (source_path, backup_file_path) tuples to verify
            backup_type: Type of backup ("mirror" or "archive")

        Returns:
            VerificationReportDict with verification results
        """
        results: list[VerificationResultDict] = []
        verified_ok = 0
        verified_failed = 0

        for source_path, backup_file_path in source_paths:
            result = self._verify_single_file(source_path, backup_file_path)
            results.append(result)

            if result["status"] == "ok":
                verified_ok += 1
            else:
                verified_failed += 1

        report: VerificationReportDict = {
            "timestamp": datetime.now(UTC).strftime(TIMESTAMP_FORMAT),
            "backup_type": backup_type,
            "backup_path": str(backup_path),
            "total_files": len(source_paths),
            "verified_ok": verified_ok,
            "verified_failed": verified_failed,
            "hash_verified": self._hash_verification_enabled,
            "results": results,
        }

        logger.info(
            f"Verification complete: {verified_ok}/{len(source_paths)} files OK, "
            f"{verified_failed} failed"
        )

        return report

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
        if not backup_path.exists():
            return False, None, "Backup file missing"

        if not source_path.exists():
            return False, None, "Source file no longer exists"

        try:
            source_size = source_path.stat().st_size
            backup_size = backup_path.stat().st_size
            size_match = source_size == backup_size
        except OSError as e:
            return False, None, f"Cannot read file stats: {e}"

        if not size_match:
            return False, None, ""

        hash_match: bool | None = None
        if self._hash_verification_enabled:
            try:
                source_hash = self._calculate_hash(source_path)
                backup_hash = self._calculate_hash(backup_path)
                hash_match = source_hash == backup_hash
            except OSError as e:
                return size_match, None, f"Hash calculation failed: {e}"

        return size_match, hash_match, ""

    def format_report_for_log(self, report: VerificationReportDict) -> str:
        """
        Format a verification report for display in the log viewer.

        Args:
            report: Verification report dictionary

        Returns:
            Human-readable formatted string for log output
        """
        lines: list[str] = []

        lines.append("=" * 60)
        lines.append("BACKUP VERIFICATION REPORT")
        lines.append("=" * 60)
        lines.append("")

        lines.append(f"Timestamp:    {report['timestamp']}")
        lines.append(f"Backup Type:  {report['backup_type']}")
        lines.append(f"Backup Path:  {report['backup_path']}")
        lines.append(
            f"Hash Check:   {'Enabled' if report['hash_verified'] else 'Disabled'}"
        )
        lines.append("")

        total = report["total_files"]
        ok = report["verified_ok"]
        failed = report["verified_failed"]

        if failed == 0:
            lines.append(f"✓ All {total} files verified successfully")
        else:
            lines.append(f"✓ {ok} files verified OK")
            lines.append(f"✗ {failed} files FAILED verification")

        lines.append("")

        failed_results = [r for r in report["results"] if r["status"] != "ok"]
        if failed_results:
            lines.append("-" * 60)
            lines.append("FAILED FILES:")
            lines.append("-" * 60)

            for result in failed_results:
                lines.append(f"  {result['path']}")
                lines.append(f"    Status: {result['status']}")

                if result["status"] == "size_mismatch":
                    lines.append(
                        f"    Expected: {result['expected_size']} bytes, "
                        f"Actual: {result['actual_size']} bytes"
                    )
                elif result["status"] == "hash_mismatch":
                    lines.append("    File content differs (hash mismatch)")
                elif result["error"]:
                    lines.append(f"    Error: {result['error']}")

                lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _verify_single_file(
        self,
        source_path: Path,
        backup_path: Path,
    ) -> VerificationResultDict:
        """
        Verify a single file and return structured result.

        Args:
            source_path: Original source file path
            backup_path: File path in the backup

        Returns:
            VerificationResultDict with verification details
        """
        result: VerificationResultDict = {
            "path": str(source_path),
            "backup_path": str(backup_path),
            "status": "ok",
            "size_match": False,
            "hash_match": None,
            "expected_size": 0,
            "actual_size": None,
            "error": "",
        }

        if not backup_path.exists():
            result["status"] = "missing"
            result["error"] = "Backup file does not exist"
            logger.warning(f"Verification failed: {backup_path} missing")
            return result

        if not source_path.exists():
            result["status"] = "error"
            result["error"] = "Source file no longer exists for comparison"
            logger.warning(f"Verification skipped: {source_path} no longer exists")
            return result

        try:
            source_size = source_path.stat().st_size
            backup_size = backup_path.stat().st_size
            result["expected_size"] = source_size
            result["actual_size"] = backup_size
        except OSError as e:
            result["status"] = "error"
            result["error"] = f"Cannot read file stats: {e}"
            logger.error(f"Verification error for {source_path}: {e}")
            return result

        result["size_match"] = source_size == backup_size
        if not result["size_match"]:
            result["status"] = "size_mismatch"
            logger.warning(
                f"Size mismatch: {source_path} ({source_size} bytes) vs "
                f"{backup_path} ({backup_size} bytes)"
            )
            return result

        if self._hash_verification_enabled:
            try:
                source_hash = self._calculate_hash(source_path)
                backup_hash = self._calculate_hash(backup_path)
                result["hash_match"] = source_hash == backup_hash

                if not result["hash_match"]:
                    result["status"] = "hash_mismatch"
                    logger.warning(f"Hash mismatch: {source_path}")
                    return result

            except OSError as e:
                result["status"] = "error"
                result["error"] = f"Hash calculation failed: {e}"
                logger.error(f"Hash calculation error for {source_path}: {e}")
                return result

        logger.debug(f"Verification OK: {source_path}")
        return result

    def _calculate_hash(self, file_path: Path) -> str:
        """
        Calculate SHA-256 hash of a file.

        Args:
            file_path: Path to file to hash

        Returns:
            Hex digest of SHA-256 hash

        Raises:
            OSError: If file cannot be read
        """
        sha256_hash = hashlib.sha256()
        with Path(file_path).open("rb") as f:
            for chunk in iter(lambda: f.read(HASH_CHUNK_SIZE), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
