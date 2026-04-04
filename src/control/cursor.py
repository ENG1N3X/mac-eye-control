import logging

import pyautogui

from src.utils.angle_buffer import AngleBuffer

logger = logging.getLogger(__name__)


class CursorController:
    def __init__(self, config: dict) -> None:
        smoothing_window = config["smoothing_window"]
        self._buffer = AngleBuffer(size=smoothing_window)
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

        self._buffer.add([clamped_x, clamped_y])
        smoothed = self._buffer.get_average()
        pos = (int(smoothed[0]), int(smoothed[1]))
        pyautogui.moveTo(*pos)
        return pos

    def reset_buffer(self) -> None:
        self._buffer.buffer.clear()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled
