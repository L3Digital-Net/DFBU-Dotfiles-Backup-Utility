"""
DFBU PreviewGenerator - Backup Preview Service

Description:
    Generates preview of what would be backed up without actually
    performing the backup. Shows new, changed, and unchanged files.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from core.common_types import BackupPreviewDict, PreviewItemDict

from gui.file_operations import FileOperations


class PreviewGenerator:
    """
    Generates backup preview without performing actual backup.

    Analyzes source files and compares with existing backup to
    determine what would be copied (new/changed) or skipped (unchanged).
    """

    def __init__(
        self,
        file_ops: FileOperations,
        mirror_base_dir: Path,
    ) -> None:
        """
        Initialize PreviewGenerator.

        Args:
            file_ops: FileOperations instance for file comparison
            mirror_base_dir: Base directory for mirror backups
        """
        self._file_ops = file_ops
        self._mirror_base_dir = mirror_base_dir

    def generate_preview(
        self,
        dotfiles: list[dict[str, Any]],
        hostname_subdir: bool,
        date_subdir: bool,
        progress_callback: Callable[[int], None] | None = None,
    ) -> BackupPreviewDict:
        """
        Generate preview of backup operation.

        Args:
            dotfiles: List of dotfile configurations
            hostname_subdir: Whether to use hostname subdirectory
            date_subdir: Whether to use date subdirectory
            progress_callback: Optional callback for progress (0-100)

        Returns:
            BackupPreviewDict with preview results
        """
        items: list[PreviewItemDict] = []
        total_size = 0
        new_count = 0
        changed_count = 0
        unchanged_count = 0
        error_count = 0

        total_paths = sum(
            len(df.get("paths", [])) for df in dotfiles if df.get("enabled", True)
        )
        processed = 0

        for dotfile in dotfiles:
            if not dotfile.get("enabled", True):
                continue

            app_name = dotfile.get("application", "Unknown")

            for path_str in dotfile.get("paths", []):
                if not path_str:  # skip empty entries — can occur with malformed config
                    continue

                src_path = self._file_ops.expand_path(path_str)

                if not src_path.exists():
                    processed += 1
                    if progress_callback and total_paths > 0:
                        progress_callback(int((processed / total_paths) * 100))
                    continue

                dest_path = self._file_ops.assemble_dest_path(
                    self._mirror_base_dir,
                    src_path,
                    hostname_subdir,
                    date_subdir,
                )

                if src_path.is_file():
                    item = self._preview_file(src_path, dest_path, app_name)
                    items.append(item)
                    total_size += item["size_bytes"]
                    new_count, changed_count, unchanged_count, error_count = (
                        self._update_status_counts(
                            item, new_count, changed_count, unchanged_count, error_count
                        )
                    )

                elif src_path.is_dir():
                    for file_path in src_path.rglob("*"):
                        if file_path.is_file():
                            rel_path = file_path.relative_to(src_path)
                            file_dest = dest_path / rel_path

                            item = self._preview_file(file_path, file_dest, app_name)
                            items.append(item)
                            total_size += item["size_bytes"]
                            new_count, changed_count, unchanged_count, error_count = (
                                self._update_status_counts(
                                    item,
                                    new_count,
                                    changed_count,
                                    unchanged_count,
                                    error_count,
                                )
                            )

                processed += 1
                if progress_callback and total_paths > 0:
                    progress_callback(int((processed / total_paths) * 100))

        return BackupPreviewDict(
            items=items,
            total_size_bytes=total_size,
            new_count=new_count,
            changed_count=changed_count,
            unchanged_count=unchanged_count,
            error_count=error_count,
        )

    def _update_status_counts(
        self,
        item: PreviewItemDict,
        new_count: int,
        changed_count: int,
        unchanged_count: int,
        error_count: int,
    ) -> tuple[int, int, int, int]:
        """
        Update status counts based on item status.

        Args:
            item: The preview item to check
            new_count: Current count of new files
            changed_count: Current count of changed files
            unchanged_count: Current count of unchanged files
            error_count: Current count of error files

        Returns:
            Tuple of (new_count, changed_count, unchanged_count, error_count)
        """
        if item["status"] == "new":
            return new_count + 1, changed_count, unchanged_count, error_count
        if item["status"] == "changed":
            return new_count, changed_count + 1, unchanged_count, error_count
        if item["status"] == "unchanged":
            return new_count, changed_count, unchanged_count + 1, error_count
        return new_count, changed_count, unchanged_count, error_count + 1

    def _preview_file(
        self, src_path: Path, dest_path: Path, app_name: str
    ) -> PreviewItemDict:
        """
        Preview a single file.

        Args:
            src_path: Source file path
            dest_path: Destination file path
            app_name: Application name for the dotfile

        Returns:
            PreviewItemDict with file preview info
        """
        try:
            size = src_path.stat().st_size

            if not dest_path.exists():
                status = "new"
            elif self._file_ops.files_are_identical(src_path, dest_path):
                status = "unchanged"
            else:
                status = "changed"

            return PreviewItemDict(
                path=str(src_path),
                dest_path=str(dest_path),
                size_bytes=size,
                status=status,
                application=app_name,
            )

        except OSError, PermissionError:
            return PreviewItemDict(  # CONSTRAINT: OSError expected for protected files — return error status, not raise
                path=str(src_path),
                dest_path=str(dest_path),
                size_bytes=0,
                status="error",
                application=app_name,
            )
