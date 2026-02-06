# Agent Instructions for DFBU Desktop Application

## Quick Reference

- **UI**: PySide6 (Qt for Python 6.6.0+)
- **Language**: Python 3.14+
- **Platform**: Linux only
- **Architecture**: MVVM (Model-View-ViewModel) with Facade pattern
- **Principles**: SOLID
- **Testing**: Pytest with pytest-qt
- **Package Manager**: UV
- **Distribution**: AppImage (GitHub Releases)
- **UI Design**: Qt Designer (.ui files - NO hardcoded UI)

## Essential Files

- `CLAUDE.md` - Claude Code / AI assistant instructions
- `.github/copilot-instructions.md` - GitHub Copilot instructions
- `.agents/memory.instruction.md` - Additional agent preferences (if present)
- `.agents/branch_protection.py` - Branch protection checker (if present)
- `docs/BRANCH_PROTECTION.md` - Complete branch protection documentation
- `CONTRIBUTING.md` - Development workflow and code standards
- `DFBU/docs/ARCHITECTURE.md` - MVVM architecture details

## Critical: Branch Protection

**BEFORE ANY FILE MODIFICATION:**

1. Confirm you are not on `main`: `git branch --show-current`
2. If the repo contains `.agents/branch_protection.py`, run: `python .agents/branch_protection.py`

- ❌ NEVER modify files on `main` branch
- ✅ ALWAYS work on `testing` branch
- ✅ ONLY assist with merges when human explicitly authorizes

See [docs/BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md) for full details.

## Dev Environment (uv)

This repo’s CI uses `uv` + Python 3.14.

```bash
uv python install 3.14
uv sync --all-extras --dev
uv run python DFBU/dfbu_gui.py
```

## Architecture Rules (Non-Negotiable)

For comprehensive architecture documentation, see [DFBU/docs/ARCHITECTURE.md](DFBU/docs/ARCHITECTURE.md).

### Model Layer

✅ **Allowed**: Pure Python, dataclasses, business logic, validation, domain exceptions
❌ **Forbidden**: Any Qt imports, UI concerns, direct file I/O (use services)

### ViewModel Layer

✅ **Allowed**: QObject, signals/slots, presentation logic, calling services, state management
❌ **Forbidden**: Direct widget manipulation, business logic, UI styling

### View Layer

✅ **Allowed**: Loading .ui files, PySide6 widgets, signal connections, finding child widgets
❌ **Forbidden**: Hardcoded UI layouts, business logic, data validation, direct model access

## Development Checklist

### Starting a New Feature

- [ ] Identify which layer(s) are affected (Model/View/ViewModel)
- [ ] Design the data flow: Model → ViewModel → View
- [ ] Write tests first (TDD approach)
- [ ] Implement Model (pure Python, no Qt)
- [ ] Implement ViewModel (QObject, signals)
- [ ] Implement View (PySide6 widgets, .ui files)
- [ ] Verify SOLID principles are maintained
- [ ] Run full test suite

### Code Review Checklist

- [ ] MVVM separation maintained (no Qt in Models)
- [ ] SOLID principles followed
- [ ] Type hints on all functions/methods (modern 3.10+ syntax)
- [ ] Tests written and passing
- [ ] No business logic in Views
- [ ] UI loaded from .ui files (NO hardcoded layouts)
- [ ] Dependencies injected, not created
- [ ] Signals used for cross-layer communication
- [ ] No blocking operations on UI thread

## Running Tests

```bash
# All tests (preferred)
uv run pytest DFBU/tests/

# With coverage
uv run pytest DFBU/tests/ --cov=DFBU --cov-report=html

# Specific test file
uv run pytest DFBU/tests/test_model.py -v

# By marker
uv run pytest DFBU/tests/ -m unit
uv run pytest DFBU/tests/ -m integration
uv run pytest DFBU/tests/ -m gui

# Type checking
uv run mypy DFBU/

# Lint / format
uv run ruff check DFBU/
uv run ruff format --check DFBU/
```

For comprehensive testing documentation, see [DFBU/tests/README.md](DFBU/tests/README.md).

## Quick Patterns

### Signal Communication

```python
# ViewModel emits changes
class DataViewModel(QObject):
    data_loaded = Signal(list)

    def load_data(self):
        data = self._service.fetch()
        self.data_loaded.emit(data)

# View reacts to changes
class DataView(QWidget):
    def __init__(self, vm: DataViewModel):
        super().__init__()
        vm.data_loaded.connect(self._update_list)
        self.load_button.clicked.connect(vm.load_data)
```

### Testing Pattern

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

## Troubleshooting

### Issue: "QApplication not created"

**Solution**: Create QApplication fixture in conftest.py:

```python
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
```

### Issue: Circular dependency between View and ViewModel

**Solution**: Always pass ViewModel TO View, never the reverse. Use signals for communication.

### Issue: Tests fail with "No event loop"

**Solution**: Use `pytest-qt` plugin and pass `qtbot` fixture to tests that need Qt.

### Issue: UI freezes during long operation

**Solution**: Move operation to QThread. See [DFBU/gui/config_workers.py](DFBU/gui/config_workers.py) for examples.

## Resources

### Project Documentation

- [docs/INDEX.md](docs/INDEX.md) - Complete documentation index
- [DFBU/docs/ARCHITECTURE.md](DFBU/docs/ARCHITECTURE.md) - Comprehensive architecture documentation
- [DFBU/tests/README.md](DFBU/tests/README.md) - Testing documentation and fixtures
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup and guidelines
- [docs/BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md) - Branch protection details

### External Documentation

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Plugin](https://pytest-qt.readthedocs.io/)

## AI Agent Workflow

1. **Check branch**: Ensure you’re on `testing` (never modify `main`)
2. **Branch protection**: If present, run `python .agents/branch_protection.py`
3. **Follow MVVM strictly**: Never mix concerns between layers
4. **Use type hints**: Modern Python 3.14+ syntax (see [CONTRIBUTING.md](CONTRIBUTING.md))
5. **Write tests**: TDD approach preferred (see [DFBU/tests/README.md](DFBU/tests/README.md))
6. **Run checks after changes**: `uv run pytest DFBU/tests/` and `uv run mypy DFBU/`
