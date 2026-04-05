
# Mac Eye Control

### Hands-Free macOS Control via Eye Gaze and Head Movements

Built on Python-Gaze-Face-Tracker (MediaPipe + OpenCV). Control your Mac cursor, click, and scroll using only your eyes and head — no hands required.

---

![image](https://github.com/alireza787b/Python-Gaze-Face-Tracker/assets/30341941/08db0391-c13f-4252-9a88-9d32b77181b9)
![image](https://github.com/alireza787b/Python-Gaze-Face-Tracker/assets/30341941/8ad43aa9-dd3f-48b5-9e61-e375bc1db70f)

---

## Description

**Mac Eye Control** is a Python application for hands-free macOS computer control using eye gaze and head movements captured via a built-in MacBook webcam. Using MediaPipe FaceMesh (468 landmarks) and OpenCV, the system tracks iris position and head orientation in real time, maps gaze to screen coordinates via a 9-point calibration, and drives the mouse cursor accordingly.

Key capabilities:
- **Gaze cursor control** — cursor follows your eyes with adaptive smoothing and noise filtering
- **Double-blink clicking** — two blinks within 0.5 s fires a left click
- **Head-tilt scrolling** — pitch your head to scroll up or down
- **Smart calibration** — fixation-based 9-point calibration with eye-open and gaze-shift verification
- **Manual override** — gaze control automatically pauses when you touch the trackpad or mouse

---

## Features

- **9-Point Gaze Calibration** — fullscreen tkinter calibration window; each point requires the user to fixate (20 consecutive stable frames) with eyes open and gaze visibly shifted to that point. Saves to `data/calibration.json` and loads automatically on next launch.
- **Adaptive EMA Cursor Smoothing** — dual-speed exponential moving average: slow alpha at rest (reduces jitter), fast alpha during saccades (reaches target quickly). Configurable via `smoothing_alpha`, `cursor_alpha_fast`, `cursor_fast_velocity_threshold_px`.
- **Iris Spike Filter** — rolling median over the last N frames per axis with spike rejection. Eliminates single-frame MediaPipe outliers before they reach the cursor.
- **Deadzone Suppression** — cursor ignores sub-pixel micro-tremor when movement is below `cursor_deadzone_px`.
- **Snap Zones** — optional list of rectangular zones in logical screen points; when the cursor approaches a registered zone center it locks to it. Useful for toolbar icons and dock items.
- **Manual Mouse Override** — when trackpad or external mouse movement is detected, gaze control pauses automatically and resumes after a configurable timeout.
- **Double Blink Click** — two blinks within `blink_double_interval_sec` (default 0.5 s) fires `pyautogui.click()`. Single blinks are ignored. On-screen "CLICK" indicator shown briefly after each click.
- **Head Tilt Scroll** — pitch above/below configurable threshold scrolls up/down via `pyautogui.scroll()`. Speed proportional to pitch magnitude beyond threshold.
- **Real-Time Head Pose Reset** — press `C` at any time to set the current head position as the neutral baseline. On-screen confirmation shown for 2 seconds.
- **Facial Landmark Visualization** — optionally display all 468 MediaPipe landmarks and iris circles on the video feed.
- **CSV Data Logging** — toggle recording with `S`; saves timestamps, eye positions, blink count, and head pose angles to `logs/`.
- **UDP Telemetry** — iris position streamed over UDP socket for integration with external systems.

---

## Requirements

- Python 3.x
- macOS (MacBook built-in webcam, index `0`)
- **Accessibility permission** — System Settings → Privacy & Security → Accessibility → grant access to Terminal / your IDE

Python packages (see `requirements.txt`):
- `opencv-python`
- `mediapipe`
- `numpy`
- `pyautogui`
- `scikit-learn`
- `tkinter` (included with Python on macOS)

---

## Installation & Usage

1. **Clone the repository:**
   ```
   git clone https://github.com/alireza787b/Python-Gaze-Face-Tracker.git
   cd Python-Gaze-Face-Tracker
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Run:**
   ```
   python main.py
   ```
   Optionally specify a camera index:
   ```
   python main.py -c 1
   ```

4. **First launch** — a fullscreen 9-point calibration runs automatically. Look at each dot until the progress bar fills. Calibration is saved to `data/calibration.json` for subsequent launches.

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| `C` | Reset head pose — saves current head position as the neutral baseline for scroll control |
| `R` | Recalibrate gaze — resets head pose and runs the full 9-point calibration again |
| `P` | Toggle cursor control on/off |
| `S` | Start/stop CSV data recording |
| `Q` | Quit |

Controls are also shown in the bottom-right corner of the video window at runtime.

---

## Configuration

All parameters are in `config/default_config.json`. Key settings:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `camera_index` | `0` | Webcam index |
| `smoothing_alpha` | `0.08` | EMA alpha at rest (lower = smoother, slower) |
| `cursor_alpha_fast` | `0.35` | EMA alpha during fast saccades |
| `cursor_fast_velocity_threshold_px` | `80` | Velocity (px) that switches to fast alpha |
| `cursor_deadzone_px` | `8` | Minimum movement to update cursor position |
| `iris_filter_window` | `5` | Rolling median window for iris noise filter |
| `iris_spike_threshold_px` | `8.0` | Single-frame iris deviation treated as spike |
| `snap_zones` | `[]` | List of `{cx, cy, hw, hh}` zones in logical screen points |
| `blink_threshold` | `0.51` | EAR threshold for blink detection |
| `blink_double_interval_sec` | `0.5` | Max interval between two blinks for a click |
| `scroll_threshold_pitch_up` | `15` | Head pitch (degrees) to trigger scroll up |
| `scroll_threshold_pitch_down` | `-15` | Head pitch (degrees) to trigger scroll down |
| `scroll_speed` | `5` | Scroll units per frame when threshold exceeded |
| `calibration_dwell_sec` | `1.0` | Seconds of fixation required per calibration point |
| `calibration_points` | `9` | Number of calibration points (3×3 grid) |
| `manual_mouse_timeout_sec` | `0.5` | Seconds before gaze resumes after manual mouse move |
| `manual_mouse_threshold_px` | `15` | Movement (px) that counts as manual override |

---

## Data Logging & Telemetry

**CSV Logging** — toggle with `S` key. Files saved to `logs/` with timestamp in filename. Columns: timestamp, left/right eye centers, iris dx/dy, blink count, pitch/yaw/roll.

**UDP Telemetry** — iris data streamed to `server_ip:server_port` (default `127.0.0.1:7070`).

Packet structure (24 bytes):
- Timestamp — int64 (ms)
- Left Eye Center X — int32
- Left Eye Center Y — int32
- Left Iris Dx — int32
- Left Iris Dy — int32

---

## Project Structure

```
Python-Gaze-Face-Tracker/
├── src/
│   ├── tracking/
│   │   ├── face_mesh.py          # MediaPipe FaceMesh wrapper
│   │   ├── iris_tracker.py       # Iris position extraction (float coords)
│   │   ├── iris_filter.py        # Rolling median spike filter
│   │   ├── blink_detector.py     # EAR-based blink detection
│   │   ├── fixation_detector.py  # Consecutive-frame fixation detection
│   │   └── head_pose.py          # Pitch/yaw/roll estimation
│   ├── calibration/
│   │   ├── calibration.py        # 9-point fixation-based calibration flow
│   │   └── mapping.py            # Polynomial regression gaze mapper
│   ├── control/
│   │   ├── cursor.py             # Adaptive EMA cursor + snap zones
│   │   ├── clicker.py            # Double-blink click logic
│   │   ├── scroller.py           # Head-tilt scroll logic
│   │   ├── snap_zones.py         # SnapZoneRegistry
│   │   └── mouse_monitor.py      # Manual mouse override detection
│   ├── ui/
│   │   └── calibration_ui.py     # Fullscreen tkinter calibration window
│   └── utils/
│       ├── angle_buffer.py       # Rolling average buffer
│       └── config.py             # Config loader
├── config/
│   └── default_config.json       # All tunable parameters
├── data/
│   └── calibration.json          # Auto-generated calibration (gitignored)
├── logs/                         # CSV logs (gitignored)
├── tests/                        # Unit test suite
├── docs/                         # Feature docs, calibration guide
├── main.py                       # Entry point
└── requirements.txt
```

---

## Acknowledgements

Originally based on [Python-Gaze-Face-Tracker](https://github.com/alireza787b/Python-Gaze-Face-Tracker) by Alireza Bagheri, inspired by [Asadullah Dal's iris segmentation project](https://github.com/Asadullah-Dal17/iris-Segmentation-mediapipe-python).

---

## Note

Mac Eye Control is intended for personal use and experimentation. Gaze-based control requires a well-lit environment and a stable head position for best results. Recalibrate (`R`) whenever accuracy degrades or after significant lighting or position changes.
