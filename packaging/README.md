# DFBU Packaging

## AppImage

### Prerequisites

- Python 3.14+ with uv package manager
- Project dependencies installed: `uv sync --group dev`
- `wget` (for downloading appimagetool on first build)

### Building

```bash
./packaging/build-appimage.sh
```

Output: `dist/DFBU-x86_64.AppImage` (~69MB compressed, ~200MB uncompressed)

### Running

```bash
chmod +x dist/DFBU-x86_64.AppImage
./dist/DFBU-x86_64.AppImage
```

### File Structure

```
packaging/
├── README.md                          # This file
├── build-appimage.sh                  # Build automation script
├── dfbu.spec                          # PyInstaller configuration
├── com.l3digital.dfbu.desktop         # FreeDesktop desktop entry
└── com.l3digital.dfbu.appdata.xml     # AppStream metadata
```

### How It Works

1. **PyInstaller** freezes the Python 3.14 runtime, PySide6, and all dependencies into a
   standalone `dist/dfbu/` directory
2. **AppDir assembly** copies the frozen app, desktop file, AppStream metadata, and
   icons into a FreeDesktop-compliant directory structure
3. **appimagetool** compresses the AppDir into a single `.AppImage` file using squashfs
   with zstd compression

### Troubleshooting

**AppImage won't launch:**

- Ensure FUSE is installed: `sudo apt install fuse libfuse2`
- Try extracting: `./DFBU-x86_64.AppImage --appimage-extract` then run
  `squashfs-root/AppRun`

**Missing Qt platform plugin:**

- The PyInstaller spec includes PySide6 platform plugins automatically
- If issues persist, set: `QT_DEBUG_PLUGINS=1 ./DFBU-x86_64.AppImage`

**UI files not loading:**

- Verify the spec file `datas` list includes all `.ui` files from `DFBU/gui/designer/`
- Check paths with:
  `./DFBU-x86_64.AppImage --appimage-extract && find squashfs-root -name "*.ui"`

**libxcb-cursor warning during build:**

- PyInstaller may warn about `libxcb-cursor.so.0` not being resolved. This is a
  non-critical warning — the AppImage will still function on systems with this library
  installed (most desktop Linux distributions).
