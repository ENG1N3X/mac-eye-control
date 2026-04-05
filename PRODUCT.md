# Mac Eye Control — Product Requirements

## Overview

**Mac Eye Control** is a macOS application that enables hands-free computer control using eye gaze and head movements tracked via a built-in MacBook webcam. Built on top of Python-Gaze-Face-Tracker (MediaPipe + OpenCV).

Target user: personal use / experimentation.

---

## Core Interactions

| Action | Trigger |
|--------|---------|
| Move cursor | Gaze direction |
| Left click | Double blink within ~0.5 s |
| Scroll up | Head pitch up (above threshold) |
| Scroll down | Head pitch down (below threshold) |
| Pause/resume cursor | `P` key |
| Recalibrate | `R` key |
| Reset head pose baseline | `C` key |

---

## Features

### F1 — Gaze-to-Screen Calibration ✅
- Fullscreen 9-point (3×3 grid) calibration window via tkinter
- Each point requires the user to fixate with gaze visibly shifted to that point
- Fixation confirmed by 20 consecutive stable frames (movement < 2.5 px between frames)
- Eyes-open check — closed-eye frames reset the fixation counter (prevents calibrating with eyes shut)
- Gaze shift requirement — iris must move ≥ 3 px from the previous fixation point before the new one counts
- Collects 30 frames of `(iris_dx, iris_dy, pitch, yaw)` per point once fixation is confirmed
- Fits a degree-2 polynomial Ridge regression model from eye features to logical screen coordinates
- Saves model to `data/calibration.json`; loads automatically on subsequent launches
- Recalibration available at any time via `R` key (also resets head pose baseline)

### F2 — Cursor Control ✅
- Mouse cursor moves in real time following the user's gaze
- **Iris spike filter** — rolling median over last 5 frames per axis; single-frame spikes > 8 px are suppressed before reaching the gaze mapper
- **Dual-speed adaptive EMA** — slow alpha (0.08) at rest for jitter suppression; fast alpha (0.35) during saccades (velocity > 80 px) for quick target acquisition
- **Deadzone** — cursor ignores movement < 8 px to prevent micro-tremor drift
- **Snap zones** — optional rectangular zones in logical screen points; cursor locks to zone center when inside (configurable, empty by default)
- **Manual mouse override** — gaze control automatically pauses when trackpad/mouse movement > 15 px is detected; resumes after 0.5 s of inactivity; EMA buffer is cleared on resume to prevent jumps
- Cursor always visible; position updated via `pyautogui.moveTo()` (logical screen points)

### F3 — Double Blink Click ✅
- Two blinks detected within `blink_double_interval_sec` (default 0.5 s) fires a left mouse click
- Single blinks (natural) do not trigger a click
- Blink detected via Eye Aspect Ratio (EAR) threshold — `blink_threshold: 0.51`, confirmed over `blink_consec_frames: 2` consecutive frames
- Brief "CLICK" indicator shown on the video feed for 0.3 s after each click

### F4 — Head Tilt Scroll ✅
- Head pitch above `scroll_threshold_pitch_up` (default 15°) → scroll up
- Head pitch below `scroll_threshold_pitch_down` (default −15°) → scroll down
- Neutral head position = no scroll
- Scroll speed proportional to pitch magnitude beyond threshold (configurable `scroll_speed`)
- Pitch measured relative to a user-defined neutral baseline (reset with `C` key)

### F5 — Configuration & Controls ✅
- All thresholds and parameters in `config/default_config.json` — no source code edits needed
- Hotkeys:
  - `C` — reset head pose baseline (current position becomes neutral)
  - `R` — full recalibration (resets head pose, then runs 9-point calibration)
  - `P` — toggle cursor control on/off
  - `S` — start/stop CSV data recording
  - `Q` — quit
- On-screen controls hint in bottom-right corner of the video window
- On-screen head pose reset confirmation message (2 s)
- Clean per-frame console output (disabled by default via `print_data: false`)

---

## Platform
- macOS only (MacBook built-in webcam)
- Python 3.x
- Requires Accessibility permission for `pyautogui` cursor control

---

## Out of Scope (for now)
- IR camera support
- Eye gesture shortcuts (wink, etc.)
- On-screen gaze keyboard
- Multi-monitor support
- Windows / Linux support
- Dynamic snap zone inference (auto-learning icon positions)
- Per-user profile persistence for snap zones
- Kalman filter / predictive gaze smoothing
