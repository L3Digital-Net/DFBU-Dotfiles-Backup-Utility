# DFBU — Style and Conventions

## Code Style

- Ruff linter + formatter (py314 target, line-length 88, Black-compatible)
- Full type hint coverage with mypy compliance
- SOLID principles throughout

## Architecture Rules

- MVVM: View never touches Model directly; always through ViewModel
- Signal/slot for cross-layer communication
- QThread workers for non-blocking operations
- ConfigManager handles all config I/O
- FileOperations handles all filesystem ops
