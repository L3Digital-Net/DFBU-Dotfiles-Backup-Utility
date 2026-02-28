<!-- @format -->

# DFBU Documentation Index

This index provides a roadmap to all documentation in the DFBU project. Documents are
organized by audience and purpose.

---

## Quick Links by Audience

| Audience          | Start Here                                                               |
| ----------------- | ------------------------------------------------------------------------ |
| **Users**         | [README.md](../README.md) - Installation and usage                       |
| **Developers**    | [CONTRIBUTING.md](../CONTRIBUTING.md) - Development setup and guidelines |
| **AI Assistants** | [CLAUDE.md](../CLAUDE.md) - Claude Code instructions                     |

---

## User Documentation

For Linux users who want to backup their configuration files.

| Document                                  | Description                                   |
| ----------------------------------------- | --------------------------------------------- |
| [README.md](../README.md)                 | Installation, features, and quick start guide |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md)  | Common issues and solutions                   |
| [CHANGELOG.md](../DFBU/docs/CHANGELOG.md) | Version history and release notes             |

---

## Developer Documentation

For contributors and developers working on DFBU.

### Getting Started

| Document                                     | Description                                       |
| -------------------------------------------- | ------------------------------------------------- |
| [CONTRIBUTING.md](../CONTRIBUTING.md)        | Development setup, code standards, and PR process |
| [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) | Branch protection rules (read before committing)  |

### Architecture & Design

| Document                                                     | Description                                   |
| ------------------------------------------------------------ | --------------------------------------------- |
| [ARCHITECTURE.md](../DFBU/docs/ARCHITECTURE.md)              | Comprehensive MVVM architecture documentation |
| [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) | Threading and performance improvements        |

### Testing

| Document                                               | Description                                                         |
| ------------------------------------------------------ | ------------------------------------------------------------------- |
| [tests/README.md](../DFBU/tests/README.md)             | Test suite documentation, fixtures, and coverage                    |
| [QT_PILOT_TESTING_NOTES.md](QT_PILOT_TESTING_NOTES.md) | Known Qt Pilot instability, safe usage profile, and policy guidance |

### Scripts & Setup

| Document                                            | Description                                   |
| --------------------------------------------------- | --------------------------------------------- |
| [scripts/README.md](../scripts/README.md)           | Setup scripts and development utilities       |
| [.mypy-strict-config.md](../.mypy-strict-config.md) | Conservative MyPy type checking configuration |

---

## AI Assistant Documentation

For AI coding assistants (Claude, Copilot, etc.) working on the codebase.

| Document                                                              | Description                              | AI System         |
| --------------------------------------------------------------------- | ---------------------------------------- | ----------------- |
| [CLAUDE.md](../CLAUDE.md)                                             | Project context and coding instructions  | Claude Code       |
| [AGENTS.md](../AGENTS.md)                                             | Templates, patterns, and troubleshooting | General AI agents |
| [.agents/memory.instruction.md](../.agents/memory.instruction.md)     | Critical rules and preferences           | All AI agents     |
| [.github/copilot-instructions.md](../.github/copilot-instructions.md) | Coding guidelines and patterns           | GitHub Copilot    |

---

## Design & Planning Documents

Historical and active design documents.

### Active Plans

| Document                                                                           | Description                         |
| ---------------------------------------------------------------------------------- | ----------------------------------- |
| [plans/2026-02-05-v110-features-tdd.md](plans/2026-02-05-v110-features-tdd.md)     | v1.1.0 feature implementation (TDD) |
| [plans/2026-02-05-ui-refinement.md](plans/2026-02-05-ui-refinement.md)             | UI refinement plan                  |
| [plans/2026-02-04-ui-overhaul.md](plans/2026-02-04-ui-overhaul.md)                 | UI overhaul design                  |
| [plans/2026-02-04-appimage-packaging.md](plans/2026-02-04-appimage-packaging.md)   | AppImage packaging                  |
| [plans/plan-v110FeatureImplementation.md](plans/plan-v110FeatureImplementation.md) | v1.1.0 feature implementation plan  |

### Archived Plans

Completed or superseded design documents.

---

## UI & Design

| Document                                                                         | Description                        |
| -------------------------------------------------------------------------------- | ---------------------------------- |
| [designer/UI_GENERATION_REPORT.md](../DFBU/gui/designer/UI_GENERATION_REPORT.md) | Qt Designer UI component inventory |

---

## Documentation Maintenance

### Canonical Sources

To reduce duplication, these are the authoritative documents for key topics:

| Topic             | Canonical Source                                | Summary in                            |
| ----------------- | ----------------------------------------------- | ------------------------------------- |
| Architecture      | [ARCHITECTURE.md](../DFBU/docs/ARCHITECTURE.md) | CLAUDE.md, AGENTS.md, CONTRIBUTING.md |
| Branch Protection | [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md)    | All contributor docs                  |
| Testing           | [tests/README.md](../DFBU/tests/README.md)      | CLAUDE.md, CONTRIBUTING.md            |
| Code Standards    | [CONTRIBUTING.md](../CONTRIBUTING.md)           | AI agent docs                         |

When updating these topics, update the canonical source first, then verify summaries in
other documents remain accurate.

---

_Last updated: February 2026_
