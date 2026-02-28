"""
Pytest Configuration and Shared Fixtures

Description:
    Central configuration and reusable fixtures for pytest test suite.
    Provides QApplication fixture for PySide6 testing, temporary file fixtures,
    and common test resources following MVVM testing best practices.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-02-2025
Date Changed: 02-01-2026
License: MIT

Features:
    - QApplication session fixture for Qt testing
    - Temporary directory fixtures for file operations
    - Mock service fixtures for ViewModel testing
    - Proper pytest-qt integration

Requirements:
    - pytest>=7.0.0
    - pytest-qt>=4.0.0
    - pytest-mock>=3.0.0
    - PySide6>=6.6.0
"""

from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from PySide6.QtWidgets import QApplication


if TYPE_CHECKING:
    from _pytest.config import Config


# =============================================================================
# Qt Application Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication]:
    """
    Create QApplication instance for Qt tests (session scope).

    This fixture ensures a single QApplication instance exists for all tests
    in the session, following pytest-qt best practices. Required for any test
    that uses PySide6 widgets, signals, or Qt functionality.

    Scope:
        session - One instance for entire test session

    Returns:
        QApplication: Qt application instance for testing

    Example:
        def test_viewmodel_with_qt(qapp, qtbot):
            vm = MyViewModel()
            # Test Qt functionality
    """
    app: QApplication | None = QApplication.instance()  # type: ignore[assignment]
    if app is None:
        app = QApplication([])
    yield app
    # Cleanup: process events and allow threads to finish
    app.processEvents()
    app.quit()


@pytest.fixture
def qapp_function() -> QApplication:
    """
    Create QApplication instance for function-scoped tests.

    Use this fixture when tests need a fresh QApplication instance
    for each test function (less common, but useful for isolation).

    Scope:
        function - New instance for each test function

    Returns:
        QApplication: Qt application instance for testing
    """
    app: QApplication | None = QApplication.instance()  # type: ignore[assignment]
    if app is None:
        app = QApplication([])
    return app


# =============================================================================
# Temporary File System Fixtures
# =============================================================================


@pytest.fixture
def temp_config_path(tmp_path: Path) -> Path:
    """
    Provide temporary path for configuration file testing.

    Args:
        tmp_path: pytest built-in temporary directory fixture

    Returns:
        Path: Temporary config file path (not created, ready to use)

    Example:
        def test_load_config(temp_config_path):
            model = DFBUModel(temp_config_path)
            # Test configuration loading
    """
    return tmp_path / "test_config.toml"


@pytest.fixture
def temp_dotfile(tmp_path: Path) -> Path:
    """
    Create a temporary dotfile with content for testing.

    Args:
        tmp_path: pytest built-in temporary directory fixture

    Returns:
        Path: Path to created test dotfile

    Example:
        def test_backup_file(temp_dotfile):
            # Test backup of actual file
            assert temp_dotfile.exists()
    """
    dotfile = tmp_path / "test_dotfile.conf"
    dotfile.write_text("# Test configuration\ntest_key = test_value\n")
    return dotfile


@pytest.fixture
def temp_dotfile_dir(tmp_path: Path) -> Path:
    """
    Create a temporary directory with multiple files for testing.

    Args:
        tmp_path: pytest built-in temporary directory fixture

    Returns:
        Path: Path to created test directory

    Example:
        def test_backup_directory(temp_dotfile_dir):
            # Test backup of entire directory
            assert temp_dotfile_dir.is_dir()
    """
    dotdir = tmp_path / "test_dotdir"
    dotdir.mkdir()

    # Create some test files in the directory
    (dotdir / "file1.conf").write_text("File 1 content")
    (dotdir / "file2.conf").write_text("File 2 content")
    (dotdir / "subdir").mkdir()
    (dotdir / "subdir" / "file3.conf").write_text("File 3 content")

    return dotdir


# =============================================================================
# Sample Configuration Fixtures
# =============================================================================


@pytest.fixture
def yaml_config_dir(tmp_path: Path) -> Path:
    """
    Create a temporary directory with valid YAML configuration files.

    This fixture creates the three YAML files needed by ConfigManager:
    - settings.yaml (paths and options)
    - dotfiles.yaml (dotfile definitions)
    - session.yaml (exclusions)

    Args:
        tmp_path: pytest built-in temporary directory fixture

    Returns:
        Path: Directory containing YAML configuration files

    Example:
        def test_config(yaml_config_dir):
            manager = ConfigManager(yaml_config_dir, expand_path_callback=...)
            success, error = manager.load_config()
    """
    # Create settings.yaml
    settings_file = tmp_path / "settings.yaml"
    settings_file.write_text("""
paths:
  mirror_dir: ~/test_mirror
  archive_dir: ~/test_archive
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: false
  hostname_subdir: true
  date_subdir: false
  archive_format: tar.gz
  archive_compression_level: 9
  rotate_archives: true
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
  verify_after_backup: false
  hash_verification: false
""")

    # Create dotfiles.yaml
    dotfiles_file = tmp_path / "dotfiles.yaml"
    dotfiles_file.write_text("""
TestApp:
  description: Test dotfile
  path: ~/test.txt
""")

    # Create session.yaml
    session_file = tmp_path / "session.yaml"
    session_file.write_text("""
excluded: []
""")

    return tmp_path


@pytest.fixture
def minimal_config_content() -> str:
    """
    Provide minimal valid TOML configuration content (legacy).

    NOTE: This is kept for backward compatibility with some tests.
    New tests should use yaml_config_dir fixture instead.

    Returns:
        str: Minimal valid TOML configuration

    Example:
        def test_minimal_config(tmp_path, minimal_config_content):
            config_path = tmp_path / "config.toml"
            config_path.write_text(minimal_config_content)
            # Test loading minimal config
    """
    return """
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true
archive = false
hostname_subdir = true
date_subdir = false

[[dotfile]]
category = "Test"
application = "TestApp"
description = "Test dotfile"
path = "~/test.txt"
enabled = true
"""


@pytest.fixture
def complete_config_content() -> str:
    """
    Provide complete TOML configuration with all options.

    Returns:
        str: Complete TOML configuration with all fields

    Example:
        def test_complete_config(tmp_path, complete_config_content):
            config_path = tmp_path / "config.toml"
            config_path.write_text(complete_config_content)
            # Test loading complete config
    """
    return """
[paths]
mirror_dir = "~/dfbu_mirror"
archive_dir = "~/dfbu_archive"

[options]
mirror = true
archive = true
hostname_subdir = true
date_subdir = false
archive_format = "tar.gz"
archive_compression_level = 9
rotate_archives = true
max_archives = 5

[[dotfile]]
category = "Shell"
application = "Bash"
description = "Bash configuration"
path = "~/.bashrc"
enabled = true

[[dotfile]]
category = "Editor"
application = "Vim"
description = "Vim configuration"
path = "~/.vimrc"
enabled = false

[[dotfile]]
category = "Terminal"
application = "Alacritty"
description = "Alacritty config directory"
path = "~/.config/alacritty"
enabled = true
"""


# =============================================================================
# Mock Service Fixtures for MVVM Testing
# =============================================================================


@pytest.fixture
def mock_file_service(mocker: Any) -> Any:
    """
    Provide mock file service for testing ViewModels.

    This fixture creates a mock service object that can be injected into
    ViewModels for isolated testing without actual file operations.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock: Configured mock service object

    Example:
        def test_viewmodel_with_mock_service(mock_file_service):
            mock_file_service.load_files.return_value = ["file1", "file2"]
            vm = MyViewModel(mock_file_service)
            # Test ViewModel without actual file I/O
    """
    mock_service = mocker.Mock()
    mock_service.load_files.return_value = []
    mock_service.save_file.return_value = True
    mock_service.exists.return_value = True
    return mock_service


@pytest.fixture
def mock_config_service(mocker: Any) -> Any:
    """
    Provide mock configuration service for testing.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock: Configured mock configuration service

    Example:
        def test_config_loading(mock_config_service):
            mock_config_service.load.return_value = {"key": "value"}
            # Test configuration handling
    """
    mock_service = mocker.Mock()
    mock_service.load.return_value = {}
    mock_service.save.return_value = True
    return mock_service


# =============================================================================
# Path Setup and Custom Markers
# =============================================================================


def pytest_configure(config: Config) -> None:
    """
    Configure pytest session before test collection.

    Adds parent directory to path for proper imports of application modules.
    This ensures test files can import from the gui package.
    Also registers custom pytest markers.

    Args:
        config: pytest configuration object
    """
    # Add DFBU directory to path for imports
    dfbu_dir = Path(__file__).parent.parent
    if str(dfbu_dir) not in sys.path:
        sys.path.insert(0, str(dfbu_dir))

    # Register custom markers
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line(
        "markers", "integration: Integration tests across components"
    )
    config.addinivalue_line("markers", "slow: Tests that take more than 1 second")
    config.addinivalue_line(
        "markers", "gui: Tests requiring GUI components and QApplication"
    )
