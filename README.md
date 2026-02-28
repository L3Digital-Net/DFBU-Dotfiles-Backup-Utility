# DFBU — DotFiles Backup Utility

DFBU is a Linux desktop application (PySide6/Qt) for backing up and restoring your
dotfiles (e.g. `~/.bashrc`, `~/.config/`, `~/.local/share/`).

**Platform:** Linux • **License:** MIT

## Highlights

- **Mirror + Archive backups**: readable folder mirrors and/or compressed `.tar.gz`
  archives
- **Safe restores**: optional pre-restore safety backups (undo-friendly)
- **Verification**: optional post-backup verification + hash verification
- **Profiles**: save and switch between backup selections/options
- **Quality-of-life**: verbose logs, per-file skip logging, hide missing sources,
  built-in help

## Install (Recommended: AppImage)

1. Download `DFBU-x86_64.AppImage` from GitHub Releases
2. Make it executable: `chmod +x DFBU-x86_64.AppImage`
3. Run it: `./DFBU-x86_64.AppImage`

Notes:

- Some distros require `libfuse2` for AppImages.
- If you see OpenGL/EGL-related errors, install `libegl1` and `libgl1`.

## Run From Source (Development)

### Using `uv` (matches CI)

```bash
uv python install 3.14
uv sync --all-extras --dev
uv run python DFBU/dfbu_gui.py
```

### Tests / Lint

```bash
uv run ruff check DFBU/
uv run ruff format --check DFBU/
uv run mypy DFBU/
uv run pytest DFBU/tests/
```

## Configuration

DFBU uses **YAML** configuration files:

- `settings.yaml`: backup paths + options
- `dotfiles.yaml`: dotfile library entries
- `session.yaml`: session exclusions (what you’ve temporarily excluded)

Locations:

- **AppImage / packaged**: `~/.config/dfbu/`
- **Running from source**: `DFBU/data/` (development default)

Tip: the GUI includes an **Edit Config** action to open `dotfiles.yaml` in your editor.

## Keyboard Shortcuts

- `Ctrl+B`: Start Backup
- `Ctrl+R`: Start Restore
- `Ctrl+V`: Verify Backup
- `F1`: Open Help
- `Ctrl+Q`: Quit

## More Docs

- Changelog: `DFBU/docs/CHANGELOG.md`
- Architecture (MVVM): `DFBU/docs/ARCHITECTURE.md`
- Contributing: `CONTRIBUTING.md`

## License

MIT — see `LICENSE`.
