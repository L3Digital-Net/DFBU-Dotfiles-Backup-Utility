# Scripts Directory

This directory contains setup and utility scripts for the DFBU project.

## Files

### setup.sh

**Purpose**: Development environment setup script for Linux systems

**Description**: Automated setup script that configures the development environment for
DFBU. Checks for required dependencies, installs UV package manager if needed, creates a
virtual environment, and installs all project dependencies.

**Requirements**:

- Linux operating system
- Python 3.14+
- Internet connection for downloading UV and dependencies

**Features**:

- Checks Python version (requires 3.14+)
- Installs UV package manager if not present
- Creates virtual environment using UV
- Installs runtime dependencies from `DFBU/requirements.txt`
- Installs development dependencies (pytest, pytest-qt, pytest-mock, pytest-cov, mypy)
- Provides helpful usage instructions

**Usage**:

```bash
# From project root
./scripts/setup.sh

# Or run directly from scripts directory
cd scripts
./setup.sh
```

**Post-Setup**: After successful setup, activate the virtual environment:

```bash
source .venv/bin/activate
```

**Output**:

- Creates `.venv/` directory in project root
- Installs all dependencies
- Displays activation and usage instructions

### setup-branch-protection.sh

**Purpose**: Configure branch protection rules for GitHub repository

**Description**: Shell script that sets up branch protection for the `main` and
`testing` branches to prevent accidental direct commits. Implements the branch
protection workflow described in `BRANCH_PROTECTION.md`.

**Requirements**:

- Git repository initialized
- GitHub CLI (`gh`) installed and authenticated
- Repository owner/admin permissions

**Features**:

- Protects `main` branch from direct pushes
- Protects `testing` branch with appropriate rules
- Requires pull request reviews before merging
- Enforces status checks
- Prevents force pushes

**Usage**:

```bash
# From project root (recommended)
./scripts/setup-branch-protection.sh

# Or from scripts directory
cd scripts
./setup-branch-protection.sh
```

**Related Documentation**:

- `BRANCH_PROTECTION.md` - Complete branch protection documentation
- `BRANCH_PROTECTION_QUICK.md` - Quick reference guide
- `.agents/branch_protection.py` - Python checker for AI agents

### verify_test_setup.py

**Purpose**: Verify test environment configuration and dependencies

**Description**: Python script that validates the testing infrastructure is properly
configured. Checks for required testing packages, verifies pytest configuration, and
ensures test discovery is working correctly.

**Requirements**:

- Python 3.14+
- Virtual environment activated
- Testing dependencies installed

**Features**:

- Checks for pytest and plugins (pytest-qt, pytest-mock, pytest-cov)
- Verifies `DFBU/tests/` directory structure
- Validates `conftest.py` fixtures
- Checks mypy configuration
- Reports any missing dependencies or configuration issues

**Usage**:

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run verification
python scripts/verify_test_setup.py
```

**Output**:

- Reports status of each check (✅ or ❌)
- Lists any missing dependencies
- Provides remediation steps if issues found

**Exit Codes**:

- `0`: All checks passed
- `1`: One or more checks failed

## Development Workflow

### Initial Setup

1. Run `setup.sh` to configure development environment
2. Activate virtual environment: `source .venv/bin/activate`
3. Verify setup: `python scripts/verify_test_setup.py`

### Branch Protection (Repository Owners)

1. Ensure GitHub CLI is installed and authenticated
2. Run `setup-branch-protection.sh` to configure branch rules
3. Verify protection rules in GitHub repository settings

### Testing Verification

Before running tests, verify environment:

```bash
python scripts/verify_test_setup.py
```

If verification passes, run tests:

```bash
pytest DFBU/tests/
```

## Maintenance

### Updating Dependencies

To update project dependencies after modifying `DFBU/requirements.txt`:

```bash
source .venv/bin/activate
uv pip install -r DFBU/requirements.txt
```

### Recreating Environment

If the virtual environment becomes corrupted:

```bash
# Remove existing environment
rm -rf .venv

# Re-run setup
./scripts/setup.sh
```

## Related Documentation

- **Main README**: `../README.md` - Project overview and getting started
- **CONTRIBUTING**: `../CONTRIBUTING.md` - Contribution guidelines
- **Branch Protection**: `../BRANCH_PROTECTION.md` - Branch protection workflow
- **Testing Docs**: `../DFBU/tests/README.md` - Comprehensive test documentation

## Notes

- All scripts assume they are run from the project root directory
- Scripts use UV for dependency management (faster than pip)
- Setup script automatically adds UV to PATH if installed during execution
- Branch protection script requires GitHub repository owner permissions

---

**Last Updated**: November 5, 2025 **Maintainer**: Chris Purcell <chris@l3digital.net>
