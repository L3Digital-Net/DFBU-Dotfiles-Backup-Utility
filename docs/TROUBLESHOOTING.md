# DFBU Troubleshooting Guide

This guide covers common issues and their solutions. For quick answers, see the
[README troubleshooting section](../README.md#troubleshooting).

---

## Installation Issues

### Setup script fails

**Symptom:** `./scripts/setup.sh` exits with an error.

**Solutions:**

1. Ensure you have internet connectivity (UV downloads Python)
2. Check if curl is installed: `which curl`
3. Try running with verbose output: `bash -x ./scripts/setup.sh`
4. If UV fails to install, install it manually:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### "Python 3.14+ required" error

**Symptom:** Error message about Python version when launching DFBU.

**Solutions:**

1. Re-run the setup script: `./scripts/setup.sh`
2. Verify Python version: `python --version`
3. If using a custom Python installation, ensure it's 3.14 or higher
4. Check your virtual environment is activated: `source .venv/bin/activate`

### Virtual environment not found

**Symptom:** "No such file or directory: .venv/bin/activate"

**Solutions:**

1. Run the setup script first: `./scripts/setup.sh`
2. Or create manually: `uv venv && uv pip install -r DFBU/requirements.txt`

---

## Backup Issues

### "Permission denied" errors

**Symptom:** Some files fail to backup with permission errors.

**Cause:** DFBU runs as your user and can only read files you have permission to access.

**Solutions:**

1. Check file permissions: `ls -la ~/.config/problem-file`
2. For system files in `/etc/`, consider running as root (not recommended for GUI apps)
3. Exclude problematic files using the session exclusion feature

### Backup takes too long

**Symptom:** Backup appears stuck or takes much longer than expected.

**Causes:**

- Large directories (browser caches, IDE indexes)
- Many small files
- Slow destination drive

**Solutions:**

1. Enable size warnings in Settings to identify large directories
2. Add exclusion patterns to `.dfbuignore`:

   ```
   **/.cache/
   **/Cache/
   **/.mozilla/firefox/*/cache2/
   ```

3. Use mirror mode for faster incremental backups (only copies changed files)

### Backup is unexpectedly large

**Symptom:** Backup size is much larger than expected.

**Common large directories:**

| Directory                  | Typical Size  | Safe to Exclude?    |
| -------------------------- | ------------- | ------------------- |
| `~/.cache/`                | 1-10 GB       | Yes                 |
| `~/.config/google-chrome/` | 1-5 GB        | Partially (Cache/)  |
| `~/.mozilla/firefox/`      | 500 MB - 5 GB | Partially (cache2/) |
| `~/.local/share/Steam/`    | 10-100+ GB    | Usually             |
| `~/.local/share/Trash/`    | Varies        | Yes                 |

**Solutions:**

1. Use the size warning feature (Settings tab) to identify large items
2. Add patterns to `DFBU/data/.dfbuignore` for directories you don't need
3. Exclude specific applications using the session exclusion feature

### Mirror backup shows no changes

**Symptom:** "0 files copied" even though files have changed.

**Causes:**

- Files haven't actually changed since last backup
- Backup destination has newer timestamps (clock skew)

**Solutions:**

1. Use the "Force Backup" option to copy all files regardless of timestamps
2. Check system clock on both source and destination

---

## Restore Issues

### Restore button is grayed out

**Symptom:** Cannot click the Restore button.

**Causes:**

- No backup directory selected
- Selected directory doesn't contain valid backups
- Hostname mismatch

**Solutions:**

1. Use "Browse" to select your backup directory
2. Navigate to the correct hostname subfolder
3. Ensure the backup was created by DFBU (should contain dated folders)

### "Hostname mismatch" warning

**Symptom:** Warning about backup from different computer.

**Explanation:** DFBU organizes backups by hostname. If you're restoring on a different
computer than where the backup was created, paths may not match.

**Solutions:**

1. Proceed with caution - file paths may differ
2. Manually copy needed files from the backup directory
3. Rename the backup's hostname folder to match current computer (advanced)

### Restore overwrites wrong files

**Symptom:** Restore affected files you didn't intend to change.

**Prevention:**

1. Always enable "Pre-Restore Backup" in Settings (on by default)
2. Review the file list before clicking Restore
3. Use selective restore to restore only specific files

**Recovery:**

1. If Pre-Restore Backup was enabled, find your safety backup in:

   ```
   ~/.local/share/dfbu/restore-backups/
   ```

2. Files are organized by timestamp - find the most recent one before your restore
3. Manually copy back any files you need

---

## Configuration Issues

### Settings not saving

**Symptom:** Changes to settings are lost after restart.

**Causes:**

- Configuration directory permissions
- Corrupted config file

**Solutions:**

1. Check directory permissions: `ls -la DFBU/data/`
2. Verify settings.yaml is writable: `touch DFBU/data/settings.yaml`
3. If corrupted, delete and let DFBU recreate:

   ```bash
   mv DFBU/data/settings.yaml DFBU/data/settings.yaml.bak
   ```

### Dotfile list is empty after update

**Symptom:** All configured dotfiles disappeared.

**Cause:** Usually a corrupted or overwritten `dotfiles.yaml`.

**Solutions:**

1. Check for backup configs in `DFBU/data/`:

   ```bash
   ls -la DFBU/data/*.backup
   ```

2. Restore from backup: `cp DFBU/data/dotfiles.yaml.backup DFBU/data/dotfiles.yaml`
3. If no backup exists, re-add your dotfiles

### Config file syntax error

**Symptom:** Error loading configuration on startup.

**Cause:** Invalid YAML syntax (often from manual editing).

**Solutions:**

1. Check YAML syntax - common issues:
   - Missing colons after keys
   - Incorrect indentation (use spaces, not tabs)
   - Unquoted special characters
2. Use a YAML validator:
   `python -c "import yaml; yaml.safe_load(open('DFBU/data/settings.yaml'))"`
3. Restore from backup or delete the problematic file

---

## GUI Issues

### Window doesn't appear

**Symptom:** DFBU seems to start but no window shows.

**Causes:**

- Display server issues
- Window opened off-screen
- Qt platform plugin problems

**Solutions:**

1. Try resetting window position:

   ```bash
   rm ~/.config/dfbu/window_state.json
   ```

2. Force X11 mode: `QT_QPA_PLATFORM=xcb python DFBU/dfbu_gui.py`
3. Check for error messages in terminal

### UI elements look broken or missing

**Symptom:** Buttons missing, text cut off, or layout issues.

**Causes:**

- Qt theme incompatibility
- Missing fonts
- High DPI scaling issues

**Solutions:**

1. Try different Qt style:

   ```bash
   QT_STYLE_OVERRIDE=Fusion python DFBU/dfbu_gui.py
   ```

2. For high DPI displays:

   ```bash
   QT_SCALE_FACTOR=1.5 python DFBU/dfbu_gui.py
   ```

### Progress bar stuck

**Symptom:** Progress bar doesn't update during backup/restore.

**Note:** This doesn't necessarily mean the operation is stuck - file operations
continue in the background.

**Solutions:**

1. Check the log panel for activity
2. Wait - large file operations can take time
3. If truly stuck, close and reopen DFBU (backup may be incomplete)

---

## Log Files

DFBU logs are stored in:

```
~/.local/share/dfbu/logs/
```

To view recent logs:

```bash
tail -100 ~/.local/share/dfbu/logs/dfbu.log
```

When reporting issues, include relevant log entries.

---

## Getting More Help

### Before reporting an issue

1. Check this troubleshooting guide
2. Review the [README](../README.md)
3. Search
   [existing issues](https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility/issues)

### How to report a bug

1. Go to
   [GitHub Issues](https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility/issues/new)
2. Include:
   - DFBU version (shown in Help > About)
   - Linux distribution and version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Relevant log entries

---

## FAQ

### Can I backup to a network drive?

Currently, DFBU only supports local paths. Network drives mounted as local paths (via
NFS, SSHFS, etc.) may work but are not officially supported.

### Can I schedule automatic backups?

Not yet - this is a planned feature for a future version. For now, you can use cron with
the CLI (if available) or launch DFBU manually.

### Can I restore to a different computer?

Yes, but with caveats:

- File paths must exist on the target computer
- User home directory path should match
- Some application configs may include absolute paths that won't work

### Does DFBU backup hidden files?

Yes - dotfiles are hidden files by convention (starting with `.`). DFBU handles them
like any other file.

### How do I exclude specific files or patterns?

Two ways:

1. **Session exclusions:** In the Backup tab, uncheck applications you don't want to
   backup this time
2. **Permanent exclusions:** Edit `DFBU/data/.dfbuignore` to add gitignore-style
   patterns

---

Last Updated: February 2026
