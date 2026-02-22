<!-- @format -->

# GitHub Copilot Instructions - DFBU DotFiles Backup Utility

## Project Overview

DFBU is a Python 3.14+ Linux desktop application for configuration file
backup/restoration with a PySide6 GUI. Uses UV for package management.

**Version:** 1.2.0 | **License:** MIT | **Architecture:** MVVM with Facade pattern

## Critical: Branch Protection

**NEVER modify files on `main` branch. Always work on `testing` branch.**

```bash
python .agents/branch_protection.py   # Verify before any modifications
```

## Architecture: MVVM with Facade Pattern

```text
View (view.py) ↔ signals/slots ↔ ViewModel (viewmodel.py) ↔ Model (model.py - Facade)
                                                                    ↕ delegates to
Components:
├── ConfigManager (config_manager.py)           # Config I/O, YAML, CRUD
├── FileOperations (file_operations.py)         # Path handling, copying, archives
├── BackupOrchestrator (backup_orchestrator.py) # Backup/restore coordination
├── StatisticsTracker (statistics_tracker.py)   # Operation metrics
├── RestoreBackupManager (restore_backup_manager.py) # Pre-restore safety backups
├── VerificationManager (verification_manager.py)    # Backup integrity verification
├── ErrorHandler (error_handler.py)             # Structured error handling
├── SizeAnalyzer (size_analyzer.py)             # File size analysis, .dfbuignore
├── BackupHistoryManager (backup_history.py)    # Backup operation history
├── ProfileManager (profile_manager.py)         # User profile management
└── PreviewGenerator (preview_generator.py)     # Backup preview generation

Dialogs & UI Helpers:
├── ProfileDialog (profile_dialog.py)           # Profile create/edit dialog
├── RecoveryDialog (recovery_dialog.py)         # Recovery options dialog
├── SizeWarningDialog (size_warning_dialog.py)  # File size warning dialog
├── HelpDialog (help_dialog.py)                 # Help/documentation dialog
└── TooltipManager (tooltip_manager.py)         # Widget tooltip management

Infrastructure:
├── LoggingConfig (logging_config.py)           # Logging setup
├── Constants (constants.py)                    # Application constants
├── Theme (theme.py)                            # Color palette, spacing, typography
└── ThemeLoader (theme_loader.py)               # QSS stylesheet loader
```

### Layer Rules (Non-Negotiable)

| Layer         | Allowed                                                      | Forbidden                                                 |
| ------------- | ------------------------------------------------------------ | --------------------------------------------------------- |
| **Model**     | Pure Python, dataclasses, business logic, validation         | Qt imports, UI concerns                                   |
| **ViewModel** | QObject, signals/slots, presentation logic, state management | Direct widget manipulation, business logic                |
| **View**      | Loading .ui files, PySide6 widgets, signal connections       | Hardcoded UI layouts, business logic, direct model access |

### Key Design Constraints

- **UI from `.ui` files only** — Load via `QUiLoader` from `DFBU/gui/designer/`, NEVER
  hardcode layouts
- **Dependencies injected** — Components implement Protocol interfaces
  (`DFBU/gui/protocols.py`)
- **Signals for cross-layer communication** — No direct method calls between layers
- **Long operations on QThread** — See `DFBU/gui/config_workers.py` for patterns

## Code Standards

### Type Hints (Mandatory - Strict Enforcement)

Modern Python 3.10+ syntax required on ALL functions, parameters, return values, and
class attributes:

```python
# ✅ Correct
def process(items: list[str], config: dict[str, Any] | None = None) -> bool: ...

# ❌ Wrong — old typing syntax
from typing import List, Optional
def process(items: List[str], config: Optional[Dict] = None) -> bool: ...
```

### Threading Pattern

```python
class ConfigLoadWorker(QThread):
    progress_updated = Signal(int)
    load_finished = Signal(bool, str, int)

    def run(self) -> None:
        self.progress_updated.emit(10)
        success, error = self.config_manager.load_config()
        self.progress_updated.emit(100)
        self.load_finished.emit(success, error, count)
```

### Testing Pattern (AAA with pytest-qt)

```python
def test_viewmodel_emits_signal(qtbot, mocker):
    # Arrange
    mock_service = mocker.Mock()
    mock_service.fetch.return_value = ["item1", "item2"]
    vm = DataViewModel(mock_service)

    # Act
    with qtbot.waitSignal(vm.data_loaded, timeout=1000) as blocker:
        vm.load_data()

    # Assert
    assert blocker.args[0] == ["item1", "item2"]
    mock_service.fetch.assert_called_once()
```

Test markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.gui`,
`@pytest.mark.slow`

## Essential Commands

```bash
# Run
python DFBU/dfbu_gui.py

# Test
pytest DFBU/tests/                                # All tests
pytest DFBU/tests/ -m unit                        # Unit tests only
pytest DFBU/tests/ --cov=DFBU --cov-report=html   # With coverage

# Type check (must pass with 0 errors)
mypy DFBU/
```

## Shared Types

`DFBU/core/common_types.py` defines `TypedDict` classes: `DotFileDict`, `OptionsDict`,
`VerificationResultDict`, `OperationResultDict`, `PathResultDict`, `SizeReportDict`.

## Configuration Files (DFBU/data/)

- **settings.yaml** — Application settings (paths, backup options)
- **dotfiles.yaml** — Dotfile library (application entries with paths and tags)
- **session.yaml** — Runtime exclusions
- **.dfbuignore** — Patterns for size analysis exclusion

## Key Files

| File                             | Purpose                                                             |
| -------------------------------- | ------------------------------------------------------------------- |
| `DFBU/gui/protocols.py`          | Protocol interfaces for dependency injection                        |
| `DFBU/gui/config_workers.py`     | Worker thread implementations                                       |
| `DFBU/core/common_types.py`      | Shared TypedDict definitions                                        |
| `DFBU/core/yaml_config.py`       | YAML config loading/saving with schema validation                   |
| `DFBU/gui/input_validation.py`   | Input validation framework                                          |
| `DFBU/gui/theme.py`              | Centralized color palette (DFBUColors), spacing, typography         |
| `DFBU/gui/theme_loader.py`       | QSS stylesheet loader                                               |
| `DFBU/gui/styles/dfbu_light.qss` | Qt Style Sheet — branded light theme                                |
| `DFBU/gui/styles/dfbu_dark.qss`  | Qt Style Sheet — dark theme                                         |
| `DFBU/resources/help/`           | Externalized help content (quick_start.html, config_reference.html) |
| `DFBU/tests/conftest.py`         | Pytest fixtures for Qt and file testing                             |

## References

- [DFBU/docs/ARCHITECTURE.md](../DFBU/docs/ARCHITECTURE.md) — Comprehensive architecture
  documentation
- [DFBU/tests/README.md](../DFBU/tests/README.md) — Testing documentation and fixtures
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Development setup and guidelines
- [docs/BRANCH_PROTECTION.md](../docs/BRANCH_PROTECTION.md) — Branch protection rules
- [.agents/memory.instruction.md](../.agents/memory.instruction.md) — Coding preferences
