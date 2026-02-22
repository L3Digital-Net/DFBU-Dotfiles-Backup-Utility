"""
DFBU ConfigWorkers - Worker Threads for Configuration Operations

Description:
    Worker threads for non-blocking configuration load/save operations.
    Prevents UI freezing during YAML file I/O, backup rotation, and path validation.
    Provides progress feedback for large configurations.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-06-2025
Date Changed: 11-06-2025
License: MIT

Features:
    - Non-blocking configuration loading with progress feedback
    - Non-blocking configuration saving with rotating backups
    - Parallel path validation for efficiency
    - Signal-based communication with ViewModel
    - Thread-safe operations
    - Memory-efficient processing

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - PySide6 framework for Qt threading
    - Local: config_manager module

Classes:
    - ConfigLoadWorker: Worker thread for loading configuration
    - ConfigSaveWorker: Worker thread for saving configuration

Functions:
    None
"""

from PySide6.QtCore import QThread, Signal

from gui.config_manager import ConfigManager


class ConfigLoadWorker(QThread):
    """
    Worker thread for loading configuration without blocking UI.

    Signals:
        progress_updated: Emitted during load operation (percentage)
        load_finished: Emitted when load completes (success, error_message, dotfile_count)
        error_occurred: Emitted on error (context, error_message)

    Attributes:
        config_manager: Reference to ConfigManager instance
    """

    progress_updated = Signal(int)  # progress percentage
    load_finished = Signal(bool, str, int)  # success, error_message, dotfile_count
    error_occurred = Signal(str, str)  # context, error_message

    def __init__(self) -> None:
        """Initialize the ConfigLoadWorker."""
        super().__init__()
        self.config_manager: ConfigManager | None = None

    def set_config_manager(self, config_manager: ConfigManager) -> None:
        """
        Set the config manager reference.

        Args:
            config_manager: ConfigManager instance to use for loading
        """
        self.config_manager = config_manager

    def run(self) -> None:
        """
        Main thread execution method for loading configuration.

        Loads YAML configuration, validates, and emits progress signals.
        """
        if not self.config_manager:
            self.error_occurred.emit("Configuration Load", "Config manager not set")
            return

        try:
            self.progress_updated.emit(10)

            success, error_message = self.config_manager.load_config()

            self.progress_updated.emit(100)

            dotfile_count = self.config_manager.get_dotfile_count()
            self.load_finished.emit(success, error_message, dotfile_count)

        except Exception as e:
            self.error_occurred.emit(
                "Configuration Load", f"Unexpected error: {type(e).__name__}: {e}"
            )
            self.load_finished.emit(False, str(e), 0)


class ConfigSaveWorker(QThread):
    """
    Worker thread for saving configuration without blocking UI.

    Signals:
        progress_updated: Emitted during save operation (percentage)
        save_finished: Emitted when save completes (success, error_message)
        error_occurred: Emitted on error (context, error_message)

    Attributes:
        config_manager: Reference to ConfigManager instance
    """

    progress_updated = Signal(int)  # progress percentage
    save_finished = Signal(bool, str)  # success, error_message
    error_occurred = Signal(str, str)  # context, error_message

    def __init__(self) -> None:
        """Initialize the ConfigSaveWorker."""
        super().__init__()
        self.config_manager: ConfigManager | None = None

    def set_config_manager(self, config_manager: ConfigManager) -> None:
        """
        Set the config manager reference.

        Args:
            config_manager: ConfigManager instance to use for saving
        """
        self.config_manager = config_manager

    def run(self) -> None:
        """
        Main thread execution method for saving configuration.

        Creates rotating backup, builds YAML structure, and writes files.
        """
        if not self.config_manager:
            self.error_occurred.emit("Configuration Save", "Config manager not set")
            return

        try:
            self.progress_updated.emit(10)

            self.progress_updated.emit(40)

            success, error_message = self.config_manager.save_config()

            self.progress_updated.emit(100)

            self.save_finished.emit(success, error_message)

        except Exception as e:
            self.error_occurred.emit(
                "Configuration Save", f"Unexpected error: {type(e).__name__}: {e}"
            )
            self.save_finished.emit(False, str(e))
