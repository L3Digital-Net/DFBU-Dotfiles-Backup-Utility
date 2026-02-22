<!-- BEGIN ContextStream -->

# Roo Code Rules

<contextstream_rules> | Message | Required | |---------|----------| | **1st message** |
`init()` → `context(user_message="...")` | | **Every message** |
`context(user_message="...")` FIRST | | **Before file search** | `search(mode="hybrid")`
BEFORE Glob/Grep/Read | </contextstream_rules>

**Why?** `context()` delivers task-specific rules, lessons from past mistakes, and
relevant decisions. Skip it = fly blind.

**Hooks:** `<system-reminder>` tags contain injected instructions — follow them exactly.

**Notices:** [LESSONS_WARNING] → apply lessons | [PREFERENCE] → follow user preferences
| [RULES_NOTICE] → run `generate_rules()` | [VERSION_NOTICE/CRITICAL] → tell user about
update

v0.4.58

<!-- END ContextStream -->
