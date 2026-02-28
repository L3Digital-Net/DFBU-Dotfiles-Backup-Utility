#!/usr/bin/env bash
#
# Format all markdown files in the project with Prettier
#
# Usage:
#   ./scripts/format-markdown.sh [path]
#
# Examples:
#   ./scripts/format-markdown.sh           # Format all markdown files
#   ./scripts/format-markdown.sh docs/     # Format only docs/ directory
#   ./scripts/format-markdown.sh README.md # Format single file

set -euo pipefail

# Default to all markdown files if no path specified
TARGET="${1:-**/*.md}"

echo "Formatting markdown files: $TARGET"

# Use npx to ensure Prettier is available
npx prettier --write "$TARGET" \
    --prose-wrap always \
    --print-width 88

echo "✓ Formatting complete!"
