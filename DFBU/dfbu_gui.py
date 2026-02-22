#!/usr/bin/env python3
r"""
DFBU GUI - Dotfiles Backup Utility (Desktop Edition)

Description:
    Desktop application for comprehensive file backup and restoration with a
    graphical user interface. Built on MVVM architecture using PySide6,
    providing an intuitive way to manage configuration file backups.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-18-2025
Date Changed: 02-01-2026
License: MIT

Features:
    - MVVM desktop GUI with tab-based interface and threaded operations
    - Window state persistence and responsive user feedback
    - YAML configuration with Application/Description/Paths/Tags structure
    - Interactive dotfile management (add, update, remove)
    - Flexible backup organization with hostname and date-based directories
    - Mirror and compressed archive backup modes with rotation
    - Interactive restore with progress tracking and pre-restore backups
    - Backup verification with size and optional SHA-256 hash checking
    - File size analysis with configurable thresholds and warnings
    - Structured error handling with recovery dialogs
    - Python 3.14 Path.copy() with metadata and symlink support
    - Standard library first approach with minimal dependencies

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - PySide6 for GUI components
    - Additional technical requirements and dependencies

Known Issues:
    - No support for network paths or remote destinations
    - Restore functionality requires exact hostname match in backup directory structure
    - Limited symlink support (follow_symlinks=True only)

Planned Features:
    - Differential backups with change detection based on modification time
    - Enhanced restore capabilities with cross-hostname support
    - Incremental backup support with change detection
    - Network path support for remote backup destinations
    - Scheduled backups with timer-based automation
    - Multiple configuration profile support
    - Drag-and-drop file addition to configuration
    - Dark mode theme support

Classes:
    - Application: Main application controller implementing MVVM pattern

Functions:
    - main: Main entry point for the application
"""

import shutil
import sys
from pathlib import Path
from typing import Final, cast


# SIDE-EFFECT: Mutates sys.path — must execute before any local module imports
# Ensures 'gui' is importable as a package when run directly or via `python -m DFBU`
# Frozen (PyInstaller) builds skip this — the import hook handles resolution
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).parent))

from gui.logging_config import get_logger, setup_default_logging
from gui.model import DFBUModel
from gui.theme_loader import load_theme
from gui.view import MainWindow
from gui.viewmodel import DFBUViewModel


# DANGER: PySide6 absence is unrecoverable — no fallback GUI; hard-exit is intentional
try:
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("PySide6 is required but not installed.")
    print("Install it with: pip install PySide6")
    sys.exit(1)

# SIDE-EFFECT: Configures global log handlers before any module emits events
setup_default_logging()
logger = get_logger(__name__)

__version__: Final[str] = "1.2.1"
PROJECT_NAME: Final[str] = "DFBU GUI"
# CONSTRAINT: Writable by user; live config and history are written here at runtime
USER_CONFIG_DIR: Final[Path] = Path.home() / ".config" / "dfbu"

# Bundled config path — read-only when frozen; sys._MEIPASS is the unpacked bundle root
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    _data_base = Path(cast(str, sys._MEIPASS))
else:
    _data_base = Path(__file__).parent
BUNDLED_CONFIG_PATH: Final[Path] = (_data_base / "data").resolve()

IS_FROZEN: Final[bool] = getattr(sys, "frozen", False)

# Frozen → USER_CONFIG_DIR (writable); source → BUNDLED_CONFIG_PATH (local data dir)
DEFAULT_CONFIG_PATH: Final[Path] = USER_CONFIG_DIR if IS_FROZEN else BUNDLED_CONFIG_PATH


def _initialize_user_config() -> None:
    """
    Initialize user config directory with bundled defaults on first run.

    When running as AppImage/frozen app, the bundled config files are read-only.
    This function copies them to the user's writable config directory on first run.
    Verifies that all required config files are present after initialization.

    Files copied: settings.yaml, dotfiles.yaml, session.yaml, .dfbuignore
    """
    if not IS_FROZEN:
        return  # CONSTRAINT: Source mode uses BUNDLED_CONFIG_PATH directly — no copy needed

    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # CONSTRAINT: All four files required; missing any causes config load failure on startup
    config_files = ["settings.yaml", "dotfiles.yaml", "session.yaml", ".dfbuignore"]

    for filename in config_files:
        user_file = USER_CONFIG_DIR / filename
        bundled_file = BUNDLED_CONFIG_PATH / filename

        # CONSTRAINT: Skip if user file exists — never overwrite user customizations on upgrade
        if not user_file.exists() and bundled_file.exists():
            try:
                shutil.copy2(bundled_file, user_file)
                logger.info("Copied default config: %s -> %s", filename, user_file)
            except (OSError, PermissionError) as e:
                logger.warning("Failed to copy default config %s: %s", filename, e)

    missing = [f for f in config_files if not (USER_CONFIG_DIR / f).exists()]
    if missing:
        logger.error(
            "Missing required config files after initialization: %s "
            "(bundled path: %s, user path: %s)",
            ", ".join(missing),
            BUNDLED_CONFIG_PATH,
            USER_CONFIG_DIR,
        )
        # DANGER: If bundled source also missing, config gap is unrecoverable — log both failure paths
        for filename in missing:
            bundled_file = BUNDLED_CONFIG_PATH / filename
            if bundled_file.exists():
                try:
                    shutil.copy2(bundled_file, USER_CONFIG_DIR / filename)
                    logger.info("Fallback copy succeeded: %s", filename)
                except (OSError, PermissionError) as e:
                    logger.error("Fallback copy failed for %s: %s", filename, e)
            else:
                logger.error(
                    "Bundled config not found: %s (expected at %s)",
                    filename,
                    bundled_file,
                )
    else:
        logger.info(
            "All config files verified in %s (%d files)",
            USER_CONFIG_DIR,
            len(config_files),
        )


class Application:
    """
    Main application controller implementing MVVM pattern.

    Attributes:
        app: QApplication instance
        model: DFBUModel for business logic and state
        viewmodel: DFBUViewModel for presentation logic
        view: MainWindow for UI presentation

    Public methods:
        run: Start the application main loop
        cleanup: Perform cleanup when application exits

    Private methods:
        _initialize_config_directory: Create configuration directory if needed
    """

    def __init__(self) -> None:
        """Initialize the Application with MVVM architecture."""
        logger.info(f"Initializing {PROJECT_NAME} v{__version__}")

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(PROJECT_NAME)
        self.app.setApplicationVersion(__version__)
        self.app.setOrganizationName("L3DigitalNet")

        # Load user's preferred theme (read QSettings directly — ViewModel not yet created)
        settings = QSettings("L3DigitalNet", "dfbu_gui_settings")
        saved_theme = str(settings.value("appearance/theme", "dfbu_light"))
        if not load_theme(self.app, saved_theme):
            load_theme(self.app)  # Fallback to default light theme

        icon_path = Path(__file__).parent / "resources" / "icons" / "dfbu.svg"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))

        self._initialize_config_directory()

        try:
            # CONSTRAINT: Instantiation order fixed — Model owns state, ViewModel wraps Model, View wraps ViewModel
            logger.debug("Creating Model with config path: %s", DEFAULT_CONFIG_PATH)
            self.model = DFBUModel(DEFAULT_CONFIG_PATH)

            logger.debug("Creating ViewModel")
            self.viewmodel = DFBUViewModel(self.model)

            logger.debug("Creating Main Window")
            self.view = MainWindow(self.viewmodel, __version__)

            self._load_config_if_available()

            logger.info("Application initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize application: %s", e, exc_info=True)
            raise

    def _initialize_config_directory(self) -> None:
        """Create configuration directory and copy defaults if needed."""
        # SIDE-EFFECT: May copy files from BUNDLED_CONFIG_PATH → USER_CONFIG_DIR on first frozen-app run
        _initialize_user_config()

    def _load_config_if_available(self) -> None:
        """
        Load configuration from default path on startup.

        Verifies config path exists and contains required files before
        attempting to load. Logs diagnostic information on failure.
        """
        if not DEFAULT_CONFIG_PATH.exists():
            logger.warning("Config directory does not exist: %s", DEFAULT_CONFIG_PATH)
            return

        required = ["settings.yaml", "dotfiles.yaml"]
        missing = [f for f in required if not (DEFAULT_CONFIG_PATH / f).exists()]
        if missing:
            logger.error(
                "Cannot load config — missing required files in %s: %s",
                DEFAULT_CONFIG_PATH,
                ", ".join(missing),
            )
            return

        logger.info("Loading configuration from %s", DEFAULT_CONFIG_PATH)
        self.viewmodel.command_load_config()

    def run(self) -> int:
        """
        Start the application main loop.

        Returns:
            Application exit code
        """
        self.view.show()
        exit_code = self.app.exec()
        self.cleanup()
        return exit_code

    def cleanup(self) -> None:
        """Perform cleanup when application exits."""


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Application exit code
    """
    app = Application()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
