# Qt Pilot Testing Notes

This document captures confirmed findings from Qt Pilot GUI testing for DFBU.

## Scope

These notes apply to automated GUI smoke testing driven by the Qt Pilot harness.

## Findings (Confirmed on February 6, 2026)

1. Intermittent GUI process crashes occur during Qt Pilot interaction.
2. Crash signatures include:
   - `exit_code: -11`
   - `QWidget::repaint: Recursive repaint detected`
   - `QBackingStore::endPaint() called with active painter`
3. The same crash pattern reproduces in a minimal standalone PySide6 app
   (`/tmp/qtpilot_minimal.py`), not only in DFBU.
4. This indicates the issue is in the Qt Pilot/harness interaction path, not a proven
   DFBU application logic defect.

## Practical Testing Guidance

Use Qt Pilot as a constrained smoke tool:

- Reliable uses:
  - app launch checks
  - widget discovery/object-name validation
  - screenshot capture
  - simple navigation with paced interactions
- Unreliable uses (until harness bug is fixed):
  - rapid click-heavy flows
  - coordinate-based clicking (`click_at`) as a primary strategy
  - treating failures in these flows as release-blocking DFBU regressions

## Stable Interaction Profile

For best reliability:

1. Prefer `click_widget` over `click_at`.
2. Add `wait_for_idle` between each interaction.
3. Use keyboard confirm/close (`Enter`) for modal dialogs when possible.
4. Keep Qt Pilot failures in flaky paths as non-gating evidence unless reproduced by
   pytest-qt or manual testing.

## Release/CI Policy Recommendation

Qt Pilot should currently be treated as:

- a smoke/monitoring layer for basic GUI health, not
- an authoritative gating layer for modal interaction correctness.

Use pytest-qt and focused manual tests for behavior validation in dialog-heavy
workflows.

## Evidence Artifacts

Screenshots and debug captures from this investigation are in:

- `qt_pilot_screenshots/`

Representative files:

- `qt_pilot_screenshots/debug_phase1_help_open.png`
- `qt_pilot_screenshots/debug_phase1_help_closed.png`
- `qt_pilot_screenshots/debug_dfbu_paced_sequence.png`
- `qt_pilot_screenshots/debug_minimal_launch.png`
- `qt_pilot_screenshots/debug_minimal_no_click.png`
