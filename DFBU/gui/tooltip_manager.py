"""Centralized tooltip management for DFBU GUI.

This module provides the TooltipManager class which stores and applies
tooltips to all configuration controls in the application.
"""

from PySide6.QtWidgets import QWidget


class TooltipManager:
    """Manages tooltips for all GUI widgets.

    Stores tooltip definitions centrally and applies them to widgets
    after UI load. Includes an enabled property for future "disable
    tooltips" setting support.

    Attributes:
        enabled: Whether tooltips should be applied. When False,
            apply_tooltips() will skip setting tooltips.
    """

    TOOLTIPS: dict[str, str] = {
        # Backup Tab - File Group
        "filterLineEdit": "Filter the file list by application name, tags, or path",
        "fileGroupAddFileButton": "Add a new dotfile entry to the configuration",
        "fileGroupUpdateFileButton": "Edit the selected dotfile entry",
        "fileGroupRemoveFileButton": "Remove the selected dotfile from the configuration",
        "fileGroupToggleEnabledButton": "Include or exclude selected files from backup operations",
        # fileGroupSaveFilesButton - already has tooltip in .ui
        # Backup Tab - Options
        "mirrorCheckbox": "Copy files to an uncompressed directory preserving folder structure",
        "archiveCheckbox": "Create a compressed archive of all selected files",
        # forceBackupCheckbox - already has tooltip in .ui
        # startBackupButton - already has tooltip in .ui
        # Restore Tab
        "restoreSourceEdit": "Path to the backup directory containing your hostname folder",
        "restoreSourceBrowseButton": "Browse for a backup directory to restore from",
        "restoreSourceButton": "Restore files from the selected backup to their original locations",
        # Configuration Tab - Paths
        "config_mirror_path_edit": "Directory where uncompressed mirror backups are stored",
        "browse_mirror_btn": "Browse for a mirror backup directory",
        "configArchivePathEdit": "Directory where compressed archive backups are stored",
        "browseArchiveButton": "Browse for an archive backup directory",
        # Configuration Tab - Modes
        "config_mirror_checkbox": "Enable copying files to the mirror directory during backup",
        "config_archive_checkbox": "Enable creating compressed archives during backup",
        # Configuration Tab - Directory Structure
        "config_hostname_checkbox": "Create a subdirectory named after this computer's hostname",
        "config_date_checkbox": "Create a subdirectory with today's date for each backup",
        # Configuration Tab - Archive Options
        # config_compression_spinbox - already has tooltip in .ui
        "config_rotate_checkbox": "Automatically delete oldest archives when the limit is reached",
        # config_max_archives_spinbox - already has tooltip in .ui
        # Configuration Tab - Pre-Restore Safety
        # config_pre_restore_checkbox - already has tooltip in .ui
        # config_max_restore_spinbox - already has tooltip in .ui
        # config_restore_path_edit - already has tooltip in .ui
        "browse_restore_btn": "Browse for a pre-restore backup directory",
        "saveConfigButton": "Save all configuration changes to settings.yaml",
        # Logs Tab
        # verifyBackupButton - already has tooltip in .ui
        "pushButton": "Save the current log output to a file",
    }

    def __init__(self, enabled: bool = True) -> None:
        """Initialize the tooltip manager.

        Args:
            enabled: Whether tooltips should be applied. Defaults to True.
        """
        self.enabled = enabled

    def apply_tooltips(self, parent: QWidget) -> int:
        """Apply tooltips to all known widgets within the parent.

        Searches for child widgets by object name and sets their tooltips
        from the TOOLTIPS dictionary. Only applies tooltips if enabled
        is True.

        Args:
            parent: The parent widget (typically MainWindow) to search
                for child widgets.

        Returns:
            The number of tooltips successfully applied.
        """
        if not self.enabled:
            return 0

        applied_count = 0
        for widget_name, tooltip_text in self.TOOLTIPS.items():
            widget = parent.findChild(QWidget, widget_name)
            if widget is not None:
                widget.setToolTip(tooltip_text)
                applied_count += 1

        return applied_count

    def clear_tooltips(self, parent: QWidget) -> int:
        """Remove tooltips from all known widgets within the parent.

        Useful for implementing a "disable tooltips" feature at runtime.

        Args:
            parent: The parent widget to search for child widgets.

        Returns:
            The number of tooltips cleared.
        """
        cleared_count = 0
        for widget_name in self.TOOLTIPS:
            widget = parent.findChild(QWidget, widget_name)
            if widget is not None:
                widget.setToolTip("")
                cleared_count += 1

        return cleared_count
