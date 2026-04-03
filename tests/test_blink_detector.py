"""
Tests for src/tracking/blink_detector.py

Acceptance criteria covered:
- BlinkDetector instantiates with a config dict
- update() returns False for a single frame below threshold (not enough consecutive frames)
- update() returns True after enough consecutive frames below threshold, then a frame above
- total_blinks increments correctly

Strategy:
- We mock _blinking_ratio to inject controlled EAR values, keeping tests deterministic
  and independent of numpy geometry math.
- The EAR formula in the code is: (right_ratio + left_ratio + 1) / 2
  For a "closed" eye EAR we need <= 0.51 (threshold from default config).
  For an "open" eye EAR we need > 0.51.
- blink_consec_frames=2 means the counter must be STRICTLY GREATER THAN 2,
  i.e. we need at least 3 consecutive below-threshold frames, then one above.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Minimal config matching default_config.json relevant keys
MINIMAL_CONFIG = {
    "blink_threshold": 0.51,
    "blink_consec_frames": 2,
    "smoothing_window": 10,
    "user_face_width_mm": 140,
    "min_detection_confidence": 0.8,
    "min_tracking_confidence": 0.8,
    "head_pose_display_threshold": 10,
}

# Dummy mesh that satisfies the shape but we will mock _blinking_ratio anyway
DUMMY_MESH = np.zeros((478, 3), dtype=np.float32)


class TestBlinkDetectorInstantiation(unittest.TestCase):
    def test_instantiates_without_error(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)
        self.assertIsNotNone(detector)

    def test_initial_total_blinks_is_zero(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)
        self.assertEqual(detector.total_blinks, 0)


class TestBlinkDetectorSingleFrameNoClick(unittest.TestCase):
    """One frame below threshold must NOT register a blink."""

    def test_single_below_threshold_frame_returns_false(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        # EAR = 0.30 → below threshold 0.51 → eyes "closed"
        with patch.object(detector, "_blinking_ratio", return_value=0.30):
            result = detector.update(DUMMY_MESH)

        self.assertFalse(result)

    def test_single_below_threshold_frame_does_not_increment_total(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        with patch.object(detector, "_blinking_ratio", return_value=0.30):
            detector.update(DUMMY_MESH)

        self.assertEqual(detector.total_blinks, 0)


class TestBlinkDetectorTwoFramesNoClick(unittest.TestCase):
    """
    Two consecutive below-threshold frames then one above: NOT a blink.
    blink_consec_frames=2 → counter must exceed 2 (strict >) to register.
    Two frames → counter reaches 2, which is NOT > 2.
    """

    def test_two_below_then_one_above_returns_false(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        # Two closed frames
        with patch.object(detector, "_blinking_ratio", return_value=0.30):
            detector.update(DUMMY_MESH)
            detector.update(DUMMY_MESH)

        # One open frame — should NOT fire blink (counter==2, threshold needs >2)
        with patch.object(detector, "_blinking_ratio", return_value=0.80):
            result = detector.update(DUMMY_MESH)

        self.assertFalse(result)

    def test_two_below_then_one_above_total_stays_zero(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        with patch.object(detector, "_blinking_ratio", return_value=0.30):
            detector.update(DUMMY_MESH)
            detector.update(DUMMY_MESH)

        with patch.object(detector, "_blinking_ratio", return_value=0.80):
            detector.update(DUMMY_MESH)

        self.assertEqual(detector.total_blinks, 0)


class TestBlinkDetectorThreeFramesRegistersClick(unittest.TestCase):
    """
    Three consecutive below-threshold frames then one above: blink IS registered.
    counter reaches 3, which is > 2 → blink fires.
    """

    def test_three_below_then_one_above_returns_true(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        with patch.object(detector, "_blinking_ratio", return_value=0.30):
            detector.update(DUMMY_MESH)
            detector.update(DUMMY_MESH)
            detector.update(DUMMY_MESH)

        with patch.object(detector, "_blinking_ratio", return_value=0.80):
            result = detector.update(DUMMY_MESH)

        self.assertTrue(result)

    def test_three_below_then_one_above_increments_total(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        with patch.object(detector, "_blinking_ratio", return_value=0.30):
            detector.update(DUMMY_MESH)
            detector.update(DUMMY_MESH)
            detector.update(DUMMY_MESH)

        with patch.object(detector, "_blinking_ratio", return_value=0.80):
            detector.update(DUMMY_MESH)

        self.assertEqual(detector.total_blinks, 1)


class TestBlinkDetectorFrameCounterResets(unittest.TestCase):
    """After registering a blink, the frame counter resets to zero."""

    def test_counter_resets_after_blink(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        with patch.object(detector, "_blinking_ratio", return_value=0.30):
            for _ in range(3):
                detector.update(DUMMY_MESH)

        with patch.object(detector, "_blinking_ratio", return_value=0.80):
            detector.update(DUMMY_MESH)

        # After reset, a single closed frame should NOT immediately fire another blink
        with patch.object(detector, "_blinking_ratio", return_value=0.30):
            detector.update(DUMMY_MESH)

        with patch.object(detector, "_blinking_ratio", return_value=0.80):
            result = detector.update(DUMMY_MESH)

        # Only 1 closed frame since reset → should not fire
        self.assertFalse(result)


class TestBlinkDetectorTotalBlinksAccumulates(unittest.TestCase):
    """total_blinks increments on each distinct blink event."""

    def _trigger_blink(self, detector):
        with patch.object(detector, "_blinking_ratio", return_value=0.30):
            for _ in range(3):
                detector.update(DUMMY_MESH)
        with patch.object(detector, "_blinking_ratio", return_value=0.80):
            detector.update(DUMMY_MESH)

    def test_two_blinks_total_is_two(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        self._trigger_blink(detector)
        self._trigger_blink(detector)

        self.assertEqual(detector.total_blinks, 2)

    def test_three_blinks_total_is_three(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        self._trigger_blink(detector)
        self._trigger_blink(detector)
        self._trigger_blink(detector)

        self.assertEqual(detector.total_blinks, 3)


class TestBlinkDetectorAboveThresholdFramesNeverFire(unittest.TestCase):
    """Open-eye frames must never return True."""

    def test_open_eye_frames_return_false(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        with patch.object(detector, "_blinking_ratio", return_value=0.80):
            for _ in range(10):
                result = detector.update(DUMMY_MESH)
                self.assertFalse(result)


class TestBlinkDetectorExactlyAtThreshold(unittest.TestCase):
    """EAR exactly at threshold (0.51) is treated as closed (<=)."""

    def test_ear_at_threshold_does_not_immediately_fire(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        with patch.object(detector, "_blinking_ratio", return_value=0.51):
            result = detector.update(DUMMY_MESH)

        # Just one frame at threshold — still not enough frames
        self.assertFalse(result)

    def test_ear_just_above_threshold_treated_as_open(self):
        from src.tracking.blink_detector import BlinkDetector
        detector = BlinkDetector(MINIMAL_CONFIG)

        with patch.object(detector, "_blinking_ratio", return_value=0.52):
            result = detector.update(DUMMY_MESH)

        self.assertFalse(result)
        self.assertEqual(detector.total_blinks, 0)


if __name__ == "__main__":
    unittest.main()
