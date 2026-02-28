# DFBU Test Suite Documentation

## Overview

This directory contains the comprehensive test suite for the DFBU (DotFiles Backup
Utility) application. The test suite follows MVVM architecture principles and adheres to
the testing standards outlined in `.github/prompts/test.prompt.md`.

## Test Coverage

**Current Coverage: 82%** (exceeds 80% target)

- **Model Layer**: 100% coverage
- **ViewModel Layer**: 99% coverage
- **View Layer**: 99% coverage (2 skipped UI interaction tests)
- **Core Utilities**: 94-100% coverage
- **Integration Tests**: 100% coverage

## Test Organization

All test files are organized in the `DFBU/tests/` directory, following the project
structure:

```
DFBU/tests/
├── conftest.py                          # Pytest configuration and fixtures
├── test_model.py                        # Model layer unit tests
├── test_model_additional_coverage.py    # Extended model testing
├── test_model_file_operations.py        # File operation tests
├── test_viewmodel_multiple_paths.py     # ViewModel path handling
├── test_viewmodel_template.py           # ViewModel testing template
├── test_view_comprehensive.py           # View layer tests
├── test_workers_comprehensive.py        # Background worker tests
├── test_backup_orchestrator.py          # Backup orchestration tests
├── test_config_validation.py            # Configuration validation tests
├── test_dotfile_class.py                # DotFile class tests
└── test_dfbu_cli.py                     # CLI integration tests
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Fast, isolated tests for individual components without external dependencies.

- **Model Tests**: Business logic, data validation, state management
- **ViewModel Tests**: Presentation logic, signal emissions, state coordination
- **View Tests**: UI component initialization, signal connections

### Integration Tests (`@pytest.mark.integration`)

Tests that verify interactions between multiple components.

- **CLI Integration**: Complete workflow testing
- **Backup Orchestration**: Multi-component backup operations
- **Configuration Management**: Loading, validation, and saving

### GUI Tests (`@pytest.mark.gui`)

Tests requiring QApplication and Qt components.

- **Signal/Slot Tests**: Verifying Qt signal emissions
- **Worker Thread Tests**: Background operation testing
- **Dialog Tests**: UI dialog initialization and behavior

### Slow Tests (`@pytest.mark.slow`)

Tests that take more than 1 second to execute.

## Running Tests

### Run All Tests

```bash
pytest DFBU/tests/
```

### Run with Coverage

```bash
pytest DFBU/tests/ --cov=DFBU --cov-report=html --cov-report=term-missing
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest DFBU/tests/ -m unit

# Integration tests only
pytest DFBU/tests/ -m integration

# GUI tests only
pytest DFBU/tests/ -m gui

# Skip slow tests
pytest DFBU/tests/ -m "not slow"
```

### Run Specific Test Files

```bash
pytest DFBU/tests/test_model.py -v
pytest DFBU/tests/test_viewmodel_multiple_paths.py -v
```

### Run Specific Test Classes or Methods

```bash
# Run specific test class
pytest DFBU/tests/test_model.py::TestDFBUModelInitialization -v

# Run specific test method
pytest DFBU/tests/test_model.py::TestDFBUModelInitialization::test_model_initialization -v
```

## Test Standards

### AAA Pattern

All tests follow the Arrange-Act-Assert pattern:

```python
def test_model_initialization(tmp_path):
    """Test model initializes with correct default values."""
    # Arrange
    config_path = tmp_path / "config.toml"

    # Act
    model = DFBUModel(config_path)

    # Assert
    assert model.config_path == config_path
    assert model.hostname != ""
```

### Test Naming Convention

Tests use descriptive names that explain expected behavior:

```python
def test_should_<expected_behavior>_when_<condition>()
def test_<component>_<action>_<expected_result>()
```

Examples:

- `test_model_initialization()`
- `test_load_config_file_not_found()`
- `test_viewmodel_emits_signal_when_data_changes()`

### Fixtures

#### Session-Scoped Fixtures

- `qapp`: QApplication instance for Qt testing (provided by pytest-qt)

#### Function-Scoped Fixtures

- `tmp_path`: Temporary directory for test files (pytest built-in)
- `temp_config_path`: Temporary path for configuration files
- `temp_dotfile`: Temporary file with test content
- `temp_dotfile_dir`: Temporary directory with test files

#### Configuration Fixtures

- `minimal_config_content`: Minimal valid TOML configuration
- `complete_config_content`: Complete TOML with all options

#### Mock Fixtures

- `mock_file_service`: Mock file service for ViewModel testing
- `mock_config_service`: Mock configuration service

## Testing MVVM Layers

### Model Layer Testing

**Focus**: Business logic, data validation, domain entities

```python
class TestDFBUModelConfigManagement:
    """Test suite for configuration loading and saving."""

    def test_load_config_file_not_found(self, tmp_path):
        """Test loading nonexistent config file returns error."""
        # Arrange
        model = DFBUModel(tmp_path / "nonexistent.toml")

        # Act
        success, error_message = model.load_config()

        # Assert
        assert success is False
        assert "not found" in error_message.lower()
```

**Characteristics**:

- ✅ Pure Python testing (no Qt dependencies)
- ✅ Focus on business logic correctness
- ✅ Data validation and transformation
- ❌ No UI concerns

### ViewModel Layer Testing

**Focus**: Presentation logic, signal emissions, state coordination

```python
def test_viewmodel_emits_signal(qtbot, mocker):
    """Test that viewmodel emits signal when data changes."""
    # Arrange
    mock_service = mocker.Mock()
    mock_service.fetch.return_value = ["item1"]
    vm = ExampleViewModel(mock_service)

    # Act & Assert
    with qtbot.waitSignal(vm.data_changed, timeout=1000) as blocker:
        vm.load_data()

    assert blocker.args[0] == ["item1"]
    mock_service.fetch.assert_called_once()
```

**Characteristics**:

- ✅ Uses `qtbot` fixture from pytest-qt
- ✅ Tests signal emissions with `qtbot.waitSignal()`
- ✅ Mocks Model and Service dependencies
- ✅ Validates state management
- ❌ No direct widget manipulation

### View Layer Testing (Optional)

**Focus**: UI initialization, signal connections

```python
def test_main_window_initialization(qapp, viewmodel_with_config):
    """Test MainWindow initializes with ViewModel."""
    # Act
    window = MainWindow(viewmodel_with_config, "1.0.0")

    # Assert
    assert window.viewmodel == viewmodel_with_config
    assert "DFBU GUI" in window.windowTitle()
    assert hasattr(window, "tab_widget")
```

**Note**: Per test.prompt.md guidelines, View layer tests are optional. Focus is on
Model and ViewModel testing. Complex UI interaction tests may be skipped when mocking
becomes overly intricate.

## Mocking Strategy

### Mock Services for ViewModels

```python
@pytest.fixture
def mock_file_service(mocker):
    """Provide mock file service for testing ViewModels."""
    mock_service = mocker.Mock()
    mock_service.load_files.return_value = []
    mock_service.save_file.return_value = True
    return mock_service
```

### Mock Qt Dialogs

```python
@patch("PySide6.QtWidgets.QFileDialog.getOpenFileName")
def test_file_selection(mock_file_dialog, qapp):
    """Test file selection dialog."""
    mock_file_dialog.return_value = ("/path/to/file", "")
    # ... test code ...
```

## Type Safety Testing

Tests validate that runtime behavior matches type annotations:

```python
def test_function_accepts_expected_types():
    """Test that function accepts and returns expected types."""
    # Arrange
    input_data: list[str] = ["item1", "item2"]

    # Act
    result: bool = process_data(input_data)

    # Assert
    assert isinstance(result, bool)
```

## Coverage Configuration

Coverage settings are defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["DFBU/tests"]
addopts = [
    "-v",
    "--cov=DFBU",
    "--cov-report=term-missing",
    "--cov-report=html",
]
```

Coverage reports are generated in:

- **Terminal**: Shows coverage summary with missing lines
- **HTML**: Detailed report in `DFBU/htmlcov/index.html`

## Test Results Summary

**Total Tests**: 553

- **Passed**: 551 (99.64%)
- **Skipped**: 2 (0.36%)
- **Failed**: 0 (0%)

**Execution Time**: ~5-15 seconds for full suite

## Skipped Tests

Two View layer tests are intentionally skipped:

1. `test_browse_path_selects_file` - Complex QMessageBox interaction
2. `test_browse_path_falls_back_to_directory` - Complex QMessageBox interaction

**Reason**: These tests require intricate mocking of Qt dialog lifecycle. Per
test.prompt.md guidelines, View tests are optional when mocking complexity outweighs
testing value. The functionality is verified through manual testing and integration
tests.

## Continuous Integration

Tests are designed to run in CI/CD environments:

```bash
# CI test command
pytest DFBU/tests/ --cov=DFBU --cov-report=xml --cov-report=term
```

## Adding New Tests

### 1. Choose Test Location

- **Model tests**: `test_model*.py`
- **ViewModel tests**: `test_viewmodel*.py`
- **View tests**: `test_view*.py`
- **Integration tests**: `test_*_integration.py` or existing integration files

### 2. Follow Naming Conventions

```python
class TestComponentName:
    """Test suite for ComponentName functionality."""

    def test_should_do_something_when_condition(self, fixtures):
        """Test that component does something under specific condition."""
        # Arrange
        # Act
        # Assert
```

### 3. Use Appropriate Fixtures

```python
def test_with_temp_file(tmp_path, temp_dotfile):
    """Test using temporary file fixture."""
    # Test implementation
```

### 4. Add Test Markers

```python
@pytest.mark.unit
def test_isolated_function():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_component_interaction():
    """Integration test."""
    pass

@pytest.mark.slow
def test_long_operation():
    """Slow test."""
    pass
```

### 5. Mock External Dependencies

```python
def test_with_mocks(mocker):
    """Test with mocked dependencies."""
    mock_service = mocker.Mock()
    mock_service.method.return_value = "expected"
    # Test implementation
```

## Troubleshooting

### QApplication Not Created Error

**Solution**: Use `qapp` fixture from conftest.py

```python
def test_qt_component(qapp):
    """Test requiring QApplication."""
    # Test implementation
```

### Signal Not Emitted Error

**Solution**: Use `qtbot.waitSignal()` with timeout

```python
def test_signal_emission(qtbot):
    """Test signal emission."""
    with qtbot.waitSignal(vm.signal_name, timeout=1000):
        vm.trigger_signal()
```

### Import Errors

**Solution**: Check that test file adds parent to path

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))
```

### Qt Pilot Segfaults During GUI Automation

**Symptoms**:

- Qt Pilot command returns `Expecting value: line 1 column 1 (char 0)`
- App process exits with code `-11`
- Stderr shows repaint/backing-store errors such as:
  - `QWidget::repaint: Recursive repaint detected`
  - `QBackingStore::endPaint() called with active painter`

**What this means**:

- Current evidence shows this can reproduce in a minimal standalone PySide6 app.
- Treat these failures as Qt Pilot harness instability unless reproduced by pytest-qt or
  manual testing.

**Recommended approach**:

1. Use Qt Pilot for smoke checks (launch, widget discovery, screenshots).
2. Prefer `click_widget` over `click_at`.
3. Use `wait_for_idle` between each interaction.
4. Validate dialog-heavy behavior with pytest-qt and manual tests.

For full details and investigation artifacts, see:

- `docs/QT_PILOT_TESTING_NOTES.md`

## Best Practices Summary

✅ **DO**:

- Store all tests in `DFBU/tests/` directory
- Follow AAA pattern (Arrange-Act-Assert)
- Use descriptive test names
- Mock external dependencies
- Test signal emissions with pytest-qt
- Target 80%+ coverage on critical paths
- Keep tests fast and isolated

❌ **DON'T**:

- Place tests in base project directory
- Test implementation details
- Create flaky tests dependent on timing
- Test framework code (Qt, Python stdlib)
- Over-mock simple functionality
- Write tests that depend on each other

## Resources

- **Pytest Documentation**: <https://docs.pytest.org/>
- **pytest-qt Plugin**: <https://pytest-qt.readthedocs.io/>
- **PySide6 Testing**: <https://doc.qt.io/qtforpython/>
- **Test Prompt Guidelines**: `.github/prompts/test.prompt.md`
- **Project Architecture**: `AGENTS.md`, `.github/copilot-instructions.md`

---

**Last Updated**: February 6, 2026 **Maintainer**: Chris Purcell <chris@l3digital.net>
**License**: MIT
