"""
DFBU ProfileManager - Backup Profile Management Component

Description:
    Handles named backup profiles allowing users to save and switch
    between different dotfile selection and option configurations.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT
"""

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML


sys.path.insert(0, str(Path(__file__).parent.parent))

from core.common_types import ProfileDict


class ProfileManager:
    """
    Manages backup profiles for different configurations.

    Profiles allow users to save named presets of excluded dotfiles
    and option overrides for quick switching between backup configurations.

    Attributes:
        config_path: Path to configuration directory
        _profiles: Dictionary of profile name -> ProfileDict
        _active_profile: Name of currently active profile (None = default)
    """

    def __init__(self, config_path: Path) -> None:
        """
        Initialize ProfileManager.

        Args:
            config_path: Path to configuration directory for profiles.yaml
        """
        self.config_path: Path = config_path
        self._profiles: dict[str, ProfileDict] = {}
        self._active_profile: str | None = None

        self._yaml: YAML = YAML()
        self._yaml.preserve_quotes = True
        self._yaml.default_flow_style = False

    def get_profile_count(self) -> int:
        """
        Get number of saved profiles.

        Returns:
            Number of profiles in storage
        """
        return len(self._profiles)

    def get_active_profile_name(self) -> str | None:
        """
        Get name of currently active profile.

        Returns:
            Active profile name, or None if using default settings
        """
        return self._active_profile

    def load_profiles(self) -> tuple[bool, str]:
        """
        Load profiles from YAML configuration file.

        Returns:
            Tuple of (success, error_message)
        """
        profiles_file = self.config_path / "profiles.yaml"

        if not profiles_file.exists():
            return (
                True,
                "",
            )  # CONSTRAINT: Missing profiles.yaml means no profiles configured — not an error

        try:
            with profiles_file.open("r", encoding="utf-8") as f:
                data = self._yaml.load(f)

            if data is None:
                return True, ""

            self._active_profile = data.pop("active_profile", None)

            # CONSTRAINT: active_profile popped before iteration — remaining keys are profile names
            for name, profile_data in data.items():
                if isinstance(profile_data, dict):
                    self._profiles[name] = ProfileDict(
                        name=name,
                        description=profile_data.get("description", ""),
                        excluded=profile_data.get("excluded", []),
                        options_overrides=profile_data.get("options_overrides", {}),
                        created_at=profile_data.get("created_at", ""),
                        modified_at=profile_data.get("modified_at", ""),
                    )

            return True, ""

        except OSError as e:
            return False, f"Failed to load profiles: {e}"

    def save_profiles(self) -> tuple[bool, str]:
        """
        Save profiles to YAML configuration file.

        Returns:
            Tuple of (success, error_message)
        """
        profiles_file = self.config_path / "profiles.yaml"

        try:
            data: dict[str, Any] = {}

            for name, profile in self._profiles.items():
                data[name] = {
                    "description": profile["description"],
                    "excluded": profile["excluded"],
                    "options_overrides": profile["options_overrides"],
                    "created_at": profile["created_at"],
                    "modified_at": profile["modified_at"],
                }

            if self._active_profile:
                data["active_profile"] = self._active_profile

            with profiles_file.open("w", encoding="utf-8") as f:
                self._yaml.dump(data, f)

            return True, ""

        except OSError as e:
            return False, f"Failed to save profiles: {e}"

    def create_profile(
        self,
        name: str,
        description: str,
        excluded: list[str],
        options_overrides: dict[str, bool | int | str] | None = None,
    ) -> bool:
        """
        Create a new backup profile.

        Args:
            name: Unique profile name
            description: Human-readable description
            excluded: List of application names to exclude
            options_overrides: Optional settings overrides

        Returns:
            True if profile was created successfully
        """
        if name in self._profiles:
            return False  # Profile already exists

        now = datetime.now(UTC).isoformat()
        self._profiles[name] = ProfileDict(
            name=name,
            description=description,
            excluded=excluded,
            options_overrides=options_overrides or {},
            created_at=now,
            modified_at=now,
        )
        return True

    def get_profile(self, name: str) -> ProfileDict | None:
        """
        Get profile by name.

        Args:
            name: Profile name to retrieve

        Returns:
            ProfileDict or None if not found
        """
        return self._profiles.get(name)

    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile by name.

        Args:
            name: Profile name to delete

        Returns:
            True if profile was deleted
        """
        if name not in self._profiles:
            return False

        del self._profiles[name]

        if self._active_profile == name:
            self._active_profile = None

        return True

    def switch_profile(self, name: str | None) -> bool:
        """
        Switch to a different profile.

        Args:
            name: Profile name to switch to, or None for default

        Returns:
            True if switch was successful
        """
        if name is not None and name not in self._profiles:
            return False

        self._active_profile = name
        return True

    def get_active_exclusions(self) -> list[str]:
        """
        Get exclusions from active profile.

        Returns:
            List of excluded application names, empty if no active profile
        """
        if self._active_profile is None:
            return []

        profile = self._profiles.get(self._active_profile)
        if profile is None:
            return []

        return profile["excluded"]

    def get_profile_names(self) -> list[str]:
        """
        Get list of all profile names.

        Returns:
            Sorted list of profile names
        """
        return sorted(self._profiles.keys())
