"""
DFBU BackupHistoryManager - Backup History Service

Description:
    Tracks backup history for dashboard metrics and analytics.
    Persists history to YAML file with automatic rotation.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.common_types import BackupHistoryEntry, DashboardMetrics
from ruamel.yaml import YAML


class BackupHistoryManager:
    """
    Manages backup history for dashboard analytics.

    Records backup operations and calculates aggregate metrics
    for display in the dashboard view.

    Attributes:
        config_path: Path to configuration directory
        MAX_HISTORY_ENTRIES: Maximum entries to retain (prevents unbounded growth)
    """

    MAX_HISTORY_ENTRIES = 1000  # Limit history to prevent unbounded growth

    def __init__(self, config_path: Path) -> None:
        """
        Initialize BackupHistoryManager.

        Args:
            config_path: Path to configuration directory
        """
        self.config_path: Path = config_path
        self._history: list[BackupHistoryEntry] = []
        self._load_history()

    def _load_history(self) -> None:
        """Load history from YAML file."""
        history_file: Path = self.config_path / "backup_history.yaml"

        if not history_file.exists():
            return

        try:
            yaml = YAML()
            with history_file.open("r", encoding="utf-8") as f:
                data = yaml.load(f)

            if data and "entries" in data:
                # Convert CommentedSeq to list of BackupHistoryEntry
                self._history = [
                    BackupHistoryEntry(
                        timestamp=entry.get("timestamp", ""),
                        profile=entry.get("profile", "Default"),
                        items_backed=entry.get("items_backed", 0),
                        size_bytes=entry.get("size_bytes", 0),
                        duration_seconds=entry.get("duration_seconds", 0.0),
                        success=entry.get("success", False),
                        backup_type=entry.get("backup_type", "mirror"),
                    )
                    for entry in data["entries"]
                ]
        except Exception:
            pass  # CONSTRAINT: Fail open — history load failure is non-fatal; start with empty list

    def _save_history(self) -> None:
        """Save history to YAML file."""
        history_file: Path = self.config_path / "backup_history.yaml"

        try:
            yaml = YAML()
            yaml.default_flow_style = False

            trimmed_history: list[BackupHistoryEntry] = self._history[
                -self.MAX_HISTORY_ENTRIES :
            ]

            entries_data: list[dict[str, str | int | float | bool]] = [
                {
                    "timestamp": entry["timestamp"],
                    "profile": entry["profile"],
                    "items_backed": entry["items_backed"],
                    "size_bytes": entry["size_bytes"],
                    "duration_seconds": entry["duration_seconds"],
                    "success": entry["success"],
                    "backup_type": entry["backup_type"],
                }
                for entry in trimmed_history
            ]

            data: dict[str, Any] = {"entries": entries_data}

            with history_file.open("w", encoding="utf-8") as f:
                yaml.dump(data, f)
        except Exception:
            pass  # CONSTRAINT: Fail open — history save failure is non-fatal; data persists in memory

    def get_entry_count(self) -> int:
        """
        Get number of history entries.

        Returns:
            Number of backup history entries
        """
        return len(self._history)

    def record_backup(
        self,
        items_backed: int,
        size_bytes: int,
        duration_seconds: float,
        success: bool,
        backup_type: str,
        profile: str = "Default",
    ) -> None:
        """
        Record a backup operation.

        Args:
            items_backed: Number of items backed up
            size_bytes: Total size backed up
            duration_seconds: Duration of backup
            success: Whether backup succeeded
            backup_type: Type of backup ("mirror" or "archive")
            profile: Profile name used
        """
        entry = BackupHistoryEntry(
            timestamp=datetime.now(UTC).isoformat(),
            profile=profile,
            items_backed=items_backed,
            size_bytes=size_bytes,
            duration_seconds=duration_seconds,
            success=success,
            backup_type=backup_type,
        )
        self._history.append(entry)
        self._save_history()

    def get_metrics(self) -> DashboardMetrics:
        """
        Calculate dashboard metrics from history.

        Returns:
            DashboardMetrics with aggregate statistics
        """
        total: int = len(self._history)
        successful: int = sum(1 for e in self._history if e["success"])
        failed: int = total - successful

        success_rate: float = successful / total if total > 0 else 0.0
        total_size: int = sum(e["size_bytes"] for e in self._history if e["success"])

        durations: list[float] = [
            e["duration_seconds"] for e in self._history if e["success"]
        ]
        avg_duration: float = sum(durations) / len(durations) if durations else 0.0

        last_timestamp: str | None = (
            self._history[-1]["timestamp"] if self._history else None
        )

        return DashboardMetrics(
            total_backups=total,
            successful_backups=successful,
            failed_backups=failed,
            success_rate=success_rate,
            total_size_backed_bytes=total_size,
            average_duration_seconds=avg_duration,
            last_backup_timestamp=last_timestamp,
        )

    def get_recent_history(self, count: int = 10) -> list[BackupHistoryEntry]:
        """
        Get recent backup history entries.

        Args:
            count: Number of entries to return

        Returns:
            List of recent history entries (newest first)
        """
        return list(reversed(self._history[-count:]))
