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
| File patterns           | `pattern`    | "_.sql", "test\__.py"                      |
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
