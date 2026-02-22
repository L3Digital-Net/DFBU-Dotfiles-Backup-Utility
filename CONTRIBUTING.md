<!-- @format -->

# Contributing to DFBU - DotFiles Backup Utility

Thank you for your interest in contributing to DFBU! This guide will help you get
started.

## Development Setup

### Prerequisites

- Python 3.14+
- Git
- Linux operating system
- Basic understanding of PySide6 and MVVM architecture
- UV package manager (optional but recommended)

### Initial Setup

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility.git
   cd DFBU-DotFiles-Backup-Utility
   ```

2. Run the setup script (installs UV, creates venv, installs dependencies):

   ```bash
   ./scripts/setup.sh
   ```

3. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

## Architecture Guidelines

This project follows strict architectural principles:

### MVVM Pattern

- **Models** (`DFBU/gui/model.py`, `DFBU/gui/*_*.py` components): Pure Python business
  logic (some Qt in facade)
- **ViewModels** (`DFBU/gui/viewmodel.py`): QObject-based, signals for state changes
- **Views** (`DFBU/gui/view.py`): PySide6 widgets, minimal logic

### Component Architecture

The Model layer uses a **Facade pattern** to coordinate specialized components:

- **DFBUModel**: Facade providing unified API to ViewModel
- **ConfigManager**: Configuration file I/O and YAML management
- **FileOperations**: File system operations and path handling
- **BackupOrchestrator**: Backup/restore coordination with progress tracking
- **StatisticsTracker**: Operation metrics and statistics collection

### SOLID Principles

All code must adhere to SOLID principles:

- **S**ingle Responsibility
- **O**pen/Closed
- **L**iskov Substitution
- **I**nterface Segregation
- **D**ependency Inversion

For comprehensive architecture documentation including detailed MVVM patterns, component
interactions, and design decisions, see
[DFBU/docs/ARCHITECTURE.md](DFBU/docs/ARCHITECTURE.md).

## Development Workflow

### 0. Check Branch Protection

**CRITICAL**: Always work on `testing` branch, never modify `main` directly.

```bash
# Check current branch before modifications
python .agents/branch_protection.py

# Switch to testing branch if needed
git checkout testing
```

See [docs/BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md) for full details.

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Write Tests First (TDD)

```bash
# Create test file in DFBU/tests/
touch DFBU/tests/test_your_feature.py

# Write tests
# Run tests (they should fail initially)
pytest DFBU/tests/test_your_feature.py
```

### 3. Implement Feature

Follow the MVVM structure:

```bash
# For Model components (if needed)
touch DFBU/gui/your_component.py

# For ViewModel changes
# Edit DFBU/gui/viewmodel.py

# For View changes
# Edit DFBU/gui/view.py
```

### 4. Run Tests

```bash
# All tests
pytest DFBU/tests/

# With coverage
pytest DFBU/tests/ --cov=DFBU --cov-report=html

# Specific test file
pytest DFBU/tests/test_your_feature.py -v
```

### 5. Code Quality Checks

```bash
# Type checking (MANDATORY - conservative configuration)
mypy DFBU/
# See .mypy-strict-config.md for details on strict settings

# Optional: Format code
black DFBU/
isort DFBU/

# Optional: Linting
pylint DFBU/
```

### 6. Commit Changes

Follow conventional commit format:

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in component"
git commit -m "docs: update README"
git commit -m "test: add tests for feature"
```

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Standards

### Type Hints (MANDATORY - STRICT ENFORCEMENT)

**CRITICAL**: Type hints are MANDATORY for ALL code, not optional guidelines.

**Required type hints:**

- ✅ **ALL** function parameters (including `self` when helpful)
- ✅ **ALL** function return values (including `None` and `-> None`)
- ✅ **ALL** class attributes defined in `__init__`
- ✅ **ALL** module-level variables and constants

**Modern Python 3.10+ syntax:**

```python
from typing import Final
from collections.abc import Callable

# ✅ Correct
def process_data(items: list[str], config: dict[str, Any] | None = None) -> bool:
    """Process data with optional configuration."""
    return True

value: str | None = None
MAX_SIZE: Final[int] = 1000

# ❌ Wrong - old syntax
from typing import List, Dict, Optional

def process_data(items: List[str], config: Optional[Dict] = None) -> bool:
    return True
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> dict:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Dictionary containing results.

    Raises:
        ValueError: If param2 is negative.
    """
```

### Testing

For comprehensive testing documentation including fixtures, markers, and coverage
requirements, see [DFBU/tests/README.md](DFBU/tests/README.md).

Key testing principles:

- Use Arrange-Act-Assert pattern
- One assertion per test (when possible)
- Descriptive test names: `test_should_X_when_Y` or `test_component_action_result`
- Mock external dependencies
- Use `pytest-qt` for Qt signal testing

Example:

```python
def test_viewmodel_emits_signal_when_data_loaded(qtbot, mocker):
    # Arrange
    mock_model = mocker.Mock()
    mock_model.load_data.return_value = ["item1"]
    vm = DFBUViewModel(mock_model)

    # Act & Assert
    with qtbot.waitSignal(vm.data_loaded, timeout=1000):
        vm.command_load_data()

    mock_model.load_data.assert_called_once()
```

## What to Contribute

### Good Contributions

✅ Bug fixes with tests ✅ New features following MVVM/SOLID ✅ Documentation
improvements ✅ Test coverage improvements ✅ Performance optimizations ✅ Example
implementations

### Changes That Need Discussion

⚠️ Breaking API changes ⚠️ New dependencies ⚠️ Architecture changes ⚠️ Major refactoring

Please open an issue first to discuss these.

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Working on `testing` branch (NOT `main`)
- [ ] Code follows MVVM architecture
- [ ] SOLID principles maintained
- [ ] All tests pass (`pytest DFBU/tests/`)
- [ ] New features have tests
- [ ] Type hints added to all functions
- [ ] Docstrings added to public APIs (Google or NumPy style)
- [ ] Type checking passes (`mypy DFBU/`)
- [ ] Test coverage is 80%+ on new code
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventional format

## Running the Full Check Suite

```bash
# Run tests with coverage
pytest DFBU/tests/ --cov=DFBU --cov-report=html

# Type check
mypy DFBU/

# Optional: Format code
black DFBU/
isort DFBU/

# Optional: Lint
pylint DFBU/

# Run GUI application
cd DFBU
python dfbu_gui.py
```

## Directory Structure

```text
DFBU-DotFiles-Backup-Utility/
├── DFBU/                           # Main application directory
│   ├── dfbu_gui.py                 # GUI application entry point
│   ├── requirements.txt            # Python dependencies
│   ├── data/
│   │   ├── settings.yaml           # Application settings
│   │   ├── dotfiles.yaml           # Dotfile library
│   │   ├── session.yaml            # Session exclusions
│   │   └── .dfbuignore             # Size analysis exclusion patterns
│   ├── gui/                        # GUI components (MVVM)
│   │   ├── model.py                # Model facade
│   │   ├── viewmodel.py            # Presentation logic
│   │   ├── view.py                 # PySide6 UI
│   │   ├── config_manager.py       # Configuration management
│   │   ├── file_operations.py      # File system operations
│   │   ├── backup_orchestrator.py  # Backup/restore coordination
│   │   ├── statistics_tracker.py   # Operation metrics
│   │   ├── error_handler.py        # Structured error handling
│   │   ├── verification_manager.py # Backup integrity verification
│   │   ├── restore_backup_manager.py # Pre-restore safety backups
│   │   ├── size_analyzer.py        # File size analysis
│   │   ├── backup_history.py       # Backup operation history
│   │   ├── profile_manager.py      # User profile management
│   │   ├── preview_generator.py    # Backup preview generation
│   │   ├── protocols.py            # Protocol interfaces for DI
│   │   ├── input_validation.py     # Input validation framework
│   │   ├── config_workers.py       # QThread workers
│   │   ├── logging_config.py       # Logging configuration
│   │   ├── constants.py            # Application constants
│   │   ├── theme.py                # Color palette, spacing, typography
│   │   ├── theme_loader.py         # QSS stylesheet loader
│   │   ├── help_dialog.py          # Help/documentation dialog
│   │   ├── profile_dialog.py       # Profile create/edit dialog
│   │   ├── recovery_dialog.py      # Recovery options dialog
│   │   ├── size_warning_dialog.py  # File size warning dialog
│   │   ├── tooltip_manager.py      # Widget tooltip management
│   │   ├── styles/                 # QSS theme stylesheets
│   │   │   ├── dfbu_light.qss      # Light theme
│   │   │   └── dfbu_dark.qss       # Dark theme
│   │   └── designer/               # Qt Designer .ui files
│   ├── core/                       # Shared utilities
│   │   ├── common_types.py         # TypedDict definitions
│   │   └── yaml_config.py          # YAML config loading/saving
│   ├── resources/
│   │   ├── help/                   # Help content (HTML)
│   │   └── icons/                  # Application icons
│   ├── tests/                      # Test suite
│   │   ├── README.md               # Testing documentation
│   │   ├── conftest.py             # Pytest fixtures
│   │   └── test_*.py               # Unit/integration tests
│   └── docs/                       # Project documentation
│       ├── ARCHITECTURE.md         # MVVM architecture docs
│       └── CHANGELOG.md            # Version history
├── .github/
│   ├── copilot-instructions.md     # GitHub Copilot guidelines
│   └── workflows/                  # CI/CD workflows
├── .agents/                        # AI agent tools
│   ├── memory.instruction.md       # Coding preferences
│   └── branch_protection.py        # Branch protection checker
├── docs/                           # Top-level documentation
│   ├── INDEX.md                    # Documentation index
│   ├── BRANCH_PROTECTION.md        # Branch protection rules
│   └── plans/                      # Implementation plans
├── scripts/                        # Setup and utility scripts
├── AGENTS.md                       # Quick agent reference
├── CLAUDE.md                       # Claude Code instructions
├── CONTRIBUTING.md                 # This file
├── README.md                       # Project overview
└── pyproject.toml                  # Project configuration
```

## Common Patterns

See `AGENTS.md` for:

- File templates
- Testing patterns
- Signal/slot patterns
- Dependency injection examples
- Troubleshooting guide

## Getting Help

- Check [docs/INDEX.md](docs/INDEX.md) for a complete documentation guide
- Check [AGENTS.md](AGENTS.md) for quick reference and templates
- Review [DFBU/docs/ARCHITECTURE.md](DFBU/docs/ARCHITECTURE.md) for architecture details
- Review [DFBU/tests/README.md](DFBU/tests/README.md) for testing documentation
- Review `.github/copilot-instructions.md` for AI coding guidelines
- Review existing code for patterns
- Open an issue for questions
- Join discussions in pull requests

## License

By contributing, you agree that your contributions will be licensed under the same
license as the project.

## Questions?

Feel free to open an issue for any questions or clarifications!
