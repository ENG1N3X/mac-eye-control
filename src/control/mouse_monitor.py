import time

import pyautogui


class MouseMonitor:
    """Detects manual mouse/trackpad movement and temporarily suspends gaze control.

    No background threads — works entirely on the main loop. Each frame, compares
    the actual cursor position with the last position gaze control moved it to.
    If they differ by more than a threshold, the user moved the cursor manually.
    """

    def __init__(self, config: dict) -> None:
        self._timeout = config.get("manual_mouse_timeout_sec", 0.5)
        self._threshold_px = config.get("manual_mouse_threshold_px", 15)
        self._last_manual_time: float = 0.0
        self._last_known_pos: tuple[int, int] | None = None

    def check(self) -> bool:
        """Check for manual movement. Call each frame BEFORE gaze cursor move."""
        current = pyautogui.position()
        cx, cy = current.x, current.y

        if self._last_known_pos is not None:
            dx = cx - self._last_known_pos[0]
            dy = cy - self._last_known_pos[1]
            if (dx * dx + dy * dy) ** 0.5 > self._threshold_px:
                self._last_manual_time = time.monotonic()

        return (time.monotonic() - self._last_manual_time) < self._timeout

    def record_gaze_move(self, x: int, y: int) -> None:
        """Call after gaze moves cursor — records where we put it."""
        self._last_known_pos = (x, y)

    def sync_position(self) -> None:
        """Call when gaze is paused — sync reference to current cursor position
        so that cursor movement during pause is not counted against next check."""
        pos = pyautogui.position()
        self._last_known_pos = (pos.x, pos.y)

    def stop(self) -> None:
        pass  # no background thread to stop
