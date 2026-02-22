#!/usr/bin/env python3
"""
DFBU YAML Configuration Loader Module

Description:
    Handles loading and saving YAML configuration files for DFBU.
    Supports three separate configuration files: settings.yaml,
    dotfiles.yaml, and session.yaml.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 02-01-2026
Date Changed: 02-01-2026
License: MIT

Features:
    - Load and save settings configuration (paths and options)
    - Load and save dotfiles library (application configurations)
    - Load and save session state (exclusions)
    - Uses ruamel.yaml for round-trip safe YAML handling
    - Preserves comments in YAML files
    - Validation of configuration structure

Requirements:
    - Python 3.14+ for latest language features
    - ruamel.yaml for YAML handling
    - common_types module for TypedDict definitions

Classes:
    - YAMLConfigLoader: Load and save YAML configuration files
"""

import logging
import re
from io import StringIO
from pathlib import Path
from typing import Any

from core.common_types import (
    DotFileDict,
    SessionDict,
    SettingsDict,
)
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError


logger = logging.getLogger(__name__)


class YAMLConfigLoader:
    """
    Load and save YAML configuration files for DFBU.

    Handles three separate configuration files:
    - settings.yaml: Backup paths and options
    - dotfiles.yaml: Dotfile library definitions
    - session.yaml: Session-specific exclusions

    Uses ruamel.yaml for round-trip safe YAML handling that preserves
    comments and formatting when modifying files.

    Args:
        config_dir: Directory containing configuration files (Path or str)

    Properties:
        settings_path: Path to settings.yaml
        dotfiles_path: Path to dotfiles.yaml
        session_path: Path to session.yaml

    Methods:
        load_settings: Load settings from YAML file
        load_dotfiles: Load dotfiles library from YAML file
        load_session: Load session exclusions from YAML file
        save_settings: Save settings to YAML file
        save_dotfiles: Save dotfiles library to YAML file
        save_session: Save session exclusions to YAML file
    """

    def __init__(self, config_dir: Path | str) -> None:
        """
        Initialize YAMLConfigLoader with configuration directory.

        Args:
            config_dir: Directory containing configuration files
        """
        self._config_dir = Path(config_dir)
        self._yaml = YAML()
        self._yaml.preserve_quotes = True
        self._yaml.default_flow_style = False

    @property
    def settings_path(self) -> Path:
        """Path to settings.yaml configuration file."""
        return self._config_dir / "settings.yaml"

    @property
    def dotfiles_path(self) -> Path:
        """Path to dotfiles.yaml configuration file."""
        return self._config_dir / "dotfiles.yaml"

    @property
    def session_path(self) -> Path:
        """Path to session.yaml configuration file."""
        return self._config_dir / "session.yaml"

    def load_settings(self) -> SettingsDict:
        """
        Load settings from settings.yaml file.

        Returns:
            SettingsDict containing paths and options configuration

        Raises:
            FileNotFoundError: If settings.yaml does not exist
            ValueError: If settings file has invalid structure
        """
        if not self.settings_path.exists():
            raise FileNotFoundError(f"Settings file not found: {self.settings_path}")

        with self.settings_path.open("r", encoding="utf-8") as f:
            data: Any = self._yaml.load(f)  # pyright: ignore[reportUnknownMemberType]

        if data is None:
            raise ValueError("Settings file is empty")

        self._validate_settings(data)

        return data  # type: ignore[no-any-return]  # ruamel.yaml returns Any

    def load_dotfiles(self) -> dict[str, DotFileDict]:
        """
        Load dotfiles library from dotfiles.yaml file.

        Handles duplicate keys gracefully by merging entries with the same
        application name. Also validates and cleans entries for common issues
        like empty paths, missing descriptions, and duplicate paths within
        a single entry.

        Returns:
            Dictionary mapping application names to DotFileDict entries

        Raises:
            FileNotFoundError: If dotfiles.yaml does not exist
        """
        if not self.dotfiles_path.exists():
            raise FileNotFoundError(f"Dotfiles file not found: {self.dotfiles_path}")

        try:
            with self.dotfiles_path.open("r", encoding="utf-8") as f:
                data: Any = self._yaml.load(f)  # pyright: ignore[reportUnknownMemberType]
        except DuplicateKeyError as e:
            logger.warning(
                "Duplicate keys found in dotfiles.yaml, attempting repair: %s", e
            )
            data = self._repair_duplicate_dotfiles()

        if data is None:
            return {}

        result = dict(data)
        return self._validate_and_clean_dotfiles(result)

    def load_session(self) -> SessionDict:
        """
        Load session exclusions from session.yaml file.

        Returns empty session if file does not exist.

        Returns:
            SessionDict containing excluded application list
        """
        if not self.session_path.exists():
            return {"excluded": []}

        with self.session_path.open("r", encoding="utf-8") as f:
            data: Any = self._yaml.load(f)  # pyright: ignore[reportUnknownMemberType]

        if data is None:
            return {"excluded": []}

        excluded_raw = data.get("excluded", [])
        if excluded_raw is None:
            excluded_raw = []

        excluded: list[str] = []
        if isinstance(excluded_raw, list):
            for item in excluded_raw:  # pyright: ignore[reportUnknownVariableType]
                if isinstance(item, str):
                    excluded.append(item)
                else:
                    excluded.append(str(item))  # pyright: ignore[reportUnknownArgumentType]

        return {"excluded": excluded}

    def save_settings(self, settings: SettingsDict) -> None:
        """
        Save settings to settings.yaml file.

        Args:
            settings: SettingsDict containing paths and options configuration
        """
        self._config_dir.mkdir(parents=True, exist_ok=True)

        with self.settings_path.open("w", encoding="utf-8") as f:
            self._yaml.dump(dict(settings), f)  # pyright: ignore[reportUnknownMemberType]

    def save_dotfiles(self, dotfiles: dict[str, DotFileDict]) -> None:
        """
        Save dotfiles library to dotfiles.yaml file.

        Args:
            dotfiles: Dictionary mapping application names to DotFileDict entries
        """
        self._config_dir.mkdir(parents=True, exist_ok=True)

        with self.dotfiles_path.open("w", encoding="utf-8") as f:
            self._yaml.dump(dict(dotfiles), f)  # pyright: ignore[reportUnknownMemberType]

    def save_session(self, session: SessionDict) -> None:
        """
        Save session exclusions to session.yaml file.

        Args:
            session: SessionDict containing excluded application list
        """
        self._config_dir.mkdir(parents=True, exist_ok=True)

        with self.session_path.open("w", encoding="utf-8") as f:
            self._yaml.dump(dict(session), f)  # pyright: ignore[reportUnknownMemberType]

    # =========================================================================
    # Dotfiles Validation and Repair
    # =========================================================================

    def _repair_duplicate_dotfiles(self) -> dict[str, Any]:
        """
        Repair dotfiles.yaml by merging duplicate top-level keys.

        Scans the raw YAML file to extract all top-level entries (including
        duplicates), merges entries with the same key by combining their paths
        and keeping the most detailed description, then saves the cleaned file.

        Returns:
            Merged dictionary of dotfile entries
        """
        content = self.dotfiles_path.read_text(encoding="utf-8")
        all_entries = self._extract_all_toplevel_entries(content)

        grouped: dict[str, list[dict[str, Any]]] = {}
        for key, entry_data in all_entries:
            grouped.setdefault(key, []).append(entry_data)

        merged: dict[str, DotFileDict] = {}
        duplicates_found: list[str] = []

        for key, entries in grouped.items():
            if len(entries) == 1:
                merged[key] = entries[0]  # type: ignore[assignment]
            else:
                merged[key] = self._merge_dotfile_entries(key, entries)
                duplicates_found.append(key)

        if duplicates_found:
            logger.warning(
                "Merged %d duplicate dotfile entries: %s",
                len(duplicates_found),
                ", ".join(duplicates_found),
            )
            # SIDE-EFFECT: Overwrites dotfiles.yaml with de-duplicated content in-place
            self.save_dotfiles(merged)
            logger.info("Saved de-duplicated dotfiles.yaml")

        return merged

    def _extract_all_toplevel_entries(
        self, content: str
    ) -> list[tuple[str, dict[str, Any]]]:
        """
        Extract all top-level YAML entries from raw content, preserving duplicates.

        Splits the file at top-level key boundaries (lines starting with a
        non-whitespace character followed by a colon) and parses each entry
        individually.

        Args:
            content: Raw YAML file content

        Returns:
            List of (key_name, parsed_data) tuples, one per occurrence
        """
        entries: list[tuple[str, dict[str, Any]]] = []
        lines = content.split("\n")

        # CONSTRAINT: Top-level key = non-blank, non-comment line with no leading whitespace containing a colon
        toplevel_pattern = re.compile(r"^([^\s#][^:]*):(.*)$")
        boundaries: list[tuple[int, str]] = []

        for i, line in enumerate(lines):
            match = toplevel_pattern.match(line)
            if match:
                key = match.group(1).strip()
                boundaries.append((i, key))

        yaml_parser = YAML()
        yaml_parser.preserve_quotes = True
        yaml_parser.allow_duplicate_keys = True

        for idx, (start_line, key) in enumerate(boundaries):
            if idx + 1 < len(boundaries):  # end = next entry start; else EOF
                end_line = boundaries[idx + 1][0]
            else:
                end_line = len(lines)

            block_lines = lines[start_line:end_line]

            # CONSTRAINT: Strip trailing blanks/comments — ruamel fails to parse inter-entry whitespace
            while block_lines and (
                not block_lines[-1].strip() or block_lines[-1].strip().startswith("#")
            ):
                block_lines.pop()

            if not block_lines:
                continue

            block_content = "\n".join(block_lines) + "\n"

            try:
                parsed: Any = yaml_parser.load(StringIO(block_content))  # pyright: ignore[reportUnknownMemberType]
                if parsed and key in parsed:
                    entry_data = dict(parsed[key])
                    entries.append((key, entry_data))
            except Exception:
                logger.warning(
                    "Failed to parse entry '%s' at line %d, skipping",
                    key,
                    start_line + 1,
                )

        return entries

    def _merge_dotfile_entries(
        self, name: str, entries: list[dict[str, Any]]
    ) -> DotFileDict:
        """
        Merge multiple dotfile entries with the same key into a single entry.

        Combines paths from all entries (deduplicating), keeps the longest
        description as the primary one, and merges tags.

        Args:
            name: Application name (the duplicate key)
            entries: List of parsed dotfile dictionaries to merge

        Returns:
            Single merged DotFileDict
        """
        all_paths: list[str] = []
        descriptions: list[str] = []
        all_tags: list[str] = []

        for entry in entries:
            if "paths" in entry:
                paths_val = entry["paths"]
                if isinstance(paths_val, list):
                    for p in paths_val:  # pyright: ignore[reportUnknownVariableType]
                        if isinstance(p, str) and p not in all_paths:
                            all_paths.append(p)
            if "path" in entry:
                path_val = entry["path"]
                if isinstance(path_val, str) and path_val not in all_paths:
                    all_paths.append(path_val)

            desc = entry.get("description", "")
            if isinstance(desc, str) and desc:
                descriptions.append(desc)

            tags = entry.get("tags", "")
            if isinstance(tags, str) and tags:
                for tag in tags.split(","):
                    clean_tag = tag.strip()
                    if clean_tag and clean_tag not in all_tags:
                        all_tags.append(clean_tag)

        # PURPOSE: Longest description chosen as most informative; fallback to app name if none
        best_description = max(descriptions, key=len) if descriptions else name

        merged: DotFileDict = {"description": best_description}

        if len(all_paths) == 1:
            merged["path"] = all_paths[0]
        elif all_paths:
            merged["paths"] = all_paths

        if all_tags:
            merged["tags"] = ", ".join(all_tags)

        logger.info(
            "Merged duplicate '%s': combined %d entries into %d path(s)",
            name,
            len(entries),
            len(all_paths),
        )

        return merged

    def _validate_and_clean_dotfiles(
        self, data: dict[str, Any]
    ) -> dict[str, DotFileDict]:
        """
        Validate and clean all dotfile entries, fixing common issues.

        Handles:
        - Missing or empty descriptions (assigns default)
        - Missing path/paths (logs warning, keeps entry with empty paths)
        - Empty strings in paths lists (removed)
        - Duplicate paths within a single entry (deduplicated)
        - Non-string values in paths (converted to string)

        Args:
            data: Raw dotfile dictionary from YAML

        Returns:
            Cleaned dictionary of validated DotFileDict entries
        """
        cleaned: dict[str, DotFileDict] = {}

        for app_name, entry in data.items():
            if not isinstance(entry, dict):
                logger.warning(
                    "Dotfile '%s' has invalid format (expected mapping), skipping",
                    app_name,
                )
                continue

            clean_entry = self._clean_single_dotfile(
                str(app_name),
                dict(entry),  # pyright: ignore[reportUnknownArgumentType]
            )
            if clean_entry is not None:
                cleaned[str(app_name)] = clean_entry

        return cleaned

    def _clean_single_dotfile(
        self, app_name: str, data: dict[str, Any]
    ) -> DotFileDict | None:
        """
        Validate and clean a single dotfile entry.

        Args:
            app_name: Name of the application
            data: Raw dotfile entry data

        Returns:
            Cleaned DotFileDict, or None if entry is irrecoverably invalid
        """
        description = data.get("description")
        if not description or not isinstance(description, str):
            logger.warning(
                "Dotfile '%s' missing description, using app name as default",
                app_name,
            )
            data["description"] = f"{app_name} configuration"

        has_path = "path" in data
        has_paths = "paths" in data

        if has_paths:
            paths_raw = data["paths"]
            if isinstance(paths_raw, list):
                # CONSTRAINT: Remove empties, coerce non-strings, deduplicate — order preserved
                clean_paths: list[str] = []
                seen: set[str] = set()
                for p in paths_raw:  # pyright: ignore[reportUnknownVariableType]
                    p_str = str(p).strip() if p is not None else ""  # pyright: ignore[reportUnknownArgumentType]
                    if p_str and p_str not in seen:
                        clean_paths.append(p_str)
                        seen.add(p_str)

                if not clean_paths and not has_path:
                    logger.warning(
                        "Dotfile '%s' has empty paths list and no path, skipping",
                        app_name,
                    )
                    return None
                if not clean_paths:
                    # paths was empty but path exists — remove empty paths key
                    del data["paths"]
                else:
                    data["paths"] = clean_paths
            elif isinstance(paths_raw, str):
                # Single string in paths field — normalize to list
                paths_raw = paths_raw.strip()
                if paths_raw:
                    data["paths"] = [paths_raw]
                else:
                    del data["paths"]
            else:
                logger.warning(
                    "Dotfile '%s' has invalid paths type (%s), removing",
                    app_name,
                    type(paths_raw).__name__,
                )
                del data["paths"]

        if has_path:
            path_val = data["path"]
            if not isinstance(path_val, str) or not str(path_val).strip():
                if "paths" not in data:
                    logger.warning(
                        "Dotfile '%s' has empty path and no paths, skipping",
                        app_name,
                    )
                    return None
                del data["path"]
            else:
                data["path"] = str(path_val).strip()

        if "path" not in data and "paths" not in data:
            logger.warning(
                "Dotfile '%s' has neither 'path' nor 'paths', skipping",
                app_name,
            )
            return None

        return data  # type: ignore[return-value]

    def _validate_settings(self, data: dict[str, Any]) -> None:
        """
        Validate settings configuration structure.

        Args:
            data: Raw settings data from YAML file

        Raises:
            ValueError: If required sections or fields are missing
        """
        if "paths" not in data:
            raise ValueError("Settings missing required 'paths' section")
        if "options" not in data:
            raise ValueError("Settings missing required 'options' section")

        paths = data["paths"]
        required_paths = ["mirror_dir", "archive_dir", "restore_backup_dir"]
        for field in required_paths:
            if field not in paths:
                raise ValueError(f"Settings paths missing required field: {field}")

        options = data["options"]
        required_options = [
            "mirror",
            "archive",
            "hostname_subdir",
            "date_subdir",
            "archive_format",
            "archive_compression_level",
            "rotate_archives",
            "max_archives",
            "pre_restore_backup",
            "max_restore_backups",
        ]
        for field in required_options:
            if field not in options:
                raise ValueError(f"Settings options missing required field: {field}")

    def _validate_dotfile(self, app_name: str, data: dict[str, Any]) -> None:
        """
        Validate individual dotfile entry.

        Args:
            app_name: Name of the application
            data: Raw dotfile data from YAML file

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if "description" not in data:
            raise ValueError(f"Dotfile '{app_name}' missing required 'description'")

        if "path" not in data and "paths" not in data:
            raise ValueError(f"Dotfile '{app_name}' must have either 'path' or 'paths'")
