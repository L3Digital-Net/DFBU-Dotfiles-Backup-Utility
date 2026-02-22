---
agent: agent
description:
  "Walk through the full DFBU release process: validate, version bump, merge, tag, and
  publish."
---

# DFBU Release Process

You are guiding the developer through publishing a new DFBU release. Work through each
phase sequentially. **Stop and confirm with the user before executing any destructive or
irreversible step** (merge, tag push).

## Context

- Repository: `L3DigitalNet/dfbu-dotfiles-backup-utility`
- Branch model: `testing` → PR/merge → `main` → version tag → GitHub Release
- Release workflow: `.github/workflows/release.yml` (triggered by `v*` tags)
- AppImage built in CI with embedded zsync update info

## Phase 1 — Pre-flight checks on `testing`

1. Verify we are on the `testing` branch:
   ```bash
   python .agents/branch_protection.py
   git branch --show-current
   ```
2. Ensure working tree is clean:

   ```bash
   git status --short
   ```

   If dirty, stop and ask the user whether to commit or stash.

3. Run the full test suite and type checker:

   ```bash
   uv run pytest DFBU/tests/ -x -q
   uv run mypy DFBU/
   uv run ruff check DFBU/
   ```

   **All three must pass with zero errors.** If any fail, stop and report.

4. Confirm the app launches without errors:
   ```bash
   timeout 5 uv run python DFBU/dfbu_gui.py || true
   ```

## Phase 2 — Determine the new version

Ask the user:

> What version are you releasing? (current is in `pyproject.toml`) Is this a MAJOR,
> MINOR, or PATCH bump?

Once confirmed, note the new version string (e.g. `1.3.0`).

## Phase 3 — Version bump

Update the version string in **all four locations**. Use search to verify each one
before editing:

| File                                       | Field                               |
| ------------------------------------------ | ----------------------------------- |
| `pyproject.toml`                           | `version = "X.Y.Z"`                 |
| `DFBU/__init__.py`                         | `__version__ = "X.Y.Z"`             |
| `DFBU/dfbu_gui.py`                         | `__version__: Final[str] = "X.Y.Z"` |
| `packaging/com.l3digital.dfbu.appdata.xml` | Add a new `<release>` element       |

For the appdata XML, add a new `<release>` entry **above** the existing ones:

```xml
<release version="X.Y.Z" date="YYYY-MM-DD">
  <description><p>Brief release summary.</p></description>
</release>
```

Then ask the user for the CHANGELOG entry content and prepend a new section to
`DFBU/docs/CHANGELOG.md` under the appropriate heading:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added

- ...

### Changed

- ...

### Fixed

- ...
```

After all edits, re-run the lock file update:

```bash
uv lock
```

## Phase 4 — Commit the version bump on `testing`

```bash
git add -A
git diff --cached --stat
```

Show the user the staged summary and confirm before committing:

```bash
git commit -m "chore: bump version to vX.Y.Z"
```

## Phase 5 — Merge to `main`

**Ask the user** which merge strategy they prefer:

1. **Fast-forward merge** (clean linear history):
   ```bash
   git checkout main
   git merge --ff-only testing
   ```
2. **Merge commit** (preserves branch history):
   ```bash
   git checkout main
   git merge --no-ff testing -m "Merge testing for vX.Y.Z release"
   ```
3. **GitHub PR** — the user creates the PR manually on GitHub.

If option 1 or 2: execute the merge, then push main:

```bash
git push origin main
```

Then switch back to testing:

```bash
git checkout testing
```

## Phase 6 — Tag and trigger the release

Create an annotated tag and push it:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Tell the user:

> The `vX.Y.Z` tag has been pushed. The **Release AppImage** workflow is now running at:
> https://github.com/L3DigitalNet/dfbu-dotfiles-backup-utility/actions
>
> It will:
>
> 1. Run the test suite
> 2. Build the AppImage with embedded update info
> 3. Create a GitHub Release with `DFBU-x86_64.AppImage` and `.zsync` attached

## Phase 7 — Post-release verification

Ask the user to verify:

- [ ] GitHub Actions workflow completed successfully
- [ ] Release page shows at
      https://github.com/L3DigitalNet/dfbu-dotfiles-backup-utility/releases
- [ ] `DFBU-x86_64.AppImage` and `.zsync` files are attached
- [ ] Release notes look correct

Offer to open the Actions page:

```
https://github.com/L3DigitalNet/dfbu-dotfiles-backup-utility/actions/workflows/release.yml
```

## Phase 8 — Sync testing branch

Ensure testing stays in sync with main after the release:

```bash
git checkout testing
git merge main
git push origin testing
```

## Done

Summarize what was released:

- Version number
- Files changed
- Release URL
