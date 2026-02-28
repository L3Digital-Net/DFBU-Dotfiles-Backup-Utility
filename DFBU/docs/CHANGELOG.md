<!-- @format -->

# Changelog - Dotfiles Backup Utility

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version Format

- **MAJOR**: Feature completeness milestones
- **MINOR**: New functionality additions
- **PATCH**: Bug fixes and code refactoring
- **Development Stages**: `.dev`, `.a` (alpha), `.b` (beta), `.rc` (release candidate)

## [1.2.1] - 2026-02-06

### Added

- **GitHub Release Workflow**: CI automatically builds and publishes AppImage on version
  tags
- **AppImage Auto-Update Support**: Embedded zsync update info for delta updates via
  AppImageUpdate
- **Release Prompt File**: Copilot prompt to walk through the full publish process

### Changed

- **`.gitignore` Rewrite**: Replaced generic Python template with clean project-specific
  rules; removed 47 unnecessary tracked files (AI configs, screenshots, test artifacts)

## [1.2.0] - 2026-02-06

### Added

- **Verbose Log Mode**: Checkable "Verbose" toggle button in log pane toolbar shows full
  destination paths in backup log entries
- **Individual Skip Logging**: Each unchanged/skipped file is now logged individually by
  name instead of batch summaries every 10 files
- **Hide Missing Checkbox**: Filter checkbox on backup tab hides dotfiles whose source
  paths don't exist on disk
- **Edit Config Button**: Opens `dotfiles.yaml` in the system's default text editor via
  `xdg-open`
- **Validate Config Button**: Checks `dotfiles.yaml` and `settings.yaml` for YAML syntax
  and structure errors with reload option
- **Export Config Button**: Exports `dotfiles.yaml` and `settings.yaml` to a user-chosen
  directory for safekeeping
- **Unified Browse Picker**: Replaced the file/directory selection prompt with a single
  non-native QFileDialog that accepts both files and directories

### Changed

- **Backup Tab**: "Update" button renamed to "Edit" for clarity
- **Skip Logging**: Removed `SKIP_LOG_INTERVAL` constant and batch throttling; verbose
  mode shows full path for skipped files too
- **Log Output**: Verbose mode integrates with both processed and skipped file logging

### Removed

- `SKIP_LOG_INTERVAL` constant (no longer needed with individual logging)
- `_last_logged_skip_count` tracking variable (batch counting removed)
- File/directory type selection `QMessageBox` prompt in AddDotfileDialog (replaced by
  unified picker)

## [1.1.0] - 2026-02-01

### Added

- **Configuration Tab Extensions**: Added GUI controls for all settings in
  `settings.yaml`:
  - Verification Options section: "Verify After Backup" and "Hash Verification"
    checkboxes
  - Size Management section: "Enable Size Check" checkbox and threshold spinboxes
    (Warning/Alert/Critical MB)
- Integration tests for new configuration options

### Changed

- Configuration tab now exposes all available backup settings

## [1.0.0] - 2026-02-01

### Added

- **File Size Management (P3)**: Pre-backup size analysis and warnings
  - `SizeAnalyzer` component for analyzing dotfile sizes before backup
  - Configurable warning thresholds: Warning (10MB), Alert (100MB), Critical (1GB)
  - `.dfbuignore` file support for gitignore-style exclusion patterns
  - `SizeWarningDialog` UI showing large files with severity levels
  - Size check can be enabled/disabled in settings
  - Progress callback support for non-blocking analysis
  - Worker thread (`SizeScanWorker`) for background size scanning

- **Documentation Overhaul**
  - Created `docs/INDEX.md` - comprehensive documentation navigation
  - Created `docs/TROUBLESHOOTING.md` - user-focused issue resolution guide
  - Rewrote `README.md` for end users (reduced from 473 to 217 lines)
  - Added cross-references to consolidate duplicated content

### Changed

- **README.md**: Completely rewritten for intermediate Linux users
  - Removed developer-focused content (MVVM, testing, architecture)
  - Added user-focused features, backup modes explanation, troubleshooting
  - Simplified installation instructions to 3 commands
  - Moved developer content to `CONTRIBUTING.md`

- **CONTRIBUTING.md**: Now serves as the developer hub
  - Added cross-references to canonical documentation sources
  - Links to `ARCHITECTURE.md`, `tests/README.md`, and documentation index

- **AI Documentation**: Added cross-references to reduce duplication
  - Updated `CLAUDE.md` with links to architecture and testing docs
  - Updated `AGENTS.md` with project documentation section
  - Maintains separate docs for different AI systems while reducing redundancy

### New Files

- `DFBU/gui/size_analyzer.py` - Size analysis component
- `DFBU/gui/size_warning_dialog.py` - Size warning dialog
- `DFBU/gui/designer/size_warning_dialog.ui` - Dialog UI design
- `DFBU/data/.dfbuignore` - Default exclusion patterns
- `DFBU/tests/test_size_analyzer.py` - 28 unit tests for size analysis
- `docs/INDEX.md` - Documentation index
- `docs/TROUBLESHOOTING.md` - User troubleshooting guide

### TypedDict Additions

- `SizeItemDict`: Individual file/directory size entry with threshold level
- `SizeReportDict`: Backup size analysis report with summary and large items

## [0.6.1] - 2026-02-01

### Added

- **YAML Configuration Format**: Complete migration from TOML to YAML for easier manual
  editing
  - Split configuration into three files: `settings.yaml`, `dotfiles.yaml`,
    `session.yaml`
  - 53% file size reduction (1,941 lines TOML → 906 lines YAML)
  - Compact dotfile format with application name as key
  - Optional comma-separated tags on single line
  - Uses `ruamel.yaml` for comment preservation and round-trip editing
- **Exclusion-Based Selection**: New selection model replacing enabled/disabled toggles
  - All dotfiles included by default
  - Session exclusions persisted in `session.yaml`
  - Filter by application name, tags, or path in UI
- **Migration Script**: Automatic TOML to YAML migration with duplicate consolidation
  - Added `core/migration.py` for one-time migration
  - Consolidated duplicate entries (Firefox ×3, Steam ×2, etc.)
  - Cleaned up redundant description prefixes

### Changed

- **ConfigManager Refactoring**: Updated for YAML format and exclusion model
  - YAML loading/saving with `YAMLConfigLoader`
  - Exclusion management methods (`add_exclusion`, `remove_exclusion`, `is_excluded`)
  - Backward compatibility via `_to_legacy_format()` for existing consumers
- **ViewModel Updates**: Added `exclusions_changed` signal for UI synchronization
- **View Updates**: Updated table columns (Enabled→Included, Category→Tags)
  - Added filter input for application name, tags, or path search
- **TypedDict Definitions**: Updated for new format
  - `DotFileDict`: Removed `category`, `enabled`; added `tags`
  - Added `SessionDict` for exclusion persistence
  - Added `LegacyDotFileDict` for migration support

### Removed

- **CLI Application**: Removed `dfbu.py` command-line interface
  - CLI superseded by GUI application
  - Removed `tests/test_dfbu_cli.py` and `tests/test_dotfile_class.py`
- **TOML Configuration**: Replaced by YAML format
  - Removed `dfbu-config.toml`
  - Removed `tomllib` dependency

### Fixed

- **Test Coverage**: 376 tests passing after migration (84% coverage)
- **Documentation**: Updated all docs to reflect YAML format and exclusion model

- **AddDotfileDialog UI File**: Created Qt Designer .ui file for AddDotfileDialog with
  standardized naming
  - Added `gui/designer/add_dotfile_dialog.ui` for dialog interface
  - Added `gui/designer/main_window_complete.ui` with updated widget references
- **Protocol Definitions Module**: Comprehensive protocol interfaces for MVVM
  architecture
  - Added `gui/protocols.py` (502 lines) with ModelProtocol, ViewModelProtocol, and
    component protocols
  - Defined clear contracts between MVVM layers following Interface Segregation
    Principle
  - Type-safe interface definitions using Python's Protocol for better IDE support
- **Project Documentation Enhancements**:
  - Created comprehensive `scripts/README.md` documenting setup and utility scripts
  - Updated `CONTRIBUTING.md` with DFBU-specific guidelines and branch protection
    workflow
  - Added test coverage reports in `TEST_COVERAGE_REPORT.md`,
    `UI_INTEGRATION_CHECKLIST.md`, and `UI_INTEGRATION_SUMMARY.md`

### Changed

- **Widget Naming Convention**: Updated all UI widgets to follow lowerCamelCase naming
  convention
  - Standardized button, label, and widget naming for consistency
  - Updated widget references throughout View layer to match Qt Designer naming
  - Improved code readability and maintainability with consistent naming patterns
- **Configuration Updates**: Enhanced dotfile configuration with new application entries
  - Added Firefox, Qt Widget Designer, Librewolf, and Steam configurations
  - Removed obsolete custom dotfile entries
  - Updated configuration structure for better organization
- **Documentation Organization**: Moved documentation files to centralized `docs/`
  directory
  - Relocated BRANCH_PROTECTION.md, QUICKSTART.md, UI_DESIGN_GUIDE.md, and related docs
  - Improved project structure and documentation discoverability
- **MyPy Configuration**: Updated mypy.ini with improved type checking settings

### Fixed

- **UI Integration**: Resolved widget reference issues in main window and dialog
  components
- **Test Reliability**: Updated test files to reflect widget naming changes and improve
  reliability

### Security

## [0.6.0] - 2026-01-31

### Added

- **Pre-Restore Safety Feature**: Automatic backup of files before restore operations to
  prevent data loss
  - Added `RestoreBackupManager` component (`gui/restore_backup_manager.py`) for
    managing pre-restore backups
  - Timestamped backup directories at `~/.local/share/dfbu/restore-backups/`
  - TOML manifest files documenting what was backed up and why
  - Configurable retention policy (default: 5 backups)
  - Automatic cleanup of old backups exceeding retention limit
  - Directory structure preservation in backups
- **New Configuration Options**:
  - `pre_restore_backup` toggle in UI Configuration tab (default: enabled)
  - `max_restore_backups` setting for retention policy control
  - `restore_backup_dir` path configuration for backup location
- **Model Facade Method**: Added `execute_restore()` to DFBUModel for proper
  orchestration

### Changed

- **BackupOrchestrator Integration**: Restore operations now route through orchestrator
  with pre-restore backup
  - Added `pre_restore_enabled` parameter to `execute_restore()` method
  - Integrated `RestoreBackupManager` into restore workflow
- **UI Updates**: Configuration tab now includes pre-restore safety settings
  - Pre-restore backup checkbox toggle
  - Max restore backups spinbox (1-50 range)
  - Restore backup directory path field with browse button
- **Common Types**: Extended `OptionsDict` with `pre_restore_backup` and
  `max_restore_backups` fields

### Fixed

- **Critical**: RestoreWorker now uses `BackupOrchestrator.execute_restore()` instead of
  bypassing it with direct file operations - pre-restore backup was not executing during
  GUI restore
- **Encapsulation**: Added `backup_base_dir` setter to `RestoreBackupManager` for proper
  attribute access
- **Retention Policy**: Added `cleanup_old_backups()` call after successful pre-restore
  backup
- **DRY Violation**: Import `DEFAULT_BACKUP_DIR` constant from
  `restore_backup_manager.py` into `config_manager.py`
- **Documentation**: Updated `update_path()` docstring in protocols.py to include
  `restore_backup_dir`
- **Config Respect**: Pre-restore backup now respects the `pre_restore_backup` config
  option

## [0.5.8] - 2025-11-03

### Added

- **Centralized Input Validation Module**: Comprehensive validation framework for GUI
  inputs
  - Added `gui/input_validation.py` (282 lines) with `InputValidator` class and
    `ValidationResult` dataclass
  - Path validation with length checks (max 4096 chars) and character sanitization
  - String validation with configurable length limits (1-256 chars) and pattern matching
  - Numeric range validation with min/max bounds checking
  - Boolean validation with multiple format support ("yes/no", "true/false", "1/0")
  - Filename validation with illegal character detection using regex patterns
  - Type-safe validation with descriptive error messages for user feedback
- **Structured Logging Configuration**: Professional logging infrastructure with
  rotation and multiple handlers
  - Added `gui/logging_config.py` (135 lines) with centralized logging setup
  - Rotating file handler with 10MB max size and 5 backup files
  - Console handler for development with configurable log levels
  - Structured log format with timestamps, module names, function names, and line
    numbers
  - Log directory management in `~/.config/dfbu_gui/logs/`
  - Separate backup and restore log streams in UI for better operation tracking
- **Comprehensive Test Suite Extensions**: 330 total tests with extensive coverage (83%
  overall)
  - Added `tests/test_input_validation.py` (541 lines) with 95% coverage for validation
    module
  - Added `tests/test_logging_config.py` (319 lines) with 100% coverage for logging
    configuration
  - Added `tests/test_dialog_validation.py` (452 lines) for AddDotfileDialog input
    validation
  - Added `tests/test_table_sorting.py` (478 lines) for dotfile table sorting
    functionality
  - Added `tests/test_worker_signals.py` (534 lines) for worker thread signal testing
  - Added `tests/README.md` (462 lines) with comprehensive testing documentation
- **Enhanced Configuration Management**: Improved configuration validation and error
  handling
  - Configuration backups now stored with timestamps in `.dfbu-config.toml.backups/`
  - Enhanced TOML validation with better error reporting
  - Streamlined configuration file structure (reduced from 1891 to ~500 lines)

### Changed

- **GUI View Refactoring**: Major improvements to main window and dialog handling (329
  lines modified)
  - Integrated `InputValidator` for all user input fields in dialogs
  - Enhanced error message display with validation feedback
  - Improved table widget initialization and sorting behavior
  - Added `NumericTableWidgetItem` class for proper numeric sorting by file size
  - Refactored browse button handlers to use centralized validation
  - Updated signal connections for better separation of concerns
- **ViewModel Architecture**: Enhanced threading and signal handling (253 lines
  modified)
  - Refactored worker thread management for backup and restore operations
  - Improved progress tracking with separate item and file counters
  - Enhanced error signal propagation from workers to UI
  - Added item skipped signals for better user feedback
  - Improved worker cleanup and thread lifecycle management
- **Configuration Manager Enhancements**: Better config file handling (97 lines added)
  - Automatic configuration backup before save operations
  - Enhanced TOML parsing with detailed error messages
  - Improved default value handling for missing fields
  - Better path validation for mirror and archive directories
- **File Operations Updates**: Improved robustness (24 lines modified)
  - Enhanced error handling for file copy operations
  - Better symlink handling and metadata preservation
  - Improved directory creation with proper permission checks
- **Model Updates**: Better integration with validation (8 lines modified)
  - Updated to use `InputValidator` for path validation
  - Improved error propagation from orchestrator to viewmodel
- **Code Quality Improvements**: Enhanced type safety and documentation
  - Added `mypy.ini` configuration for strict type checking (100% compliance)
  - Removed unused imports and cleaned up validation module
  - Enhanced inline comments for better code readability
  - Updated file headers with current dates (11-03-2025)
- **Test Infrastructure**: Improved test organization and documentation
  - Enhanced test fixtures in `conftest.py` for better resource management
  - Removed redundant imports across multiple test files
  - Updated test assertions for improved clarity
  - Added comprehensive test documentation in `tests/README.md`

### Fixed

- **Configuration File Size**: Reduced config file bloat from 1891 to ~500 lines through
  optimization
- **Test Reliability**: Improved test stability with better fixture management (308
  passing, 2 skipped)
- **Validation Error Handling**: Enhanced error messages in validation module for user
  clarity
- **Path Validation**: Fixed edge cases in path expansion and sanitization
- **Worker Thread Cleanup**: Improved thread lifecycle management to prevent memory
  leaks

### Removed

- **Temporary Documentation Files**: Cleaned up outdated summary and status files
  - Removed `ENHANCEMENT_SUMMARY.md` (397 lines)
  - Removed `IMPLEMENTATION_COMPLETE.md` (320 lines)
  - Removed `TESTING_IMPLEMENTATION_SUMMARY.md` (456 lines)
  - Removed `TEST_SUMMARY_2025-11-02.md` (323 lines)
  - Removed `PROTECTION_STATUS.md` (obsolete)
- **Redundant Validation Code**: Consolidated duplicate validation logic into
  centralized module

## [0.5.7] - 2025-11-02

### Added

- **Comprehensive Testing Infrastructure**: Complete test suite with 217 tests achieving
  76% overall code coverage
  - Added `tests/test_backup_orchestrator.py` with 25 test cases covering
    initialization, validation, mirror/archive backups, and restore operations
  - Added `tests/test_config_validation.py` with 16 test cases for ConfigValidator
    options and dotfile validation
  - Added `tests/test_dfbu_cli.py` with 18 integration tests for CLI workflow and
    component integration
  - Added `tests/test_dotfile_class.py` with 9 test cases for DotFile initialization and
    path operations
  - Added `tests/test_model.py` with 27 comprehensive model tests covering config,
    dotfile, path, file operations, and statistics
  - Added `tests/test_model_additional_coverage.py` with 27 additional model tests for
    backup utilities, archives, and restore
  - Added `tests/test_model_file_operations.py` with 18 file operation tests including
    identity checks and confident code paths
  - Added `tests/test_view_comprehensive.py` with 25 view tests for dialogs, main
    window, and UI components
  - Added `tests/test_viewmodel_multiple_paths.py` with 12 ViewModel tests for
    categories and backup processing
  - Added `tests/test_viewmodel_template.py` with 10 example ViewModel tests
    demonstrating test patterns
  - Added `tests/test_workers_comprehensive.py` with 17 worker tests for BackupWorker
    and RestoreWorker threading
  - Configured pytest with `pyproject.toml` including testpaths, Qt plugin, and coverage
    settings
  - Added pytest fixtures in `conftest.py` for QApplication and temp config directory
- **Branch Protection System**: Comprehensive branch protection implementation
  - Added `.agents/branch_protection.py` - Python checker for AI agents to validate
    branch before file modifications
  - Added `BRANCH_PROTECTION.md` - Complete branch protection documentation with
    workflows and scenarios
  - Added `BRANCH_PROTECTION_QUICK.md` - Quick reference guide for developers and AI
    agents
  - Added `PROTECTION_STATUS.md` - Documentation of current protection implementation
    status
- **Development Documentation**: Enhanced contributing guidelines
  - Added `CONTRIBUTING.md` - Comprehensive development workflow, testing requirements,
    and style guidelines
  - Updated `.github/copilot-instructions.md` with mandatory strict type hint
    enforcement
  - Updated `AGENTS.md` with branch protection workflow integration

### Changed

- **Type Safety Enhancement**: Enforced mandatory type hints throughout entire codebase
  - All function parameters now have explicit type annotations
  - All function return values explicitly typed (including `-> None`)
  - All class attributes defined in `__init__` have type hints
  - Module-level variables and constants use `Final` type annotations
  - Updated to use modern Python 3.10+ syntax: `list[str]` instead of `List[str]`,
    `str | None` instead of `Optional[str]`
  - Used `collections.abc.Callable` for precise callback type hints
- **Test Infrastructure**: Improved pytest fixtures and configuration
  - Updated `conftest.py` to use `scope="session"` for QApplication fixture
  - Added proper cleanup handling in fixtures
  - Configured pytest-qt plugin for Qt-specific testing
  - Added `pytest-mock` for improved mocking capabilities
- **Coverage Reporting**: Configured comprehensive coverage tracking
  - Set up HTML coverage reports in `htmlcov/` directory
  - Configured terminal coverage output with missing line numbers
  - Coverage tracking for `gui/` and `core/` packages
  - Generated detailed coverage reports showing 76% overall coverage (gui/model.py:
    100%, gui/viewmodel.py: 63%, gui/view.py: 69%)

### Fixed

- **Test Reliability**: Fixed pytest fixtures to prevent QApplication-related test
  failures
  - Properly scoped QApplication fixture to session level
  - Added fallback for existing QApplication instance
  - Ensured proper cleanup between test runs

## [0.5.6] - 2025-11-01

### Fixed

- **GUI Blank Window Issue**: Resolved issue where main window displayed blank on
  startup
  - Fixed `MainWindow` initialization to properly load UI components
  - Corrected signal-slot connections for proper event handling
  - Updated window state restoration logic

### Changed

- **Code Refactoring**: Improved code organization and maintainability
  - Cleaned up unused imports and variables
  - Enhanced inline documentation
  - Updated file headers to current date

## [0.5.5] - 2025-11-01

### Changed

- **Documentation Enhancement**: Comprehensive inline comment additions to
  backup_orchestrator.py
  - Added descriptive comments for each significant code block following repository
    standards
  - Enhanced code readability with context explanations for complex logic
  - Improved AI autocompletion context with clear block-level documentation
  - Added shebang line to module header per repository standards
- **Header Updates**: Updated backup_orchestrator.py header to reflect current
  implementation

## [0.5.4] - 2025-11-01

### Fixed

- **BackupOrchestrator Progress Tracking**: Fixed progress calculation logic to
  accurately reflect completed items vs total items
  - Added `completed_items` counter separate from `processed_count` (which tracks files)
  - Progress now correctly updates based on completed dotfile entries, not individual
    file counts
  - Prevents progress bar jumping or freezing with large directories
- **FileOperations Error Handling**: Improved `copy_file()` method to properly handle
  and report copy failures
  - Added exception handling for both `Path.copy()` (Python 3.14) and `shutil.copy2()`
    fallback
  - Method now returns `False` on failure instead of always returning `True`
  - Catches `OSError` and `shutil.Error` exceptions to prevent silent failures
- **Archive Creation Robustness**: Enhanced `create_archive()` exception handling
  - Added individual file-level exception handling within archive creation loop
  - Catches `OSError`, `ValueError`, and `tarfile.TarError` per file to prevent partial
    archive failure
  - Archives now complete even if some files can't be added (symlink loops, permission
    issues, etc.)
- **CLI Copy Operations**: Added error handling to all `Path.copy()` operations in
  `dfbu.py`
  - Improved fallback exception handling for Python < 3.14 compatibility
  - Added error messages for failed copy operations in both backup and restore modes
  - Consistent error handling across file and directory processing

### Changed

- **Type Hints Enhancement**: Replaced generic `callable` type hints with precise
  `Callable[[...], ...]` from `collections.abc`
  - Updated all callback parameters in `BackupOrchestrator` class
  - Improved type safety and IDE autocomplete support
  - Specific signatures: `Callable[[int], None]` for progress,
    `Callable[[str, str], None]` for item callbacks
- **Date Format Constants**: Extracted hardcoded date formats into module-level
  constants
  - Added `DATE_FORMAT` constant: `"%Y-%m-%d"` for date subdirectories
  - Added `ARCHIVE_TIMESTAMP_FORMAT` constant: `"%Y-%m-%d_%H-%M-%S"` for archive
    filenames
  - Centralized format definitions in `file_operations.py` for consistency and
    maintainability
- **Import Organization**: Moved `import time` to top-level in `backup_orchestrator.py`
  (PEP 8 compliance)
- **Code Cleanup**: Removed unused loop variable `i` from `execute_mirror_backup()`
  enumerate call

### Added

- **Project Structure**: Moved `common_types.py` and `validation.py` to new `core/`
  subdirectory for better organization
- **Imports**: Updated all import statements to use `from core.common_types` and
  `from core.validation` patterns
- **Core Package**: Created `core/__init__.py` to expose shared utilities
  (`DotFileDict`, `OptionsDict`, `ConfigValidator`)

## [0.4.0] - 2025-11-01

### Added

- **Component Architecture**: Implemented Single Responsibility Principle by splitting
  DFBUModel into focused components
  - `ConfigManager` class (555 lines): Handles all configuration operations (I/O, TOML
    parsing, dotfile CRUD, validation)
  - `FileOperations` class (620 lines): Manages all file system operations (path
    expansion, copying, archives, restore)
  - `BackupOrchestrator` class (420 lines): Coordinates backup/restore operations with
    progress tracking
  - `StatisticsTracker` class (158 lines): Tracks operation metrics using
    BackupStatistics dataclass

### Changed

- **DFBUModel Refactoring**: Transformed from monolithic class (1,178 lines) to clean
  facade pattern (583 lines)
  - 50.5% code reduction (595 lines eliminated)
  - Now coordinates 4 focused components via delegation
  - Added property setters for `config_path`, `mirror_base_dir`, and `archive_base_dir`
    for backward compatibility
  - Maintains full API compatibility with existing ViewModel
- **Architecture Improvements**:
  - Implemented facade pattern for clean component composition
  - Dependency injection via expand_path callback from FileOperations to ConfigManager
  - Each component now has single, well-defined responsibility
- **Test Suite**: Improved to 277/282 passing (98.2% pass rate), 78% code coverage
- Updated Date Changed header to 2025-11-01

### Fixed

- Test expectations corrected for `validate_dotfile_paths` return signature (exists,
  is_dir, type_str)
- View signal connection test fixed to properly test signal connections

## [0.3.2] - 2025-11-01

### Added

- KDiff3 configuration paths for development utility support
- Krusader user actions configuration path for enhanced file manager functionality

### Changed

- Import organization improvements with proper ordering
- Enhanced type safety with strict parameter added to zip() calls
- Updated type hints for better code clarity
- Updated Date Changed header to 2025-11-01

### Fixed

- **ConfigValidator.validate_options() - Compression Level**: Fixed validation logic to
  properly default to 9 for out-of-range values (< 0 or > 9) instead of clamping to
  range boundaries
- **ConfigValidator.validate_options() - Max Archives**: Fixed validation logic to
  properly default to 5 for values below 1 instead of clamping to minimum of 1
- **Type Safety in Configuration Validation**: Added try-except blocks to handle invalid
  type conversions (e.g., string values) gracefully, defaulting to safe values
  (compression_level=9, max_archives=5)
- Configuration validation now properly handles edge cases: out-of-range integers,
  invalid types, and missing values

## [0.3.1] - 2025-10-31

### Added

### Changed

- **Documentation Update**: Comprehensive documentation review and standardization
- Updated all file headers to current date (2025-10-31) for documentation maintenance
- Enhanced project documentation organization following repository guidelines
- Standardized inline comments and docstring formatting across all modules
- Updated README.md to maintain minimal, human-readable content per guidelines
- Improved CHANGELOG.md formatting and version tracking accuracy
- Enhanced PROJECT-DOC.md files with current implementation details
- Updated GUI documentation to reflect latest MVVM implementation

### Deprecated

### Removed

### Fixed

- Corrected documentation inconsistencies across project files
- Updated version tracking in pyproject.toml and all module headers

### Security

## [0.3.0] - 2025-10-30

### Added

- **PathAssembler utility class**: Centralized path construction logic for backup
  destinations
- **ConfigValidator utility class**: Robust TOML configuration validation with type and
  range checking
- **MirrorBackup operation class**: Dedicated class for mirror backup operations
  encapsulation
- **ArchiveBackup operation class**: Dedicated class for archive creation and rotation
  operations
- **CLIHandler utility class**: Complete separation of CLI interaction from business
  logic
- Comprehensive validation for compression levels (0-9) and archive counts (>= 1)
- Type-safe configuration validation with sensible defaults for missing fields
- Dedicated methods for file and directory processing in backup operations

### Changed

- **Major Architecture Refactoring**: Implemented 4 key architecture improvements for
  better maintainability
- Separated CLI interaction from business logic using CLIHandler pattern
- Extracted path assembly logic to dedicated PathAssembler utility (~100 lines of
  duplication removed)
- Refactored backup operations into dedicated MirrorBackup and ArchiveBackup classes
- Enhanced configuration validation with ConfigValidator for robust error prevention
- Updated DotFile class to use PathAssembler for destination path construction
- Simplified Options class initialization with pre-validated configuration data
- All legacy functions now delegate to appropriate utility classes
- Improved code organization with clear separation of concerns
- Enhanced testability through isolated, focused classes
- Updated file header to reflect architecture improvements and new features
- Updated Date Changed to 2025-10-30

### Removed

- Duplicate path assembly methods (\_assemble_mirror_dest_path,
  \_assemble_archive_dest_path) from DotFile
- Redundant validation logic replaced with centralized ConfigValidator
- ~300+ lines of duplicated/redundant code through consolidation

### Fixed

- Inconsistent path construction logic now unified in PathAssembler
- Configuration validation gaps addressed with comprehensive ConfigValidator

## [0.2.2] - 2025-10-29

### Added

- FileSystemHelper utility class for eliminating DRY violations across codebase
- TypedDict definitions (DotFileDict, OptionsDict) for type-safe configuration handling
- Comprehensive type hints throughout entire codebase for all functions and classes
- Enhanced inline comments for improved code readability and AI context
- Detailed docstrings for all classes, methods, and functions following repository
  standards
- Full documentation updates reflecting current implementation state

### Changed

- Consolidated repeated patterns into FileSystemHelper static methods
- Refactored permission checking to use centralized FileSystemHelper.check_readable()
- Improved directory creation with unified FileSystemHelper.create_directory()
- Enhanced path expansion using consistent FileSystemHelper.expand_path()
- Updated all classes to use proper TypedDict types for configuration data
- Streamlined Options and DotFile initialization with validated typed dictionaries
- Improved docstring formatting and consistency across all code elements
- Enhanced MirrorBackup class with FileSystemHelper integration
- Improved ArchiveBackup class with consolidated helper methods
- Updated version to 0.2.2 reflecting code maturity
- Updated all documentation to reflect Linux-only compatibility
- Enhanced README.md with detailed architecture and dependency information
- Improved CHANGELOG.md formatting and version history accuracy

### Removed

- Duplicate code patterns for dry-run prefix formatting
- Redundant path expansion logic across multiple classes
- Repeated permission check patterns replaced with centralized helper
- Duplicate directory creation code eliminated through FileSystemHelper

## [0.2.1.dev1] - 2025-10-28

### Changed

- Updated version to 0.2.1.dev1 for continued development
- Updated documentation date references to reflect current development

## [0.2.0.dev1] - 2025-10-27

### Added

- **Dual-mode operation**: Interactive selection between backup and restore
  functionality
- **Restore functionality**: Complete implementation for restoring from hostname-based
  backup directories
- **Mode selection menu**: Interactive CLI menu for choosing backup vs. restore
  operations
- **Path resolution for restore**: Smart handling of hostname/home/root directory
  structures during restoration
- **Enhanced interactive workflow**: Separate confirmation prompts for backup and
  restore operations
- **Global DRY_RUN support**: Configurable dry-run mode for testing operations safely

### Changed

- Updated version to 0.2.0.dev1 for continued development
- Enhanced user workflow with dual-mode operation support
- Improved path handling for both backup and restore operations
- Updated documentation to reflect actual implementation vs. planned features
- Streamlined feature list in header to focus on implemented capabilities

### Fixed

- Corrected documentation to accurately reflect implemented vs. planned functionality
- Updated feature descriptions to match actual code implementation
- Clarified archive functionality status (configuration implemented, creation logic
  planned)

## [0.1.0.dev1] - 2025-10-27

### Added

- Initial version reset for major restructuring
- TOML configuration system replacing CSV-based configuration
- Options class for centralized backup configuration management
- Enhanced path handling with mirror_dir and archive_dir configuration
- Comprehensive dotfile metadata with category/subcategory/application structure
- Archive destination path support (implementation in progress)

### Changed

- Reset version numbering to align with development milestones
- Migrated from CSV to TOML configuration format using Python's tomllib
- Updated configuration file location to data/dfbu-config.toml
- Improved dotfile validation and path handling
- Enhanced user output with better formatting and color coding
- Updated documentation to reflect TOML configuration system

### Fixed

- Resolved configuration file parsing to use proper TOML format
- Improved path resolution for both home and root directory files
- Enhanced dotfile metadata validation and error reporting

## [0.4.2.dev1] - 2025-10-27 [SUPERSEDED]

### Added

- TOML configuration system replacing CSV-based configuration
- Options class for centralized backup configuration management
- Enhanced path handling with mirror_dir and archive_dir configuration
- Comprehensive dotfile metadata with category/subcategory/application structure
- Archive destination path support (implementation in progress)

### Changed

- Migrated from CSV to TOML configuration format using Python's tomllib
- Updated configuration file location to data/dfbu-config.toml
- Improved dotfile validation and path handling
- Enhanced user output with better formatting and color coding
- Updated documentation to reflect TOML configuration system

### Fixed

- Resolved configuration file parsing to use proper TOML format
- Improved path resolution for both home and root directory files
- Enhanced dotfile metadata validation and error reporting

## [0.4.1.dev1] - 2025-10-20

### Added

- Semantic versioning support with **version** variable
- Standardized changelog tracking

### Changed

- Updated version tracking to use semantic versioning format

## [0.4.0] - 2025-10-19

### Added

- CSV-driven configuration with Category/Subcategory/Application structure
- Hostname-based backup directory organization (~/GitHub/dotfiles/hostname/)
- Separate home and system file backup paths for clear organization
- Python 3.14 Path.copy() with symlink following and metadata preservation
- ANSI color-coded output using custom AnsiColor class from common_lib
- Interactive CLI menu integration with CLIMenu.ynq() for user confirmation
- Automatic directory creation and intelligent overwrite handling
- Comprehensive file existence checking and type detection

### Changed

- Migrated from defensive programming to confident design patterns
- Improved error handling and user feedback
- Enhanced terminal output with colorized status messages

### Fixed

- Resolved path handling issues for both home and system files
- Fixed metadata preservation during file copying operations
