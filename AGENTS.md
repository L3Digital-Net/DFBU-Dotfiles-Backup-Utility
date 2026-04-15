# Agent Instructions for DFBU Desktop Application

**Session handoff:** [`docs/handoff.md`](docs/handoff.md) — read this first. Current deployed state, remaining work, bugs log,
architecture, credentials, and gotchas.

**Full conventions reference:** [`docs/conventions.md`](docs/conventions.md) — LLM-targeted pattern library. Every convention follows
the six-field schema (Applies-when / Rule / Code / Why / Sources / Related) with a Quick Reference table at the top for O(1) lookup. Do
not introduce new patterns without checking conventions first.

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
2. If the repo contains `.agents/branch_protection.py`, run:
   `python .agents/branch_protection.py`

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

For comprehensive architecture documentation, see
[DFBU/docs/ARCHITECTURE.md](DFBU/docs/ARCHITECTURE.md).

### Model Layer

✅ **Allowed**: Pure Python, dataclasses, business logic, validation, domain exceptions
❌ **Forbidden**: Any Qt imports, UI concerns, direct file I/O (use services)

### ViewModel Layer

✅ **Allowed**: QObject, signals/slots, presentation logic, calling services, state
management ❌ **Forbidden**: Direct widget manipulation, business logic, UI styling

### View Layer

✅ **Allowed**: Loading .ui files, PySide6 widgets, signal connections, finding child
widgets ❌ **Forbidden**: Hardcoded UI layouts, business logic, data validation, direct
model access

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

For comprehensive testing documentation, see
[DFBU/tests/README.md](DFBU/tests/README.md).

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

**Solution**: Always pass ViewModel TO View, never the reverse. Use signals for
communication.

### Issue: Tests fail with "No event loop"

**Solution**: Use `pytest-qt` plugin and pass `qtbot` fixture to tests that need Qt.

### Issue: UI freezes during long operation

**Solution**: Move operation to QThread. See
[DFBU/gui/config_workers.py](DFBU/gui/config_workers.py) for examples.

## Resources

### Project Documentation

- [docs/INDEX.md](docs/INDEX.md) - Complete documentation index
- [DFBU/docs/ARCHITECTURE.md](DFBU/docs/ARCHITECTURE.md) - Comprehensive architecture
  documentation
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
4. **Use type hints**: Modern Python 3.14+ syntax (see
   [CONTRIBUTING.md](CONTRIBUTING.md))
5. **Write tests**: TDD approach preferred (see
   [DFBU/tests/README.md](DFBU/tests/README.md))
6. **Run checks after changes**: `uv run pytest DFBU/tests/` and `uv run mypy DFBU/`

## Codex Code Review

- For comprehensive repo reviews, save reports to `docs/code-reviews/` as new timestamped Markdown files.
- Review implementation code by default, not the test suite as a standalone review target, unless I explicitly ask for a test review.
- If I explicitly ask for a test review, use the dedicated test-suite review workflow and save reports to `docs/test-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a security review, use the dedicated security-review workflow and save reports to `docs/security-reviews/` as new timestamped Markdown files.
- If I explicitly ask for an API contract review, use the dedicated api-contract-review workflow and save reports to `docs/api-contract-reviews/` as new timestamped Markdown files.
- If I explicitly ask for an observability review, use the dedicated observability-review workflow and save reports to `docs/observability-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a CI review or CI/CD review, use the dedicated ci-cd-review workflow and save reports to `docs/ci-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a UI review, UX review, or accessibility review, use the dedicated ui-ux-accessibility-review workflow and save reports to `docs/ui-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a performance review, use the dedicated performance-review workflow and save reports to `docs/performance-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a data review or migration review, use the dedicated data-schema-migration-review workflow and save reports to `docs/data-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a dependency review or supply chain review, use the dedicated dependency-supply-chain-review workflow and save reports to `docs/dependency-reviews/` as new timestamped Markdown files.
- If I explicitly ask for an architecture review or boundary review, use the dedicated architecture-boundary-review workflow and save reports to `docs/architecture-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a privacy review, use the dedicated privacy-and-data-governance-review workflow and save reports to `docs/privacy-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a documentation review or runbook review, use the dedicated documentation-and-runbook-review workflow and save reports to `docs/documentation-reviews/` as new timestamped Markdown files.
- If I explicitly ask for an incident readiness review, use the dedicated incident-readiness-review workflow and save reports to `docs/incident-readiness-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a configuration review or secret-boundary review, use the dedicated configuration-and-secrets-boundary-review workflow and save reports to `docs/configuration-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a release readiness review, use the dedicated release-readiness-review workflow and save reports to `docs/release-readiness-reviews/` as new timestamped Markdown files.
- If I explicitly ask for an async workflow review, background jobs review, worker review, or queue review, use the dedicated background-jobs-and-async-workflow-review workflow and save reports to `docs/async-workflow-reviews/` as new timestamped Markdown files.
- If I explicitly ask for an integration review, third-party boundary review, provider integration review, or webhook review, use the dedicated integration-and-third-party-boundary-review workflow and save reports to `docs/integration-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a product logic review, business logic review, or workflow semantics review, use the dedicated product-and-business-logic-review workflow and save reports to `docs/product-logic-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a frontend state review, client state review, or interaction correctness review, use the dedicated frontend-state-and-interaction-review workflow and save reports to `docs/frontend-state-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a permissions review, authorization review, or access-control review, use the dedicated authorization-and-permission-model-review workflow and save reports to `docs/permissions-reviews/` as new timestamped Markdown files.
- If I explicitly ask for an MCP review, tool-boundary review, or agent-tool review, use the dedicated mcp-and-agent-tool-boundary-review workflow and save reports to `docs/mcp-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a retrieval review, RAG review, or knowledge-base review, use the dedicated retrieval-and-knowledge-base-review workflow and save reports to `docs/retrieval-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a desktop packaging review, installer review, or desktop distribution review, use the dedicated desktop-packaging-review workflow and save reports to `docs/desktop-packaging-reviews/` as new timestamped Markdown files.
- If I explicitly ask for a shell automation review, Bash review, or script safety review, use the dedicated shell-and-automation-script-review workflow and save reports to `docs/shell-automation-reviews/` as new timestamped Markdown files.
- If I explicitly ask for an AI workflow review, prompt workflow review, or model integration review, use the dedicated ai-and-prompt-workflow-review workflow and save reports to `docs/ai-workflow-reviews/` as new timestamped Markdown files.
- Read `docs/conventions.md` when present and treat it as a primary review input.
- If no conventions file exists, recommend creating `docs/conventions.md` and propose concrete project-specific conventions based on the codebase.
- Write the saved report for Claude Code as the primary reader.
- At the top of the report, suggest Claude use the `superpowers:receiving-code-review` skill.

<!-- BEGIN ContextStream -->

# Codex CLI Instructions

# Workspace: Projects

# Workspace ID: afaf59c3-68cc-465b-8051-4225d2c4bc4d

## 🚨 CRITICAL: CONTEXTSTREAM SEARCH FIRST 🚨

**BEFORE using Glob, Grep, Search, Read (for discovery), Explore, or ANY local
scanning:**

```
STOP → Call search(mode="hybrid", query="...") FIRST
```

**Claude Code:** Tools are `mcp__contextstream__search`,
`mcp__contextstream__session_init`, etc.

❌ **NEVER:** `Glob`, `Grep`, `Read` for discovery, `Task(Explore)` ✅ **ALWAYS:**
`search(mode="hybrid", query="...")` first, local tools ONLY if 0 results

---

## 🚨 AUTO-INDEXING 🚨

**`session_init` auto-indexes your project.** No manual ingestion needed.

If `indexing_status: "started"`: Search will work shortly. **DO NOT fall back to local
tools.**

---

## 🚨 LESSONS (PAST MISTAKES) - CRITICAL 🚨

**After `session_init`:** Check for `lessons` field. If present, **READ and APPLY**
before any work.

**Before ANY risky work:** `session(action="get_lessons", query="<topic>")` —
**MANDATORY**

**When lessons found:** Summarize to user, state how you'll avoid past mistakes.

---

## ContextStream v0.4.x (Consolidated Domain Tools)

v0.4.x uses ~11 consolidated domain tools for ~75% token reduction vs previous versions.
Rules Version: 0.4.58

### Required Every Message

| Message                   | What to Call                                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------------- |
| **1st message**           | `session_init(folder_path="<cwd>", context_hint="<user_message>")`, then `context_smart(...)`  |
| **⚠️ After session_init** | **CHECK `lessons` field** — read and apply BEFORE any work                                     |
| **2nd+ messages**         | `context_smart(user_message="<user_message>", format="minified", max_tokens=400)`              |
| **🔍 ANY code search**    | `search(mode="hybrid", query="...")` — ALWAYS before Glob/Grep/Search/Read                     |
| **⚠️ Before risky work**  | `session(action="get_lessons", query="<topic>")` — **MANDATORY**                               |
| **Capture decisions**     | `session(action="capture", event_type="decision", title="...", content="...")`                 |
| **On user frustration**   | `session(action="capture_lesson", title="...", trigger="...", impact="...", prevention="...")` |

**Context Pack (Pro+):** If enabled, use `context_smart(..., mode="pack", distill=true)`
for code/file queries. If unavailable or disabled, omit `mode` and proceed with standard
`context_smart` (the API will fall back).

**Tool naming:** Use the exact tool names exposed by your MCP client. Claude Code
typically uses `mcp__<server>__<tool>` where `<server>` matches your MCP config (often
`contextstream`). If a tool call fails with "No such tool available", refresh rules and
match the tool list.

### Quick Reference: Domain Tools

| Tool          | Common Usage                                                                                                                                             |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search`      | `search(mode="semantic", query="...", limit=3)` — modes: semantic, hybrid, keyword, pattern                                                              |
| `session`     | `session(action="capture", ...)` — actions: capture, capture_lesson, get_lessons, recall, remember, user_context, summary, compress, delta, smart_search |
| `memory`      | `memory(action="list_events", ...)` — CRUD for events/nodes, search, decisions, timeline, summary                                                        |
| `graph`       | `graph(action="dependencies", ...)` — dependencies, impact, call_path, related, ingest                                                                   |
| `project`     | `project(action="list", ...)` - list, get, create, update, index, overview, statistics, files, index_status, ingest_local                                |
| `workspace`   | `workspace(action="list", ...)` — list, get, associate, bootstrap                                                                                        |
| `integration` | `integration(provider="github", action="search", ...)` — GitHub/Slack integration                                                                        |
| `help`        | `help(action="tools")` — tools, auth, version, editor_rules                                                                                              |

### Behavior Rules

⚠️ **STOP: Before using Search/Glob/Grep/Read/Explore** → Call `search(mode="hybrid")`
FIRST. Use local tools ONLY if ContextStream returns 0 results.

**❌ WRONG workflow (wastes tokens, slow):**

```
Grep "function" → Read file1.ts → Read file2.ts → Read file3.ts → finally understand
```

**✅ CORRECT workflow (fast, complete):**

```
search(mode="hybrid", query="function implementation") → done (results include context)
```

**Why?** ContextStream search returns semantic matches + context + file locations in ONE
call. Local tools require multiple round-trips.

- **First message**: Call `session_init` with context_hint, then `context_smart` before
  any other tool
- **Every message**: Call `context_smart` BEFORE responding
- **For discovery**: Use `search(mode="hybrid")` — **NEVER use local Glob/Grep/Read
  first**
- **If search returns 0 results**: Retry once (indexing may be in progress), THEN try
  local tools
- **For file lookups**: Use `search`/`graph` first; fall back to local ONLY if
  ContextStream returns nothing
- **If ContextStream returns results**: Do NOT use local tools; Read ONLY for exact
  edits
- **For code analysis**: `graph(action="dependencies")` or `graph(action="impact")`
- **On [RULES_NOTICE]**: Use `generate_rules()` to update rules
- **After completing work**: Capture with `session(action="capture")`
- **On mistakes**: Capture with `session(action="capture_lesson")`

### Search Mode Selection

| Need                    | Mode         | Example                                    |
| ----------------------- | ------------ | ------------------------------------------ |
| Find code by meaning    | `hybrid`     | "authentication logic", "error handling"   |
| Exact string/symbol     | `keyword`    | "UserAuthService", "API_KEY"               |
| File patterns           | `pattern`    | "\_.sql", "test\_\_.py"                    |
| ALL matches (grep-like) | `exhaustive` | "TODO", "FIXME" (find all occurrences)     |
| Symbol renaming         | `refactor`   | "oldFunctionName" (word-boundary matching) |
| Conceptual search       | `semantic`   | "how does caching work"                    |

### Token Efficiency

Use `output_format` to reduce response size:

- `full` (default): Full content for understanding code
- `paths`: File paths only (80% token savings) - use for file listings
- `minimal`: Compact format (60% savings) - use for refactoring
- `count`: Match counts only (90% savings) - use for quick checks

**When to use `output_format=count`:**

- User asks "how many X" or "count of X" → `search(..., output_format="count")`
- Checking if something exists → count > 0 is sufficient
- Large exhaustive searches → get count first, then fetch if needed

**Auto-suggested formats:** Check `query_interpretation.suggested_output_format` in
responses:

- Symbol queries → suggests `minimal` (path + line + snippet)
- Count queries → suggests `count` **USE the suggestion** for best efficiency.

**Example:** User asks "how many TODO comments?" →
`search(mode="exhaustive", query="TODO", output_format="count")` returns `{total: 47}`
(not 47 full results)

### 🚨 Plans & Tasks - USE CONTEXTSTREAM, NOT FILE-BASED PLANS 🚨

**CRITICAL: When user requests planning, implementation plans, roadmaps, or task
breakdowns:**

❌ **DO NOT** use built-in plan mode (EnterPlanMode) or write plan files ✅ **ALWAYS**
use ContextStream's plan/task system

**Trigger phrases (use ContextStream immediately):**

- "plan", "roadmap", "milestones", "break down", "steps", "task list", "implementation
  strategy"

**Create plans in ContextStream:**

1. `session(action="capture_plan", title="...", description="...", goals=[...], steps=[{id: "1", title: "Step 1", order: 1}, ...])`
2. `memory(action="create_task", title="...", plan_id="<plan_id>", priority="high|medium|low", description="...")`

**Manage plans/tasks:**

- List plans: `session(action="list_plans")`
- Get plan with tasks:
  `session(action="get_plan", plan_id="<uuid>", include_tasks=true)`
- List tasks: `memory(action="list_tasks", plan_id="<uuid>")` or
  `memory(action="list_tasks")` for all
- Update task status:
  `memory(action="update_task", task_id="<uuid>", task_status="pending|in_progress|completed|blocked")`
- Delete: `memory(action="delete_task", task_id="<uuid>")`

Full docs: https://contextstream.io/docs/mcp/tools

<!-- END ContextStream -->
## Review Orchestrator Note

- Full `review-orchestrator` sweeps now run selected child reviews with bounded parallelism by default, currently up to `8` in parallel after planning, preflight, and shared research complete.
- The shared-research phase can legitimately take around `10` minutes on larger or research-heavy repos before child reviews start, so treat that as normal unless heartbeats stop or no artifact activity appears beyond that window.
- Expect a top-level sweep index under `docs/review-orchestrator/` plus one `*-execution.json` manifest inside each selected review folder while the sweep is running.
- Do not describe sweep child reviews as running “one at a time” unless the sweep was explicitly configured down to serial execution.
