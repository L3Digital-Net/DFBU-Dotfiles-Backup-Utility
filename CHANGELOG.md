# Changelog

All notable changes to DFBU are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

- ci: add coverage gate (--cov-fail-under=80)

## [1.2.3] — 2026-02-22

AppImage build only; no feature changes.

## [1.2.0] — 2026-02-06

### Added

- Verbose Log Mode: toggle shows full destination paths in log pane
- Individual skip logging per file (replaces batch summaries every 10 files)
- Hide Missing Checkbox: filter dotfiles with absent source paths
- Edit Config, Validate Config, Export Config actions
- Unified Browse Picker: single dialog accepts both files and directories

### Changed

- "Update" button renamed to "Edit" for clarity
- Removed batch skip throttling (`SKIP_LOG_INTERVAL`)

## [1.1.0] — 2026-02-04

### Added

- Branded theme: centralized `DFBUColors` palette + `dfbu_light.qss` stylesheet
- Restructured tabs: Backup, Restore (with backup preview tree), Config, Logs (color-coded)
- AppImage distribution: portable single-file binary, no dependencies required
- Expanded dotfiles library: 300+ entries with XDG and Flatpak variants
- Application icon (SVG/PNG) for desktop integration

### Changed

- Non-critical confirmation dialogs replaced with status bar messages

## [1.0.0] — 2026-02-02

### Added

- YAML config split: `settings.yaml`, `dotfiles.yaml`, `session.yaml`
- Mirror and archive backup modes
- Backup verification with optional hash checking
- Pre-restore safety backup before restore operations
- Structured error handling with retry eligibility
- MVVM architecture with PySide6 GUI

## [0.9.2] — 2026-02-01

### Changed

- Removed dead `validation.py` code (leftover from removed CLI in v0.7.0)
- Documentation updated to reflect v0.9.1 features and current architecture

## [0.9.1] — 2026-02-01

### Fixed

- Replace Category dropdown with Tags text field in Add Dotfile dialog
- Tags now accept comma-separated values and are optional
- Dialog handles legacy data with `category` field

## [0.7.0] — 2026-02-01

### Changed

- Configuration always loads from `DFBU/data/`; path no longer user-selectable
- Migrated from TOML to YAML config format (`settings.yaml`, `dotfiles.yaml`, `session.yaml`)

### Removed

- Config directory selection UI from Backup tab
- "Load Configuration..." menu action (Ctrl+O)
- CLI application (`dfbu.py`)

### Fixed

- `DEFAULT_CONFIG_PATH` pointing to non-existent `.toml` file after YAML migration
