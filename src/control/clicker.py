import time
from typing import Callable, Optional

import pyautogui


class DoubleBlinkClicker:
    def __init__(
        self,
        config: dict,
        time_fn: Optional[Callable[[], float]] = None,
        click_fn: Optional[Callable[[], None]] = None,
    ) -> None:
        self._interval_sec = float(config["blink_double_interval_sec"])
        self._time_fn = time_fn or time.monotonic
        self._click_fn = click_fn or pyautogui.click
        self._last_blink_ts: Optional[float] = None

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

    def update(self, blink_detected: bool) -> bool:
        if not blink_detected:
            return False

        now = self._time_fn()
        if self._last_blink_ts is not None:
            dt = now - self._last_blink_ts
            if dt <= self._interval_sec:
                self._click_fn()
                self._last_blink_ts = None
                return True

        self._last_blink_ts = now
        return False
