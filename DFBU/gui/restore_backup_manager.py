#!/usr/bin/env python3
"""
DFBU RestoreBackupManager - Pre-Restore Safety Component

Description:
    Manages automatic backups of files before restore operations, preventing
    data loss if a restore goes wrong. Creates timestamped backup directories
    with TOML manifests tracking what was backed up and why.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 2026-01-31
Date Changed: 02-01-2026
License: MIT

Features:
    - Automatic backup before restore operations
    - TOML manifest with backup metadata
    - Configurable retention policy (default: 5 backups)
    - Directory structure preservation
    - Cleanup of old backups

Requirements:
    - Linux environment
    - Python 3.14+ for Path.copy() with metadata preservation
    - tomli_w for TOML writing
    - No Qt dependencies (pure model layer)

Classes:
    - RestoreBackupManager: Manages pre-restore backup operations
"""

import logging
import shutil
import socket
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

import tomli_w


logger = logging.getLogger(__name__)


DEFAULT_BACKUP_DIR: Final[Path] = (
    Path.home() / ".local" / "share" / "dfbu" / "restore-backups"
)
DEFAULT_MAX_BACKUPS: Final[int] = 5
BACKUP_TIMESTAMP_FORMAT: Final[str] = "%Y-%m-%d_%H%M%S"


class RestoreBackupManager:
    """
    Manages pre-restore backup operations for data safety.

    Creates timestamped backups of files before they are overwritten during
    restore operations. Maintains TOML manifests documenting what was backed
    up and enforces retention policies to limit disk usage.

    Attributes:
        backup_base_dir: Base directory for all restore backups
        max_backups: Maximum number of backups to retain

    Public methods:
        backup_before_restore: Create backup of files before restore
        get_backup_count: Get number of existing backups
        cleanup_old_backups: Remove backups exceeding retention limit
        list_backups: List all backups with timestamps
    """

    def __init__(
        self,
        backup_base_dir: Path | None = None,
        max_backups: int = DEFAULT_MAX_BACKUPS,
        home_dir: Path | None = None,
    ) -> None:
        """
        Initialize RestoreBackupManager.

        Args:
            backup_base_dir: Base directory for backups (default: ~/.local/share/dfbu/restore-backups)
            max_backups: Maximum backups to retain (default: 5)
            home_dir: Home directory for relative path calculation (default: Path.home())
        """
        self._backup_base_dir = backup_base_dir or DEFAULT_BACKUP_DIR
        self._max_backups = max_backups
        self._home_dir = home_dir or Path.home()

    @property
    def backup_base_dir(self) -> Path:
        """Get base directory for restore backups."""
        return self._backup_base_dir

    @backup_base_dir.setter
    def backup_base_dir(self, path: Path) -> None:
        """Set base directory for restore backups."""
        self._backup_base_dir = path

    @property
    def max_backups(self) -> int:
        """Get maximum number of restore backups to retain."""
        return self._max_backups

    @max_backups.setter
    def max_backups(self, value: int) -> None:
        """Set maximum number of restore backups to retain."""
        self._max_backups = value

    def get_backup_count(self) -> int:
        """
        Get number of existing restore backups.

        Returns:
            Number of backup directories in backup_base_dir
        """
        if not self._backup_base_dir.exists():
            return 0
        return len([d for d in self._backup_base_dir.iterdir() if d.is_dir()])

    def list_backups(self) -> list[tuple[Path, str]]:
        """
        List all restore backups with their timestamps.

        Returns:
            List of (backup_path, timestamp_str) tuples, newest first
        """
        if not self._backup_base_dir.exists():
            return []

        backup_dirs = [d for d in self._backup_base_dir.iterdir() if d.is_dir()]
        # Sort by directory name (timestamp format ensures correct ordering)
        backup_dirs.sort(key=lambda d: d.name, reverse=True)

        return [(d, d.name) for d in backup_dirs]

    def cleanup_old_backups(self) -> list[Path]:
        """
        Remove oldest backups exceeding max_backups limit.

        Returns:
            List of removed backup directory paths
        """
        if not self._backup_base_dir.exists():
            return []

        backup_dirs = [d for d in self._backup_base_dir.iterdir() if d.is_dir()]
        backup_dirs.sort(key=lambda d: d.name)  # Oldest first

        removed: list[Path] = []
        while len(backup_dirs) > self._max_backups:
            oldest = backup_dirs.pop(0)
            try:
                shutil.rmtree(oldest)
                removed.append(oldest)
                logger.info(f"Removed old restore backup: {oldest}")
            except OSError as e:
                logger.error(f"Failed to remove backup {oldest}: {e}")

        return removed

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
        if not files_to_overwrite:
            return True, "", None

        existing_paths = [f for f in files_to_overwrite if f.exists()]
        if not existing_paths:
            return True, "", None

        timestamp = datetime.now(UTC).strftime(BACKUP_TIMESTAMP_FORMAT)
        backup_dir = self._backup_base_dir / timestamp

        try:
            backup_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            # Extremely unlikely - add microseconds to make unique
            timestamp = f"{timestamp}_{datetime.now(UTC).microsecond:06d}"
            backup_dir = self._backup_base_dir / timestamp
            backup_dir.mkdir(parents=True)
        except OSError as e:
            return False, f"Failed to create backup directory: {e}", None

        logger.info(f"Created pre-restore backup directory: {backup_dir}")

        backed_up_files: list[dict[str, str | int]] = []

        for src_path in existing_paths:
            try:
                try:
                    rel_path = src_path.relative_to(self._home_dir)
                except ValueError:
                    # Path not under home - use just the name
                    rel_path = Path(src_path.name)

                dest_path = backup_dir / rel_path

                if src_path.is_dir():
                    shutil.copytree(src_path, dest_path)
                    logger.debug(f"Backed up directory: {src_path} -> {dest_path}")
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    logger.debug(f"Backed up file: {src_path} -> {dest_path}")

                backed_up_files.append(
                    {
                        "original_path": str(src_path),
                        "backup_path": str(rel_path),
                        "size_bytes": src_path.stat().st_size
                        if src_path.is_file()
                        else 0,
                    }
                )

            except OSError as e:
                logger.error(f"Failed to backup {src_path}: {e}")
                # Continue with other files even if one fails

        manifest = {
            "restore_operation": {
                "timestamp": datetime.now(UTC).isoformat(),
                "source_backup": source_backup_path,
                "hostname": socket.gethostname(),
                "file_count": len(backed_up_files),
            },
            "backed_up_files": backed_up_files,
        }

        manifest_path = backup_dir / "manifest.toml"
        try:
            with open(manifest_path, "wb") as f:
                tomli_w.dump(manifest, f)
            logger.info(f"Created backup manifest: {manifest_path}")
        except OSError as e:
            logger.error(f"Failed to write manifest: {e}")
            # Backup still succeeded even if manifest failed

        return True, "", backup_dir
