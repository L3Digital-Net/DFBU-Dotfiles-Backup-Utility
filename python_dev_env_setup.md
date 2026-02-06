<!-- @format -->

# Python Development Environment Setup

A comprehensive guide to configuring VS Code and Python tooling for AI agent development. This setup maximizes code quality, type safety, and agent reliability through proper tooling integration.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Recommended Repo Layout](#recommended-repo-layout)
4. [Project Setup with uv](#project-setup-with-uv)
5. [Python Version Management](#python-version-management)
6. [pyproject.toml Configuration](#pyprojecttoml-configuration)
7. [VS Code Configuration](#vs-code-configuration)
8. [VS Code Extensions](#vs-code-extensions)
9. [Type Stubs for Third-Party Libraries](#type-stubs-for-third-party-libraries)
10. [Pre-commit Setup](#pre-commit-setup)
11. [Testing Integration](#testing-integration)
12. [Running Tools Manually](#running-tools-manually)
13. [Recommended Agent Workflow](#recommended-agent-workflow)
14. [Performance Tuning](#performance-tuning)
15. [GitHub Actions CI](#github-actions-ci)
16. [Troubleshooting](#troubleshooting)
17. [Quick Start](#quick-start)
18. [Additional Resources](#additional-resources)

---

## Overview

This guide provides a complete Python development environment optimized for AI coding agents, including:

- **Project Management**: uv for fast, reproducible environments
- **VS Code Configuration**: Two profiles for quality vs. performance
- **Type Checking**: Pylance (live) + MyPy (batch/CI)
- **Linting & Formatting**: Ruff and Black integration
- **Testing**: Pytest with VS Code integration
- **CI/CD**: GitHub Actions workflow examples

### Core Principles

#### Layered Tooling Strategy

| Layer             | Purpose                       | Tools                                      |
| ----------------- | ----------------------------- | ------------------------------------------ |
| **Editor (Live)** | Instant feedback while coding | Pylance (strict mode)                      |
| **Repo (Manual)** | On-demand validation          | MyPy, Ruff, Pytest                         |
| **CI (Gate)**     | Final enforcement             | MyPy, Ruff, Pytest (same versions as repo) |

#### Package vs. Extension Philosophy

**Key Rule**: Python packages are the source of truth; VS Code extensions provide the UI.

| Tool       | Install as Package? | Install as Extension? | Why Both?                                    |
| ---------- | ------------------- | --------------------- | -------------------------------------------- |
| Pylance    | No                  | Yes                   | Editor-only tool                             |
| MyPy       | Yes                 | Yes                   | Package for CI, extension for live feedback  |
| Ruff       | Yes                 | Yes                   | Package for CI, extension for live linting   |
| Black      | Yes                 | Yes                   | Package for CI, extension for format-on-save |
| Pytest     | Yes                 | No                    | Python extension has built-in integration    |
| pytest-cov | Yes                 | No                    | Coverage reporting for tests                 |
| pre-commit | Yes                 | No                    | Git hook framework for automation            |

**Benefits**:

- Versions are consistent between local dev and CI
- Tools work in terminals and automated workflows
- No "works on my machine" problems
- Extensions use the venv versions automatically

---

## Prerequisites

### Required

- **Python 3.14** (or 3.13 for maximum stability)
- **uv 0.10+** — Python package and project manager
- **VS Code 1.109+**

### Verify Installation

```bash
python --version    # Python 3.14.x
uv --version        # uv 0.10.x
code --version      # 1.109+
```

### Installing uv

If you don't have uv installed:

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pipx
pipx install uv
```

---

## Recommended Repo Layout

Use the `src/` layout for larger projects (cleaner imports, prevents accidental local imports):

```
repo/
├── pyproject.toml
├── uv.lock
├── README.md
├── .python-version
├── .vscode/
│   └── settings.json
├── .pre-commit-config.yaml
├── src/
│   └── your_package/
│       └── __init__.py
├── tests/
│   └── test_example.py
└── .venv/
```

For simpler projects, a flat layout works:

```
repo/
├── pyproject.toml
├── uv.lock
├── your_package/
│   └── __init__.py
├── tests/
│   └── test_example.py
└── .venv/
```

---

## Project Setup with uv

> **⚠️ Important**: Use **New Project** commands only when starting from scratch. For repositories that already have a `pyproject.toml`, skip to **Existing Project**.

### New Project

Use these commands **only** when creating a brand new project. Do **not** run `uv init` inside an existing repository—it will create a nested project folder.

```bash
# Create a new project (run from parent directory, NOT inside an existing repo)
uv init myproject
cd myproject

# This creates pyproject.toml, README.md, and src/ layout
```

### Existing Project

For repositories that already have a `pyproject.toml` (like cloned repos or established projects):

```bash
# Install dependencies from pyproject.toml and create .venv
uv sync

# Install pre-commit hooks (if .pre-commit-config.yaml exists)
pre-commit install
```

### Add Dev Dependencies

```bash
# Add development tools
uv add --dev ruff mypy pytest pytest-cov pre-commit

# Optional: Add Black if preferred over Ruff formatter
uv add --dev black

# Lock dependencies
uv lock
```

### Activate the Environment

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Or run commands directly with uv
uv run pytest
uv run mypy .
```

### Common Pitfalls

#### Running `uv init` Inside an Existing Project

**Problem**: Running `uv init myproject` inside an existing repository creates a nested project folder, which confuses VS Code's test discovery and may cause unexpected behavior.

**Symptoms**:

- A `myproject/` folder appears inside your repo
- VS Code test runner shows errors or popups from the wrong project
- `pre-commit install` runs in the wrong directory

**How to Avoid**:

- For existing projects, use `uv sync` (not `uv init`)
- Only use `uv init` from a **parent** directory when creating new projects

**How to Fix**:

```bash
# Remove the accidentally created nested project
rm -rf myproject

# Ensure you're in the correct directory
cd /path/to/your-existing-project

# Use the correct setup commands for existing projects
uv sync
pre-commit install
```

**Verify the Fix**:

```bash
# Reload VS Code test discovery
# Ctrl+Shift+P → "Python: Discover Tests"

# Run tests from terminal to confirm
uv run pytest
```

---

## Python Version Management

uv can manage Python versions directly, eliminating the need for pyenv or asdf.

### Install Python Versions

```bash
# Install specific versions
uv python install 3.14
uv python install 3.13 3.14

# List available versions
uv python list

# List installed versions
uv python list --installed
```

### Pin Project Python Version

Create a `.python-version` file in your repo root:

```bash
echo "3.14" > .python-version
```

Or specify in `pyproject.toml`:

```toml
[project]
requires-python = ">=3.14"
```

uv will automatically use the correct Python version when running commands.

---

## pyproject.toml Configuration

Complete configuration for all tools:

```toml
[project]
name = "your-project"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []

[project.optional-dependencies]
dev = [
    "ruff>=0.15",
    "mypy>=1.19",
    "pytest>=9.0",
    "pytest-cov>=6.0",
    "pre-commit>=4.5",
    "black>=26.1",
]

# Alternative: uv-specific dev dependencies
[tool.uv]
dev-dependencies = [
    "ruff>=0.15",
    "mypy>=1.19",
    "pytest>=9.0",
    "pytest-cov>=6.0",
    "pre-commit>=4.5",
    "black>=26.1",
]

# ============================================
# Ruff Configuration
# ============================================
[tool.ruff]
line-length = 88
target-version = "py314"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "ANN",    # flake8-annotations
    "B",      # flake8-bugbear
    "SIM",    # flake8-simplify
    "PTH",    # flake8-use-pathlib
    "PT",     # flake8-pytest-style
    "RET",    # flake8-return
    "PL",     # pylint
    "RUF",    # Ruff-specific rules
]
ignore = [
    "ANN401",  # Dynamically typed expressions (Any) - allow when necessary
    "PLR0913", # Too many arguments - let design dictate
    "E501",    # Allow long lines (managed by formatter)
]

# Per-file rule overrides — essential for real-world projects
[tool.ruff.lint.per-file-ignores]
# Test files need relaxed rules
"tests/**/*.py" = [
    "ANN",      # Type hints less critical in tests
    "S101",     # Assert usage required for pytest
    "PLW0108",  # Lambda wrappers acceptable in signal connections
    "E731",     # Lambda assignments acceptable in tests
    "F841",     # Unused variables acceptable for side-effect testing
    "PT011",    # Broad pytest.raises acceptable with exc_info assertions
    "PTH123",   # open() acceptable in tests
]
# Auto-generated files should not be linted
# "generated/**/*.py" = ["ALL"]

[tool.ruff.lint.isort]
known-first-party = ["your_package"]

# Optional: Use Ruff as formatter instead of Black
[tool.ruff.format]
quote-style = "double"
indent-style = "space"

# ============================================
# Black Configuration
# ============================================
[tool.black]
line-length = 88
target-version = ["py314"]

# ============================================
# MyPy Configuration
# ============================================
[tool.mypy]
python_version = "3.14"

# Core behavior
strict = true
pretty = true
show_error_codes = true
show_column_numbers = true
warn_unused_ignores = true

# Practical strictness (helps agents)
no_implicit_optional = true
warn_return_any = true
warn_redundant_casts = true

# Keep signal high (reduce noise)
ignore_missing_imports = false
follow_imports = "normal"

# Performance / stability
cache_dir = ".mypy_cache"
incremental = true

# For namespace packages or src layouts
namespace_packages = true
explicit_package_bases = true

# For src/ layout: uncomment this
# mypy_path = ["src"]

# Per-module overrides for untyped dependencies
[[tool.mypy.overrides]]
module = [
    "yaml.*",
    "boto3.*",
    "botocore.*",
]
ignore_missing_imports = true

# ============================================
# Pytest Configuration
# ============================================
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --tb=short"
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

### For src/ Layout Projects

If using `src/` layout, add this to resolve imports:

```toml
[tool.mypy]
mypy_path = ["src"]
```

And install your package as editable:

```bash
uv pip install -e .
```

---

## VS Code Configuration

### Profile A: Quality-First (Recommended Default)

Best for agent-generated code correctness. Provides full workspace diagnostics, indexing, and strict typing.

**File**: `.vscode/settings.json`

```jsonc
{
  // ---- Python interpreter & environment ----
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv",

  // ---- Pylance / analysis core ----
  "python.languageServer": "Default",
  "python.analysis.indexing": true,
  "python.analysis.diagnosticMode": "workspace",
  "python.analysis.typeCheckingMode": "strict",

  // Improve import resolution
  "python.analysis.autoSearchPaths": true,
  "python.analysis.enableEditableInstalls": true,
  "python.analysis.importFormat": "absolute",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.completeFunctionParens": true,
  "python.analysis.useLibraryCodeForTypes": true,

  // ---- Testing (pytest) ----
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.autoTestDiscoverOnSaveEnabled": false,

  // ---- Linting ----
  "python.linting.enabled": true,

  // ---- Formatting ----
  "editor.formatOnSave": true,
  // Use Black Formatter extension:
  "editor.defaultFormatter": "ms-python.black-formatter",
  // Or use Ruff formatter:
  // "editor.defaultFormatter": "charliermarsh.ruff",

  // ---- Code Actions ----
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit",
    "source.fixAll": "explicit",
  },

  // ---- Editor Quality of Life ----
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
}
```

**Why this works for agents**:

- Workspace diagnostics + strict typing catches missing returns, incompatible args, wrong attribute usage
- Indexing + auto-import completions reduces "hallucinated imports"
- Full workspace analysis means agents see issues across files, not just the active editor

### Profile B: Performance-First (Large Repos)

Use when Pylance becomes sluggish in large workspaces or monorepos.

```jsonc
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv",
  "python.languageServer": "Default",

  // Only report problems for open files
  "python.analysis.diagnosticMode": "openFilesOnly",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.indexing": false,

  // Keep these ON for agent correctness
  "python.analysis.autoSearchPaths": true,
  "python.analysis.enableEditableInstalls": true,
  "python.analysis.autoImportCompletions": true,

  // Testing
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.autoTestDiscoverOnSaveEnabled": false,

  // Formatting
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "ms-python.black-formatter",
}
```

### Select the Interpreter

In VS Code:

1. `Ctrl+Shift+P` → **Python: Select Interpreter**
2. Choose: `./.venv/bin/python` (Linux/macOS) or `.\.venv\Scripts\python.exe` (Windows)

### Optional Tuning Parameters

| Setting                                 | Value                          | Use Case                                             |
| --------------------------------------- | ------------------------------ | ---------------------------------------------------- |
| `python.analysis.userFileIndexingLimit` | `2000` (default)               | Limit indexed files; `-1` indexes all                |
| `python.analysis.languageServerMode`    | `"light"`                      | Globally resource-friendly mode                      |
| `python.analysis.aiCodeActions`         | `true`                         | AI-assisted abstract method stubs (requires Copilot) |
| `python.analysis.stubPath`              | `"${workspaceFolder}/typings"` | Custom type stub location                            |

---

## VS Code Extensions

### Required

| Extension         | Publisher | Purpose                           |
| ----------------- | --------- | --------------------------------- |
| Python            | Microsoft | Core Python support               |
| Pylance           | Microsoft | Fast type checking & IntelliSense |
| Ruff              | Astral    | Live linting and import sorting   |
| Black Formatter   | Microsoft | Format-on-save with Black         |
| MyPy Type Checker | Microsoft | Live type checking feedback       |

### Optional

| Extension | Publisher | Use Case                                          |
| --------- | --------- | ------------------------------------------------- |
| Jupyter   | Microsoft | Notebook support (only if needed)                 |
| GitLens   | GitKraken | Enhanced Git features (useful in large codebases) |

### Installing Extensions

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-python.black-formatter
code --install-extension ms-python.mypy-type-checker
```

### Extension Path Configuration

VS Code extensions for MyPy and Ruff need to find the correct executables. By default, they auto-detect from your `.venv`, but explicit paths are more reliable:

```jsonc
{
  // Point extensions to venv executables
  "mypy-type-checker.path": ["${workspaceFolder}/.venv/bin/mypy"],
  "ruff.path": ["${workspaceFolder}/.venv/bin/ruff"],

  // UV is a system-level tool — do NOT point to .venv
  // ❌ "uvToolkit.uvPath": "${workspaceFolder}/.venv/bin/uv"
  // ✅ "uvToolkit.uvPath": "uv"
}
```

> **Common Mistake**: UV is installed system-wide (via `curl` or `pipx`), not in the project's `.venv`. Setting `uvToolkit.uvPath` to a `.venv` path will break it.

---

## Type Stubs for Third-Party Libraries

Many popular libraries don't include inline type hints. Install type stubs to get proper type checking:

### Common Type Stub Packages

```bash
uv add --dev types-requests types-pyyaml types-redis types-python-dateutil
```

| Package                 | For Library     |
| ----------------------- | --------------- |
| `types-requests`        | requests        |
| `types-pyyaml`          | PyYAML          |
| `types-redis`           | redis           |
| `types-python-dateutil` | python-dateutil |
| `types-protobuf`        | protobuf        |
| `types-setuptools`      | setuptools      |
| `types-docutils`        | docutils        |
| `types-pillow`          | Pillow          |

### Finding Type Stubs

Search for stubs on PyPI:

```bash
uv search types-<library-name>
```

Or check [typeshed](https://github.com/python/typeshed) for available stubs.

### Handling Untyped Libraries

For libraries without stubs, add overrides in `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = ["some_untyped_library.*"]
ignore_missing_imports = true
```

---

## Pre-commit Setup

Pre-commit hooks prevent agents (and humans) from committing broken formatting or obvious issues.

### Install Pre-commit

```bash
uv add --dev pre-commit
pre-commit install
```

### Configuration File

Create `.pre-commit-config.yaml`:

```yaml
repos:
  # General file hygiene (run first — fast checks)
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        exclude: \.aider  # Exclude non-standard YAML files
      - id: check-toml
      - id: check-added-large-files
        args: ["--maxkb=1000"]
      - id: check-merge-conflict
      - id: debug-statements

  # Ruff linting and formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.0
    hooks:
      - id: ruff
        args: ["--fix", "--exit-non-zero-on-fix"]
      - id: ruff-format

  # MyPy type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.19.1
    hooks:
      - id: mypy
        additional_dependencies:
          - pytest>=7.0.0
          - pytest-mock>=3.0.0  # Required if tests use MockerFixture type
          # Add your project's typed dependencies here:
          # - PySide6>=6.6.0
          # - types-requests
        args: ["--config-file=pyproject.toml"]
        # Option A: Check specific files (faster, per-file)
        # (default behavior — mypy runs on each changed file)
        # Option B: Check entire project (slower but catches cross-file issues)
        # pass_filenames: false
        # entry: mypy src/
```

> **Important**: The `mirrors-mypy` hook runs in an isolated environment. You **must** list all typed dependencies in `additional_dependencies` — it cannot access your project's `.venv`. If MyPy reports "Cannot find implementation or library stub" in pre-commit but works locally, this is the cause.

### Run Manually

```bash
# Run on all files (recommended after initial setup)
pre-commit run --all-files

# Run on staged files only (default during commits)
pre-commit run
```

### Pre-commit Gotchas

1. **First run catches many pre-existing issues**: When enabling pre-commit on an existing codebase, `--all-files` will flag issues across the entire project. Budget time for this cleanup.

2. **Ruff `--exit-non-zero-on-fix` prevents silent auto-fixes**: Without this flag, Ruff silently fixes issues and commits proceed. With it, the commit fails so you can review and re-stage the fixes.

3. **Ruff format modifies files**: After a failed commit, files may have been reformatted by hooks. You need to `git add` the modified files and commit again.

4. **check-yaml fails on non-standard YAML**: Tools like aider create YAML configs that may not pass strict validation. Use `exclude` patterns to skip them.

5. **MyPy `pass_filenames: false`**: For projects where cross-file type checking matters (e.g., signal/slot connections), disable per-file checking and run MyPy on the entire project directory instead.

---

## Testing Integration

### Pytest with VS Code

Pytest integrates natively with the Python extension—no separate extension needed.

**Run tests from**:

- Testing panel (sidebar icon)
- Command Palette: `Python: Run All Tests`
- Terminal: `pytest` or `uv run pytest`

**Key settings** (already in Profile A/B):

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.autoTestDiscoverOnSaveEnabled": false
}
```

Setting `autoTestDiscoverOnSaveEnabled` to `false` prevents constant background test discovery churn while agents edit many files.

### Coverage Reports

```bash
# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Generate HTML report
uv run pytest --cov=src --cov-report=html
```

---

## Running Tools Manually

### Ruff (Linting)

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Format code (alternative to Black)
uv run ruff format .
```

### Black (Formatting)

```bash
# Format all files
uv run black .

# Check without modifying
uv run black . --check
```

### MyPy (Type Checking)

```bash
# Full project
uv run mypy .

# Specific directories
uv run mypy src tests
```

### Pytest (Testing)

```bash
# Run all tests
uv run pytest

# Quiet mode
uv run pytest -q

# With coverage
uv run pytest --cov

# Single test file
uv run pytest tests/test_example.py

# Single test function
uv run pytest tests/test_example.py::test_function_name
```

---

## Recommended Agent Workflow

### Tight Inner Loop

```
1. Agent writes/edits code
2. Pylance flags issues immediately (in-editor)
3. Ruff catches style/import errors on save
4. Run pytest (verify functionality)
5. Run mypy (type gate)
6. Fix issues, repeat
```

### Why This Works

| Stage             | Tool             | Purpose                 |
| ----------------- | ---------------- | ----------------------- |
| **While Coding**  | Pylance (strict) | Live feedback in editor |
| **On Save**       | Ruff, Black      | Linting & formatting    |
| **After Changes** | Pytest           | Verify functionality    |
| **Before Commit** | Pre-commit       | Enforce all checks      |
| **Before Push**   | MyPy             | Type gate               |
| **CI Pipeline**   | All of the above | Final enforcement       |

### The Essential Toolchain

1. **Ruff** — lint + imports (+ optional formatting)
2. **Black** — formatting (or use Ruff formatter)
3. **Pytest** — tests
4. **pytest-cov** — coverage reporting
5. **MyPy** — types
6. **pre-commit** — enforce all automatically

---

## Performance Tuning

If VS Code becomes slow in large repos, adjust these settings:

```jsonc
{
  // Reduce diagnostics scope
  "python.analysis.diagnosticMode": "openFilesOnly",

  // Disable indexing
  "python.analysis.indexing": false,

  // Reduce type checking strictness
  "python.analysis.typeCheckingMode": "basic",

  // Limit indexed files (if keeping indexing on)
  "python.analysis.userFileIndexingLimit": 1000,

  // Use light language server mode
  "python.analysis.languageServerMode": "light",
}
```

**Trade-offs**:

- Fewer cross-file diagnostics
- Auto-imports may be less complete
- Faster editor response

**Recommendation**: Start with Profile A. Switch to Profile B only when you experience latency.

---

## GitHub Actions CI

Example workflow that runs the same tools as local development:

**File**: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Set up Python
        run: uv python install 3.14

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Lint with Ruff
        run: uv run ruff check .

      - name: Check formatting
        run: uv run ruff format --check .
        # Or if using Black:
        # run: uv run black --check .

      - name: Type check with MyPy
        run: uv run mypy .

      - name: Run tests
        run: uv run pytest --cov --cov-report=xml

      # Optional: Upload coverage to Codecov
      # - uses: codecov/codecov-action@v4
      #   with:
      #     files: ./coverage.xml
```

### Matrix Testing (Multiple Python Versions)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.13", "3.14"]

    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - run: uv sync --all-extras --dev
      - run: uv run pytest
```

---

## Troubleshooting

### Pre-commit Hooks Fail on First Commit

**Problem**: After setting up pre-commit on an existing codebase, the first commit fails with many Ruff or MyPy errors.

**Solution**: Run `pre-commit run --all-files` separately, fix issues in batches, then commit. Common approaches:

```bash
# Fix auto-fixable issues
ruff check . --fix
ruff format .

# Stage fixes and try again
git add -A
pre-commit run --all-files
```

For issues that can't be auto-fixed, add appropriate per-file ignores in `pyproject.toml` (see [Per-file Ignores](#per-file-rule-overrides)).

### MyPy Passes Locally but Fails in Pre-commit

**Problem**: `uv run mypy .` succeeds, but the pre-commit MyPy hook fails with "Cannot find implementation or library stub" errors.

**Cause**: The `mirrors-mypy` pre-commit hook runs in an isolated virtualenv that only has packages listed in `additional_dependencies`.

**Solution**: Add all typed dependencies to the MyPy hook's `additional_dependencies` list in `.pre-commit-config.yaml`. Common ones to forget:
- `pytest-mock` (for `MockerFixture` type)
- `pytest-qt` (for `QtBot` type)
- Framework libraries (PySide6, Django, Flask, etc.)

### Ruff Reports N999 (Invalid Module Name)

**Problem**: Ruff flags `N999 Invalid module name` for your package directory (e.g., `MyProject/__init__.py`).

**Cause**: PEP 8 requires lowercase module names, but your project directory uses uppercase.

**Solutions**:
1. Rename the directory to lowercase (best practice for new projects)
2. Add `"N999"` to the global `ignore` list in `pyproject.toml` if renaming isn't feasible

### Auto-Generated Files Trigger Lint Errors

**Problem**: Files generated by tools (Qt Designer UI files, protobuf stubs, ORM auto-generated code) fail Ruff checks.

**Solution**: Add per-file ignores with `"ALL"` to suppress all rules for generated files:

```toml
[tool.ruff.lint.per-file-ignores]
"**/generated/**/*.py" = ["ALL"]
"**/designer/*_ui.py" = ["ALL"]
```

### VS Code Test Runner Shows Unexpected Dialogs

**Problem**: Running tests from the VS Code sidebar triggers actual GUI dialogs (message boxes, file dialogs).

**Cause**: Tests that call methods triggering `QMessageBox.warning()`, `QFileDialog.getExistingDirectory()`, etc., without mocking them.

**Solution**: Mock all dialog classes in tests:

```python
from unittest.mock import patch

def test_action_shows_warning(self, qapp, window):
    with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warn:
        window._on_some_action()
        mock_warn.assert_called_once()
```

### Git Identity Not Configured

**Problem**: `git commit` fails with "Author identity unknown".

**Cause**: Git user.name and user.email not set (common on fresh machines or containers).

**Solution**:
```bash
# Set for this repo only
git config user.name "Your Name"
git config user.email "your@email.com"

# Or set globally
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## Quick Start

### One-Command Setup

```bash
# New project (run from PARENT directory)
uv init myproject && cd myproject
uv add --dev ruff mypy pytest pytest-cov pre-commit black
pre-commit install

# Existing project (already has pyproject.toml)
uv sync
pre-commit install
```

### Checklist

**Repo Setup**:

- [ ] `.venv/` created with `uv sync` (existing project) or `uv init` (new project)
- [ ] Dev tooling installed: `ruff`, `mypy`, `pytest`, `pytest-cov`, `pre-commit`, `black`
- [ ] `pyproject.toml` configured with tool settings and per-file ignores
- [ ] `.python-version` file created (e.g., `3.14`)
- [ ] `.pre-commit-config.yaml` added with all typed deps in MyPy `additional_dependencies`
- [ ] Pre-commit hooks installed: `pre-commit install`
- [ ] Generated/auto-created files excluded from linting

**VS Code Setup**:

- [ ] Python extension installed
- [ ] Pylance extension installed
- [ ] Ruff extension installed (path configured to `.venv/bin/ruff`)
- [ ] Black Formatter extension installed
- [ ] MyPy Type Checker extension installed (path configured to `.venv/bin/mypy`)
- [ ] Interpreter set to `.venv`
- [ ] `.vscode/settings.json` or workspace settings configured
- [ ] UV toolkit path set to `"uv"` (system tool, not `.venv`)

**Verification**:

- [ ] `uv run ruff check .` — passes
- [ ] `uv run mypy .` — passes
- [ ] `uv run pytest` — passes
- [ ] `pre-commit run --all-files` — passes
- [ ] Testing panel shows tests (no unexpected dialog popups)

---

## Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [Pylance Documentation](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [VS Code Python Settings Reference](https://code.visualstudio.com/docs/python/settings-reference)
- [Typeshed (Type Stubs)](https://github.com/python/typeshed)
