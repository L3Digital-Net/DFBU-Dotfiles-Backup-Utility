# DFBU — Development Commands

## Running

```bash
uv run dfbu                    # Launch GUI
python -m DFBU.dfbu_gui        # Alternative launch
```

## Testing

```bash
pytest DFBU/tests/             # Run all tests
pytest DFBU/tests/ --cov       # With coverage
```

## Linting and Formatting

```bash
ruff check .                   # Lint
ruff check . --fix             # Lint with auto-fix
ruff format .                  # Format
```

## Git

- Work on `testing` branch
- Do NOT push to `main` without permission
