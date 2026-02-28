# DFBU Architecture Documentation

**Version:** 1.2.0 **Author:** Chris Purcell **Email:** <chris@l3digital.net> **Last
Updated:** February 6, 2026 **License:** MIT

---

## Table of Contents

1. [Overview](#overview)
2. [Architectural Principles](#architectural-principles)
3. [MVVM Pattern](#mvvm-pattern)
4. [Component Architecture](#component-architecture)
5. [Data Flow](#data-flow)
6. [Threading Model](#threading-model)
7. [Signal/Slot Communication](#signalslot-communication)
8. [Type System](#type-system)
9. [Error Handling Strategy](#error-handling-strategy)
10. [Testing Architecture](#testing-architecture)

---

## Overview

DFBU implements a clean, modern architecture based on established design patterns and
SOLID principles.

- **GUI Application** (`dfbu_gui.py`): Desktop application using MVVM pattern with
  PySide6

This document covers the GUI architecture.

### Architecture Goals

1. **Separation of Concerns**: Clear boundaries between UI, business logic, and data
   management
2. **Testability**: Components designed for isolated testing without UI dependencies
3. **Maintainability**: Small, focused classes following Single Responsibility Principle
4. **Extensibility**: Open for extension without modifying existing code
5. **Type Safety**: Full type hint coverage with mypy compliance
6. **Performance**: Non-blocking UI through threaded operations

---

## Architectural Principles

### SOLID Principles

#### Single Responsibility Principle (SRP)

Each class has one clear purpose:

- **ConfigManager**: Configuration I/O and CRUD operations
- **FileOperations**: File system operations and path handling
- **BackupOrchestrator**: Backup/restore coordination and progress tracking
- **StatisticsTracker**: Operation metrics collection

#### Open/Closed Principle (OCP)

Components are open for extension but closed for modification:

- New backup strategies can be added without modifying existing code
- Validation rules can be extended without changing core validators
- New UI components can be added without modifying MainWindow structure

#### Liskov Substitution Principle (LSP)

Derived classes maintain base class contracts:

- `NumericTableWidgetItem` extends `QTableWidgetItem` while maintaining all expected
  behaviors
- Worker threads extend `QThread` with consistent lifecycle management

#### Interface Segregation Principle (ISP)

Focused interfaces prevent unnecessary dependencies:

- ViewModel exposes only methods needed by View
- Model facade provides only essential operations to ViewModel
- Component interfaces contain minimal required methods

#### Dependency Inversion Principle (DIP)

High-level modules depend on abstractions:

- ViewModel depends on Model interface, not concrete implementation
- Components use callback functions (abstractions) for notifications
- Validation uses protocol-based interfaces

### Confident Code Design

The codebase follows a **confident design philosophy**:

#### Validation at Boundaries

- Input validation occurs at architectural boundaries (ViewModel, configuration loading)
- Once validated, data flows through core components without defensive checks
- Trust architectural guarantees rather than repeated validation

#### Clean Execution Paths

- Core business logic executes confidently without scattered None checks
- Methods assume valid inputs based on boundary validation
- Reduced cognitive load by eliminating "just in case" conditionals

#### Pythonic Return Types

- Methods return `Path | None` instead of `tuple[Path | None, bool]`
- `None` indicates failure; explicit value indicates success
- Simpler error handling and more idiomatic Python

**Example:**

```python
# Confident design
def copy_file(src: Path, dest: Path) -> bool:
    """Copy file assuming src is validated at boundary."""
    src.copy(dest, follow_symlinks=True, preserve_metadata=True)
    return True

# Instead of defensive design
def copy_file(src: Path, dest: Path) -> tuple[Path | None, bool]:
    if not self.check_readable(src):  # Defensive check
        return None, False
    # ... copy logic
    return dest, True
```

### Error Handling Philosophy

DFBU v1.0.0 implements comprehensive error handling with:

- Structured error categorization and recovery strategies
- User-friendly error messages and guidance via RecoveryDialog
- Graceful degradation where possible
- Production-ready robustness with retry logic for transient failures

---

## MVVM Pattern

### Pattern Overview

```
┌─────────────────────────────────────────────┐
│                    View                      │
│  (MainWindow, AddDotfileDialog)             │
│  - UI presentation                           │
│  - User input capture                        │
│  - Display updates                           │
└────────────┬────────────────────────────────┘
             │ Signals/Slots
             ↓
┌─────────────────────────────────────────────┐
│                 ViewModel                    │
│            (DFBUViewModel)                   │
│  - Presentation logic                        │
│  - State management                          │
│  - Command handling                          │
│  - Worker thread management                  │
└────────────┬────────────────────────────────┘
             │ Method calls
             ↓
┌─────────────────────────────────────────────┐
│                   Model                      │
│         (DFBUModel - Facade)                 │
│  - Business logic coordination               │
│  - Component delegation                      │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┬──────────┬────────────┐
    ↓                 ↓          ↓            ↓
ConfigManager  FileOperations  BackupOrchestrator  StatisticsTracker
```

### Layer Responsibilities

#### View Layer (`view.py`)

**Purpose**: Pure UI presentation

**Responsibilities**:

- Create and manage UI widgets
- Display data from ViewModel
- Capture user input
- Connect signals to ViewModel slots
- Update UI based on ViewModel signals

**Restrictions**:

- ❌ NO business logic
- ❌ NO direct Model access
- ❌ NO data validation (beyond UI constraints)
- ❌ NO file operations
- ✅ ONLY UI state management

**Key Classes**:

- `MainWindow`: Main application window with tab interface
- `AddDotfileDialog`: Dialog for adding dotfile entries
- `ProfileDialog`: Profile create/edit dialog (v1.1.0+)
- `RecoveryDialog`: Recovery options dialog (v0.9.0+)
- `SizeWarningDialog`: File size warning dialog (v1.0.0+)
- `HelpDialog`: Help/documentation dialog (v1.0.0+)
- `TooltipManager`: Widget tooltip management (v1.0.0+)
- `NumericTableWidgetItem`: Custom widget for numeric sorting

#### ViewModel Layer (`viewmodel.py`)

**Purpose**: Presentation logic and coordination

**Responsibilities**:

- Expose properties and commands for View
- Manage worker threads for long operations
- Emit signals for View updates
- Coordinate Model operations
- Handle presentation state
- Settings persistence

**Restrictions**:

- ❌ NO widget creation or manipulation
- ❌ NO UI layout decisions
- ❌ NO direct user interaction
- ✅ MAY use Qt signals/slots
- ✅ MAY manage QThread workers

**Key Classes**:

- `DFBUViewModel`: Main ViewModel coordinating all operations
- `BackupWorker`: QThread for backup operations
- `RestoreWorker`: QThread for restore operations

#### Model Layer (`model.py`, components)

**Purpose**: Business logic and data management

**Responsibilities**:

- Implement business rules
- Manage data persistence
- Execute file operations
- Validate configuration
- Track operation statistics

**Restrictions**:

- ❌ NO Qt imports (except signals in facade)
- ❌ NO UI concerns
- ❌ NO presentation logic
- ✅ Pure Python business logic
- ✅ Data validation

**Key Classes**:

- `DFBUModel`: Facade coordinating components
- `ConfigManager`: Configuration management
- `FileOperations`: File system operations
- `BackupOrchestrator`: Backup/restore coordination
- `StatisticsTracker`: Operation metrics
- `ErrorHandler`: Structured error handling (v0.9.0+)
- `VerificationManager`: Backup integrity verification (v0.8.0+)
- `RestoreBackupManager`: Pre-restore safety backups (v0.6.0+)
- `SizeAnalyzer`: File size analysis and .dfbuignore support (v1.0.0+)
- `ProfileManager`: Named backup profile management (v1.1.0+)
- `BackupHistoryManager`: Backup operation history tracking (v1.2.0+)
- `PreviewGenerator`: Backup preview generation (v1.2.0+)

---

## Component Architecture

### DFBUModel (Facade Pattern)

**Lines of Code**: 1036

**Purpose**: Provide unified interface to all Model components

**Design Pattern**: Facade

**Components Coordinated**:

1. ConfigManager
2. FileOperations
3. BackupOrchestrator
4. StatisticsTracker
5. ErrorHandler (v0.9.0+)
6. VerificationManager (v0.8.0+)
7. RestoreBackupManager (v0.6.0+)
8. SizeAnalyzer (v1.0.0+)
9. ProfileManager (v1.1.0+)
10. BackupHistoryManager (v1.2.0+)
11. PreviewGenerator (v1.2.0+)

**Key Benefits**:

- Single entry point for ViewModel
- Backward compatible API
- Component coordination without tight coupling
- Clean delegation pattern

**Public API**:

```python
class DFBUModel:
    # Configuration operations
    def load_config(self) -> tuple[bool, str]: ...
    def save_config(self) -> tuple[bool, str]: ...
    def add_dotfile(self, dotfile: DotFileDict) -> bool: ...
    def update_dotfile(self, index: int, dotfile: DotFileDict) -> bool: ...
    def remove_dotfile(self, index: int) -> bool: ...
    def toggle_dotfile_enabled(self, index: int) -> bool: ...

    # File operations
    def expand_path(self, path_str: str) -> Path: ...
    def check_readable(self, path: Path) -> bool: ...
    def copy_file(self, src: Path, dest: Path) -> bool: ...
    def copy_directory(self, src: Path, dest: Path) -> bool: ...

    # Backup/restore operations
    def create_archive(self, source_dir: Path, ...) -> Path | None: ...
    def rotate_archives(self, archives_dir: Path, max_count: int) -> None: ...

    # Statistics
    def record_item_processed(self, ...) -> None: ...
    def reset_statistics(self) -> None: ...
```

### ConfigManager

**Lines of Code**: 821

**Purpose**: Configuration file management and CRUD operations

**Responsibilities**:

- Load/save YAML configuration files (settings.yaml, dotfiles.yaml, session.yaml)
- Parse and serialize configuration data with ruamel.yaml
- Dotfile CRUD operations (add, update, remove)
- Exclusion-based selection management
- Configuration backup rotation
- Validation integration

**Key Methods**:

```python
class ConfigManager:
    def load_config(self) -> tuple[bool, str]: ...
    def save_config(self) -> tuple[bool, str]: ...
    def add_dotfile(self, dotfile: DotFileDict) -> bool: ...
    def update_dotfile(self, index: int, dotfile: DotFileDict) -> bool: ...
    def remove_dotfile(self, index: int) -> bool: ...
    def add_exclusion(self, name: str) -> bool: ...
    def remove_exclusion(self, name: str) -> bool: ...
    def is_excluded(self, name: str) -> bool: ...
```

**Configuration Structure** (YAML - split across 3 files):

```yaml
# settings.yaml
paths:
  mirror_dir: ~/backups/mirror
  archive_dir: ~/backups/archives
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: true
  hostname_subdir: true
  archive_compression_level: 9
  max_archives: 5
  verify_after_backup: true

# dotfiles.yaml
Bash:
  description: Bash shell configuration
  paths: ~/.bashrc
  tags: shell, terminal

# session.yaml
excluded:
  - Firefox
  - Steam
```

### FileOperations

**Lines of Code**: 686

**Purpose**: All file system operations and path handling

**Responsibilities**:

- Path expansion (~ to /home/user)
- File/directory copying with metadata preservation
- Permission checking
- TAR.GZ archive creation
- Archive rotation
- File size calculation
- Restore path reconstruction
- File comparison (metadata-based)

**Key Methods**:

```python
class FileOperations:
    def expand_path(self, path_str: str) -> Path: ...
    def check_readable(self, path: Path) -> bool: ...
    def create_directory(self, path: Path) -> bool: ...
    def copy_file(self, src: Path, dest: Path) -> bool: ...
    def copy_directory(self, src: Path, dest: Path) -> bool: ...
    def create_archive(self, source_dir: Path, ...) -> Path | None: ...
    def rotate_archives(self, archives_dir: Path, max_count: int) -> None: ...
    def files_are_identical(self, file1: Path, file2: Path) -> bool: ...
    def calculate_path_size(self, path: Path) -> int: ...
```

**Python 3.14 Features**:

```python
# Use Path.copy() with metadata preservation (Python 3.14+)
src.copy(dest, follow_symlinks=True, preserve_metadata=True)

# Fallback for older Python
shutil.copy2(src, dest, follow_symlinks=True)
```

### BackupOrchestrator

**Lines of Code**: 553

**Purpose**: Coordinate backup and restore operations with progress tracking

**Responsibilities**:

- Mirror backup coordination
- Archive backup coordination
- Restore operation coordination
- Progress tracking with callbacks
- Dotfile path validation
- Statistics integration
- Skip identical files optimization

**Key Methods**:

```python
class BackupOrchestrator:
    def execute_mirror_backup(
        self,
        dotfiles: list[DotFileDict],
        progress_callback: Callable[[int], None],
        item_processed_callback: Callable[[str, str], None],
        item_skipped_callback: Callable[[str, str], None],
        skip_identical: bool = True
    ) -> None: ...

    def execute_archive_backup(
        self,
        source_dir: Path,
        archive_filename: str,
        progress_callback: Callable[[int], None]
    ) -> Path | None: ...

    def execute_restore(
        self,
        restore_files: list[tuple[Path, Path]],
        progress_callback: Callable[[int], None],
        item_processed_callback: Callable[[str, str], None]
    ) -> None: ...
```

**Callback Pattern**:

```python
# Progress callback: (current_percentage: int) -> None
def on_progress(percentage: int) -> None:
    print(f"Progress: {percentage}%")

# Item processed callback: (source_path: str, dest_path: str) -> None
def on_item_processed(source: str, dest: str) -> None:
    print(f"Copied: {source} -> {dest}")
```

### StatisticsTracker

**Lines of Code**: 153

**Purpose**: Track operation metrics and statistics

**Responsibilities**:

- Record processed/skipped/failed items
- Track file counts and sizes
- Calculate processing time
- Provide statistics snapshots
- Reset functionality

**Data Structure**:

```python
@dataclass
class BackupStatistics:
    """Statistics for backup/restore operations."""
    processed_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    total_size: int = 0
    processing_time: float = 0.0
```

**Key Methods**:

```python
class StatisticsTracker:
    def record_item_processed(self, size: int) -> None: ...
    def record_item_skipped(self) -> None: ...
    def record_item_failed(self) -> None: ...
    def reset_statistics(self) -> None: ...
    def get_statistics(self) -> BackupStatistics: ...
```

### ErrorHandler (v0.9.0+)

**Lines of Code**: 439

**Purpose**: Structured error handling with categorization and recovery suggestions

**Responsibilities**:

- Categorize errors by type (PERMISSION, NOT_FOUND, DISK_FULL, etc.)
- Determine retry eligibility for recoverable errors
- Provide user-friendly error messages
- Support recovery dialog integration
- Track error patterns and statistics

**Key Methods**:

```python
class ErrorHandler:
    def handle_error(self, exception: Exception, context: str) -> ErrorInfo: ...
    def categorize_error(self, exception: Exception) -> ErrorCategory: ...
    def is_retryable(self, error: ErrorInfo) -> bool: ...
    def get_recovery_suggestions(self, error: ErrorInfo) -> list[str]: ...
```

### VerificationManager (v0.8.0+)

**Lines of Code**: 356

**Purpose**: Backup integrity verification with configurable checks

**Responsibilities**:

- Verify file existence in backup destinations
- Size comparison between source and backup
- Optional hash verification (SHA-256)
- Generate verification reports
- Integration with backup completion workflow

**Key Methods**:

```python
class VerificationManager:
    def verify_backup(self, source: Path, backup: Path) -> VerificationResult: ...
    def verify_all(self, backup_dir: Path) -> list[VerificationResult]: ...
    def generate_report(self, results: list[VerificationResult]) -> str: ...
```

### RestoreBackupManager (v0.6.0+)

**Lines of Code**: 272

**Purpose**: Pre-restore safety backups to prevent data loss

**Responsibilities**:

- Create timestamped backups before restore operations
- Generate TOML manifest files documenting backups
- Enforce retention policy (configurable max backups)
- Automatic cleanup of old backups
- Directory structure preservation

**Key Methods**:

```python
class RestoreBackupManager:
    def create_backup(self, paths: list[Path]) -> Path: ...
    def cleanup_old_backups(self, max_count: int) -> None: ...
    def get_backup_history(self) -> list[BackupInfo]: ...
```

### SizeAnalyzer (v1.0.0+)

**Lines of Code**: ~200 (estimated)

**Purpose**: File size analysis and warnings before backup operations

**Responsibilities**:

- Calculate total and per-file sizes for backup selections
- Apply .dfbuignore patterns to exclude files
- Generate size warnings at configurable thresholds (10MB, 100MB, 1GB)
- Provide detailed size reports for user decisions
- Integration with backup workflow

**Key Methods**:

```python
class SizeAnalyzer:
    def analyze_size(self, paths: list[Path]) -> SizeReportDict: ...
    def should_warn(self, size_bytes: int) -> str | None: ...
    def apply_ignore_patterns(self, path: Path) -> bool: ...
```

### ProfileManager (v1.1.0+)

**Lines of Code**: 145

**Purpose**: Named backup profile management

**Responsibilities**:

- Create, save, and load named backup profiles
- Store dotfile exclusion lists per profile
- Store option overrides per profile (compression, verification, etc.)
- Switch between profiles for different backup scenarios
- Profile persistence in profiles.yaml

**Key Methods**:

```python
class ProfileManager:
    def create_profile(self, name: str, excluded: list[str], options: dict) -> bool: ...
    def load_profile(self, name: str) -> ProfileDict | None: ...
    def delete_profile(self, name: str) -> bool: ...
    def list_profiles(self) -> list[str]: ...
    def set_active_profile(self, name: str | None) -> None: ...
```

### BackupHistoryManager (v1.2.0+)

**Lines of Code**: 189

**Purpose**: Backup operation history tracking and dashboard metrics

**Responsibilities**:

- Record backup operation results (items backed up, size, duration, success status)
- Maintain persistent history in backup_history.yaml
- Calculate aggregate dashboard metrics (total backups, success rate, average size)
- Automatic history rotation (limited to 1000 entries)
- Provide recent backup history for display

**Key Methods**:

```python
class BackupHistoryManager:
    def record_backup(
        self,
        items_backed: int,
        size_bytes: int,
        duration_seconds: float,
        success: bool,
    ) -> None: ...
    def get_metrics(self) -> DashboardMetrics: ...
    def get_recent_history(self, count: int = 10) -> list[BackupHistoryEntry]: ...
    def get_entry_count(self) -> int: ...
```

### PreviewGenerator (v1.2.0+)

**Lines of Code**: 218

**Purpose**: Backup preview generation without executing actual backup

**Responsibilities**:

- Analyze source files and compare with existing backup
- Categorize files as new, changed, or unchanged
- Calculate total counts and sizes for preview
- Support progress callbacks for non-blocking UI updates
- Respect hostname and date subdirectory settings

**Key Methods**:

```python
class PreviewGenerator:
    def generate_preview(
        self,
        dotfiles: list[dict[str, Any]],
        hostname_subdir: bool,
        date_subdir: bool,
        progress_callback: Callable[[int], None] | None = None,
    ) -> BackupPreviewDict: ...
```

---

## Data Flow

### Configuration Loading Flow

```
1. User Action (View)
   └─> MainWindow.on_load_config_clicked()
       └─> Signal: viewmodel.command_load_config()

2. ViewModel Processing
   └─> DFBUViewModel.command_load_config()
       └─> model.load_config()

3. Model Processing (Facade)
   └─> DFBUModel.load_config()
       └─> config_manager.load_config()

4. Component Processing
   └─> ConfigManager.load_config()
       ├─> Read YAML files (settings.yaml, dotfiles.yaml, session.yaml)
       ├─> Parse configuration with ruamel.yaml
       ├─> Validate configuration
       └─> Return (success, message)

5. ViewModel Response
   └─> DFBUViewModel receives result
       ├─> Emit signal: config_loaded
       └─> Emit signal: status_message

6. View Update
   └─> MainWindow.on_config_loaded()
       ├─> Update dotfiles table
       ├─> Update options fields
       └─> Show status message
```

### Backup Operation Flow

```
1. User Action (View)
   └─> MainWindow.on_backup_clicked()
       └─> Signal: viewmodel.command_backup(mirror=True, archive=False)

2. ViewModel Processing
   └─> DFBUViewModel.command_backup()
       ├─> Validate configuration loaded
       ├─> Create BackupWorker thread
       ├─> Set worker parameters
       ├─> Connect worker signals
       └─> Start worker thread

3. Worker Thread Execution
   └─> BackupWorker.run()
       └─> model.backup_orchestrator.execute_mirror_backup()
           ├─> Callback: progress_updated signal
           ├─> Callback: item_processed signal
           ├─> Callback: item_skipped signal
           └─> On completion: backup_finished signal

4. View Updates (Real-time)
   └─> MainWindow receives signals
       ├─> on_progress_updated() -> Update progress bar
       ├─> on_item_processed() -> Update status text
       └─> on_backup_finished() -> Show completion message

5. Statistics Update
   └─> StatisticsTracker records metrics
       └─> ViewModel emits statistics_updated signal
           └─> View updates statistics display
```

---

## Threading Model

### Thread Architecture

DFBU uses Qt's threading model to prevent UI blocking during long-running operations.

**Main Thread**:

- UI rendering and event processing
- User input handling
- Signal/slot connections
- Lightweight ViewModel operations

**Worker Threads**:

- Backup operations (BackupWorker)
- Restore operations (RestoreWorker)
- File copying and archive creation
- Progress calculation

### Worker Thread Pattern

```python
class BackupWorker(QThread):
    """Worker thread for backup operations."""

    # Define signals for communication
    progress_updated = Signal(int)
    item_processed = Signal(str, str)
    error_occurred = Signal(str, str)

    def run(self) -> None:
        """Main thread execution (runs in worker thread)."""
        try:
            # Long-running operation
            self.model.backup_orchestrator.execute_mirror_backup(
                dotfiles=self.dotfiles,
                progress_callback=self._on_progress,
                item_processed_callback=self._on_item_processed
            )
        except Exception as e:
            self.error_occurred.emit("Backup", str(e))

    def _on_progress(self, percentage: int) -> None:
        """Emit progress signal (thread-safe)."""
        self.progress_updated.emit(percentage)
```

### Thread Safety

**Thread-Safe Operations**:

- Qt signal emissions (always thread-safe)
- Read-only Model operations
- Statistics recording (atomic operations)

**Non-Thread-Safe Operations**:

- ❌ Direct widget updates from worker threads
- ❌ Modifying shared state without locks
- ❌ File operations without proper locking

**Best Practices**:

```python
# ✅ Correct: Emit signal from worker thread
self.progress_updated.emit(50)

# ❌ Wrong: Update widget from worker thread
self.progress_bar.setValue(50)  # Will crash!
```

---

## Signal/Slot Communication

### Qt Signal/Slot Pattern

Signals and slots provide loose coupling between components.

**Benefits**:

- Decoupled communication
- Type-safe connections
- Thread-safe across boundaries
- Reactive programming model

### ViewModel Signals

```python
class DFBUViewModel(QObject):
    """ViewModel signals for View updates."""

    # Configuration signals
    config_loaded = Signal()
    config_saved = Signal()
    dotfile_added = Signal(int)  # index
    dotfile_updated = Signal(int)  # index
    dotfile_removed = Signal(int)  # index

    # Operation signals
    backup_started = Signal()
    backup_progress = Signal(int)  # percentage
    backup_finished = Signal(bool)  # success

    restore_started = Signal()
    restore_progress = Signal(int)
    restore_finished = Signal(bool)

    # Status signals
    status_message = Signal(str)
    error_message = Signal(str, str)  # title, message

    # Statistics signals
    statistics_updated = Signal(dict)
```

### View Signal Connections

```python
class MainWindow(QMainWindow):
    """Main window with signal connections."""

    def _connect_signals(self) -> None:
        """Connect ViewModel signals to View slots."""
        # Configuration signals
        self.viewmodel.config_loaded.connect(self.on_config_loaded)
        self.viewmodel.config_saved.connect(self.on_config_saved)

        # Progress signals
        self.viewmodel.backup_progress.connect(self.on_progress_updated)

        # Status signals
        self.viewmodel.status_message.connect(self.on_status_message)
        self.viewmodel.error_message.connect(self.on_error_message)

        # Button clicks (View -> ViewModel)
        self.backup_button.clicked.connect(
            lambda: self.viewmodel.command_backup(mirror=True)
        )
```

---

## Type System

### Type Hint Standards

**Mandatory Type Hints** (100% coverage):

- All function parameters
- All function return values (including `-> None`)
- All class attributes in `__init__`
- Module-level variables and constants

**Modern Python 3.10+ Syntax**:

```python
# ✅ Use new syntax
from typing import Final
from collections.abc import Callable

def process(items: list[str]) -> dict[str, int]: ...
value: str | None = None
callback: Callable[[int], None] = lambda x: None
MAX_SIZE: Final[int] = 1000

# ❌ Don't use old syntax
from typing import List, Dict, Optional, Callable as CallableType

def process(items: List[str]) -> Dict[str, int]: ...
value: Optional[str] = None
```

### TypedDict Definitions

```python
from typing import TypedDict

class DotFileDict(TypedDict):
    """Type definition for dotfile configuration entry."""
    category: str
    subcategory: str
    application: str
    source_path: str
    enabled: bool

class OptionsDict(TypedDict):
    """Type definition for backup options."""
    hostname: str
    mirror_base_dir: str
    archive_base_dir: str
    compression_level: int
    max_archives: int
```

### Type Checking

```bash
# Run mypy type checker
mypy DFBU/

# Strict mode enabled in mypy.ini
[mypy]
python_version = 3.14
strict = True
warn_return_any = True
warn_unused_configs = True
```

---

## Error Handling Strategy

### Current Approach (v0.9.0+)

**Philosophy**: Structured error handling with categorization and recovery

**Error Handling Features**:

1. **Error Categorization**: Errors classified by type (PERMISSION, NOT_FOUND,
   DISK_FULL, NETWORK, etc.)
2. **Recovery Dialogs**: UI-integrated error recovery with user choices (Retry, Skip,
   Abort)
3. **Retry Logic**: Automatic retry for transient failures with configurable attempts
4. **User-Friendly Messages**: Detailed error explanations with remediation suggestions
5. **Logging**: Comprehensive logging for debugging and audit trails

**Error Flow**:

```python
# ErrorHandler categorizes and provides recovery options
error_info = error_handler.handle_error(exception, context="backup")
if error_info.is_retryable:
    # Show recovery dialog with Retry/Skip/Abort options
    recovery_dialog.show(error_info)
else:
    # Log and continue with graceful degradation
    logger.error(f"{error_info.category}: {error_info.message}")
```

**Error Categories**:

- `PERMISSION`: Access denied errors → Suggest permission fixes
- `NOT_FOUND`: Missing files/directories → Skip or verify paths
- `DISK_FULL`: Storage exhausted → Free space or change destination
- `NETWORK`: Connection issues → Retry with backoff
- `UNKNOWN`: Unexpected errors → Log details for debugging

---

## Testing Architecture

### Test Organization

```
DFBU/tests/                          # 25 test files, 553 test functions
├── conftest.py                      # Pytest configuration & fixtures
├── test_model*.py                   # Model unit tests (3 files)
├── test_viewmodel_*.py              # ViewModel tests (4 files)
├── test_view_comprehensive.py       # View tests
├── test_backup_orchestrator.py      # Backup coordination tests
├── test_config_*.py                 # Config manager & validation tests
├── test_error_handler.py            # Error handling tests
├── test_verification_manager.py     # Verification tests
├── test_recovery_dialog*.py         # Recovery dialog tests (2 files)
├── test_worker*.py                  # Worker thread tests (2 files)
└── test_*.py                        # Additional component tests
```

### Test Markers

```python
@pytest.mark.unit          # Fast, isolated tests
@pytest.mark.integration   # Multi-component tests
@pytest.mark.gui          # Qt/GUI tests
@pytest.mark.slow         # Tests taking > 1 second
```

### Testing Patterns

**Model Testing** (Pure Python):

```python
def test_model_configuration(tmp_path):
    """Test model configuration loading."""
    # Arrange
    config_path = tmp_path / "config.toml"
    model = DFBUModel(config_path)

    # Act
    success, message = model.load_config()

    # Assert
    assert success is True
    assert model.options is not None
```

**ViewModel Testing** (Qt Signals):

```python
def test_viewmodel_signal_emission(qtbot):
    """Test viewmodel emits signals correctly."""
    # Arrange
    viewmodel = DFBUViewModel(model)

    # Act & Assert
    with qtbot.waitSignal(viewmodel.config_loaded, timeout=1000):
        viewmodel.command_load_config()
```

**View Testing** (Optional):

```python
def test_main_window_initialization(qapp, viewmodel):
    """Test main window initializes correctly."""
    # Act
    window = MainWindow(viewmodel, "1.0.0")

    # Assert
    assert window.viewmodel == viewmodel
    assert "DFBU GUI" in window.windowTitle()
```

### Coverage Goals

- **Overall**: 82% coverage (current)
- **Model Layer**: 95%+ coverage
- **ViewModel Layer**: 90%+ coverage
- **View Layer**: 70%+ coverage
- **Test Count**: 553 tests across 25 files

---

## Summary

DFBU's architecture demonstrates:

1. **Clean Separation**: MVVM pattern with clear layer boundaries
2. **SOLID Principles**: Single responsibility, dependency inversion
3. **Protocol-Based DI**: Type-safe dependency injection via Python Protocols
4. **Structured Error Handling**: Categorized errors with recovery options (v0.9.0+)
5. **Backup Verification**: Integrity checking with size/hash comparison (v0.8.0+)
6. **Type Safety**: Full type hint coverage with mypy compliance
7. **Testability**: 82% coverage with 553 tests across 25 files
8. **Performance**: Non-blocking UI through threaded operations
9. **Maintainability**: Small, focused components (all < 860 lines)

This architecture supports both current development needs and future extensibility while
maintaining code quality and developer experience.

---

**See Also**:

- [README.md](../../README.md) - Project overview
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Development guidelines
- [Test Suite README](../tests/README.md) - Testing documentation
- [Documentation Index](../../docs/INDEX.md) - Complete documentation guide
