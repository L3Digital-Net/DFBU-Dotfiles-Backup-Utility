# DFBU — Project Overview

## Purpose

Desktop application for backing up and restoring Linux dotfiles/configuration files.
PySide6 GUI with MVVM architecture.

## Tech Stack

- Python 3.14, PySide6 (Qt6), ruamel-yaml, tomli-w
- Build: Hatchling
- Linter/Formatter: Ruff (target py314, line-length 88)
- Entry point: `DFBU.dfbu_gui:main`

## Architecture — MVVM Pattern

- **Model**: ConfigManager (config I/O + CRUD), FileOperations (filesystem + paths),
  BackupOrchestrator (coordination + progress), StatisticsTracker (metrics)
- **ViewModel**: Exposes only methods needed by View
- **View**: PySide6 widgets, Qt Designer .ui files in `DFBU/gui/designer/`

## SOLID Principles

- SRP: each class has one purpose
- OCP: new backup strategies without modifying existing code
- LSP: subclasses maintain base contracts (NumericTableWidgetItem, QThread workers)
- ISP: focused interfaces, minimal required methods
- DIP: ViewModel depends on abstractions

## Key Directories

```
DFBU/
  dfbu_gui.py          # Entry point
  src/                 # Core logic
  gui/                 # PySide6 views
  gui/designer/        # Qt Designer .ui files
  config/              # YAML config files
  tests/               # pytest test suite
  docs/                # Architecture docs, changelog
```

## Threading

- Non-blocking UI via QThread workers
- Signal/slot communication between layers
