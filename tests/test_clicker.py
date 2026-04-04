"""
Tests for src/control/clicker.py — DoubleBlinkClicker

Phase 3 acceptance criteria covered (PRODUCT.md F3 — Double Blink Click):
- single blink does not trigger click
- two blinks within interval trigger one click
- two blinks outside interval do not trigger click
- detector emits a visual-trigger flag (update() returns True on click)
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class FakeClock:
    def __init__(self, start=100.0):
        self.now = start

    def set(self, value: float) -> None:
        self.now = value

    def __call__(self) -> float:
        return self.now


class TestDoubleBlinkClicker(unittest.TestCase):
    def _make_clicker(self, interval=0.5):
        from src.control.clicker import DoubleBlinkClicker

        clock = FakeClock()
        click_fn = MagicMock()
        cfg = {"blink_double_interval_sec": interval}
        clicker = DoubleBlinkClicker(cfg, time_fn=clock, click_fn=click_fn)
        return clicker, clock, click_fn

    def test_single_blink_does_not_click(self):
        clicker, clock, click_fn = self._make_clicker(interval=0.5)
        clock.set(10.0)
        fired = clicker.update(True)
        self.assertFalse(fired)
        click_fn.assert_not_called()

    def test_two_blinks_within_interval_clicks_once(self):
        clicker, clock, click_fn = self._make_clicker(interval=0.5)
        clock.set(10.0)
        self.assertFalse(clicker.update(True))
        clock.set(10.4)
        self.assertTrue(clicker.update(True))
        click_fn.assert_called_once()

    def test_two_blinks_outside_interval_do_not_click(self):
        clicker, clock, click_fn = self._make_clicker(interval=0.5)
        clock.set(10.0)
        self.assertFalse(clicker.update(True))
        clock.set(10.7)
        self.assertFalse(clicker.update(True))
        click_fn.assert_not_called()

    def test_non_blink_frame_never_triggers(self):
        clicker, _, click_fn = self._make_clicker(interval=0.5)
        self.assertFalse(clicker.update(False))
        click_fn.assert_not_called()

    def test_after_click_sequence_resets(self):
        clicker, clock, click_fn = self._make_clicker(interval=0.5)
        clock.set(20.0)
        self.assertFalse(clicker.update(True))
        clock.set(20.3)
        self.assertTrue(clicker.update(True))

        # New sequence starts after a successful double blink.
        clock.set(21.0)
        self.assertFalse(clicker.update(True))
        clock.set(21.2)
        self.assertTrue(clicker.update(True))
        self.assertEqual(click_fn.call_count, 2)


if __name__ == "__main__":
    unittest.main()
