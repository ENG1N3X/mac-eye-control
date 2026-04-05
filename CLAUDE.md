# CLAUDE.md — Mac Eye Control

## Project

Mac Eye Control — hands-free macOS computer control via eye gaze and head movements.
Built on Python-Gaze-Face-Tracker (MediaPipe + OpenCV). See PRODUCT.md for full requirements.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Language |
| OpenCV (`cv2`) | Video capture, drawing |
| MediaPipe | Face mesh, iris tracking (468 landmarks) |
| NumPy | Math, array ops |
| `pyautogui` | Mouse movement, clicking, scrolling |
| `scikit-learn` | Polynomial regression for gaze mapping (Ridge) |
| `tkinter` | Calibration UI window |
| `json` | Config and calibration persistence |

---

## Project Structure

```
Python-Gaze-Face-Tracker/
├── src/
│   ├── tracking/
│   │   ├── __init__.py
│   │   ├── face_mesh.py          # MediaPipe FaceMesh wrapper
│   │   ├── iris_tracker.py       # Iris position extraction (float32 coords)
│   │   ├── iris_filter.py        # Rolling median spike filter for iris dx/dy
│   │   ├── blink_detector.py     # EAR-based blink detection + is_eyes_open()
│   │   ├── fixation_detector.py  # Consecutive-frame fixation detection
│   │   └── head_pose.py          # Pitch/yaw/roll estimation (display + calibrated)
│   ├── calibration/
│   │   ├── __init__.py
│   │   ├── calibration.py        # 9-point fixation-based calibration flow
│   │   └── mapping.py            # Polynomial Ridge regression gaze mapper
│   ├── control/
│   │   ├── __init__.py
│   │   ├── cursor.py             # Dual-speed adaptive EMA cursor + snap zones
│   │   ├── clicker.py            # Double-blink click logic
│   │   ├── scroller.py           # Head-tilt scroll logic
│   │   ├── snap_zones.py         # SnapZoneRegistry (rectangular zones)
│   │   └── mouse_monitor.py      # Manual mouse override detection (position-based)
│   ├── ui/
│   │   ├── __init__.py
│   │   └── calibration_ui.py     # Fullscreen tkinter calibration window
│   └── utils/
│       ├── __init__.py
│       ├── angle_buffer.py       # Rolling average buffer (legacy, still used for head pose)
│       └── config.py             # Config loader
├── config/
│   └── default_config.json       # All tunable parameters
├── data/
│   └── calibration.json          # Auto-generated, gitignored
├── logs/                         # CSV logs, gitignored
├── tests/
│   ├── __init__.py
│   ├── test_iris_tracker.py
│   ├── test_cursor_controller.py
│   ├── test_cursor_accuracy_mvp.py
│   └── test_calibration_session.py
├── tools/
│   └── mediapipe_landmarks_test.py  # Dev utility — visualize landmark indices
├── docs/
│   ├── overview.md
│   ├── calibration.md            # Calibration system documentation
│   ├── features/                 # Feature analysis docs
│   └── logs/                     # Token usage logs
├── main.py                       # Entry point (thin orchestrator)
├── AngleBuffer.py                # Legacy — do not use, use src/utils/angle_buffer.py
├── requirements.txt
├── README.md
├── PRODUCT.md
└── CLAUDE.md
```

---

## Development Phases

### Phase 1 — Calibration ✅ DONE
- Fullscreen 9-point calibration window (tkinter, `overrideredirect` fullscreen)
- Fixation-based collection: 20 consecutive stable frames required per point
- Eyes-open check via `BlinkDetector.is_eyes_open()` — closed eyes reset fixation counter
- Gaze shift requirement: iris must move ≥ 3 px from previous point before fixation counts
- Polynomial Ridge regression (degree 2) fit on `(iris_dx, iris_dy, pitch, yaw)` → `(screen_x, screen_y)`
- Saved to `data/calibration.json`; loaded on startup; recalibration via `R` key

### Phase 2 — Cursor Control ✅ DONE
- Gaze mapper output → `CursorController.move()`
- Dual-speed adaptive EMA: slow alpha at rest, fast alpha during saccades
- Deadzone: suppresses micro-tremor below `cursor_deadzone_px`
- Iris spike filter applied before `gaze_mapper.predict()`
- Manual mouse override: position-comparison based (no pynput), pauses/resumes gaze control

### Phase 3 — Double Blink Click ✅ DONE
- EAR-based blink via `BlinkDetector`, two blinks within 0.5 s → `pyautogui.click()`
- Single blinks do not trigger
- On-screen "CLICK" indicator (0.3 s)

### Phase 4 — Head Tilt Scroll ✅ DONE
- Calibrated pitch from `HeadPoseEstimator.estimate()`
- Thresholds: `scroll_threshold_pitch_up` (15°), `scroll_threshold_pitch_down` (−15°)
- Speed proportional to pitch beyond threshold

### Phase 5 — Config & Polish ✅ DONE
- All parameters in `config/default_config.json`
- Hotkeys: C (reset head pose), R (recalibrate), P (toggle cursor), S (recording), Q (quit)
- On-screen controls hint overlay (bottom-right corner)
- Head pose reset confirmation message overlay

### Cursor Accuracy MVP ✅ DONE
- `IrisFilter` — rolling median + spike rejection (`src/tracking/iris_filter.py`)
- `SnapZoneRegistry` — rectangular snap-to-zone lookup (`src/control/snap_zones.py`)
- Dual-speed adaptive EMA in `CursorController` (replaces single fixed alpha)
- Iris coordinates switched from `int32` to `float32` (native `cv2.minEnclosingCircle` output)

---

## Key Parameters (current defaults)

```json
{
  "camera_index": 0,
  "blink_threshold": 0.51,
  "blink_consec_frames": 2,
  "blink_double_interval_sec": 0.5,
  "scroll_threshold_pitch_up": 15,
  "scroll_threshold_pitch_down": -15,
  "scroll_speed": 5,
  "smoothing_alpha": 0.08,
  "cursor_alpha_fast": 0.35,
  "cursor_fast_velocity_threshold_px": 80,
  "cursor_deadzone_px": 8,
  "iris_filter_window": 5,
  "iris_spike_threshold_px": 8.0,
  "snap_zones": [],
  "calibration_dwell_sec": 1.0,
  "calibration_points": 9,
  "calibration_collect_frames": 30,
  "calibration_gaze_shift_px": 3,
  "fixation_window_frames": 20,
  "fixation_movement_threshold": 2.5,
  "manual_mouse_timeout_sec": 0.5,
  "manual_mouse_threshold_px": 15
}
```

---

## macOS Notes

- `pyautogui` requires **Accessibility permissions** — System Settings → Privacy & Security → Accessibility
- MacBook built-in webcam index is `0`
- `cv2.imshow` is used only for the tracking overlay (non-blocking with `waitKey(1)`)
- Calibration window uses `overrideredirect(True)` + manual `geometry(WxH+0+0)` instead of `-fullscreen True` — the latter bypasses `withdraw()` on macOS Tk 8.6 and causes AppKit crashes
- `CalibrationUI` must be created on the main thread **before** `cv2.imshow` is ever called — creating a `tk.Tk()` instance after OpenCV has started its window causes `NSInvalidArgumentException` on macOS
- `CalibrationUI.close()` calls `withdraw()` (not `destroy()`) — the Tk instance is reused across recalibrations

---

## Agent Commands

Use these slash commands to implement phases via AI agents:

| Command | When to use |
|---------|-------------|
| `/implement-phase <phase>` | Implement a phase whose plan already exists in `docs/features/development-plan.md`. Skips planner — goes directly to developer → tester. Lean test scope (15–25 tests). |
| `/new-feature <description>` | Implement a new feature with no existing plan. Runs planner → developer → tester. |
| `/analyze-feature <description>` | Analyze and document a feature idea before implementation. Saves result to `docs/features/`. |

After each command completes, update `docs/logs/token_usage.md` with agent token counts.

---

## Rules

- Do not modify `AngleBuffer.py` — it works, extend it if needed
- Do not break existing `main.py` logic — refactor incrementally
- Keep each phase in its own module; `main.py` orchestrates
- No hardcoded screen resolutions — always query via `pyautogui.size()`
- Do not use `time.sleep()` in the main tracking loop — it will drop frames
- tkinter windows must be created and used on the main thread (macOS requirement)
- Ask before adding new dependencies not listed in this file
- Calibration tests (`test_calibration_session.py`) test function logic only — no UI or camera hardware; use `fixation_window_frames: 1`, `fixation_movement_threshold: 100`, `calibration_gaze_shift_px: 0` in MINIMAL_CONFIG to avoid infinite loops
