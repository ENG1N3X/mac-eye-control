import logging

import pyautogui

logger = logging.getLogger(__name__)


class CursorController:
    def __init__(self, config: dict) -> None:
        # EMA: smaller alpha = smoother but more lag; larger = more responsive but jittery
        self._alpha = config.get("smoothing_alpha", 0.1)
        # Deadzone: skip move if delta is below this many pixels (suppresses micro-tremor)
        self._deadzone = config.get("cursor_deadzone_px", 4)
        self._ema_x: float | None = None
        self._ema_y: float | None = None
        self._last_pos: tuple[int, int] | None = None
        self._enabled = True
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

    def move(self, screen_x: float, screen_y: float) -> tuple[int, int] | None:
        """Move cursor to predicted position. Returns the final (x, y) moved to, or None."""
        if not self._enabled:
            return None

        screen_w, screen_h = pyautogui.size()
        clamped_x = max(0, min(screen_x, screen_w - 1))
        clamped_y = max(0, min(screen_y, screen_h - 1))

        # Exponential moving average
        if self._ema_x is None:
            self._ema_x, self._ema_y = clamped_x, clamped_y
        else:
            self._ema_x = self._alpha * clamped_x + (1.0 - self._alpha) * self._ema_x
            self._ema_y = self._alpha * clamped_y + (1.0 - self._alpha) * self._ema_y

        new_x, new_y = int(self._ema_x), int(self._ema_y)

        # Deadzone: don't move if change is smaller than threshold
        if self._last_pos is not None:
            dx = abs(new_x - self._last_pos[0])
            dy = abs(new_y - self._last_pos[1])
            if dx < self._deadzone and dy < self._deadzone:
                return self._last_pos

        pyautogui.moveTo(new_x, new_y)
        self._last_pos = (new_x, new_y)
        return self._last_pos

    def reset_buffer(self) -> None:
        self._ema_x = None
        self._ema_y = None
        self._last_pos = None

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled
