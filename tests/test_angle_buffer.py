"""
Tests for src/utils/angle_buffer.py

Acceptance criteria covered:
- `from src.utils.angle_buffer import AngleBuffer` works (import succeeds)
- AngleBuffer from src.utils is the same class as AngleBuffer from legacy AngleBuffer module
- add() and get_average() work correctly with known values
"""

import os
import sys
import unittest

import numpy as np

# Ensure the project root is on sys.path so both src/ and AngleBuffer.py resolve
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestAngleBufferImport(unittest.TestCase):
    """src.utils.angle_buffer.AngleBuffer can be imported."""

    def test_import_succeeds(self):
        try:
            from src.utils.angle_buffer import AngleBuffer  # noqa: F401
        except ImportError as exc:
            self.fail(f"Import of src.utils.angle_buffer.AngleBuffer raised ImportError: {exc}")


class TestAngleBufferSameClass(unittest.TestCase):
    """src.utils.angle_buffer.AngleBuffer is the same class as AngleBuffer.AngleBuffer."""

    def test_same_class_identity(self):
        from src.utils.angle_buffer import AngleBuffer as SrcBuffer
        from AngleBuffer import AngleBuffer as LegacyBuffer

        self.assertIs(SrcBuffer, LegacyBuffer)


class TestAngleBufferInstantiation(unittest.TestCase):
    """AngleBuffer can be instantiated with and without arguments."""

    def test_default_instantiation(self):
        from src.utils.angle_buffer import AngleBuffer
        buf = AngleBuffer()
        self.assertIsNotNone(buf)

    def test_custom_size_instantiation(self):
        from src.utils.angle_buffer import AngleBuffer
        buf = AngleBuffer(size=5)
        self.assertIsNotNone(buf)


class TestAngleBufferAdd(unittest.TestCase):
    """add() stores values accessible via get_average()."""

    def test_add_single_value_and_average(self):
        from src.utils.angle_buffer import AngleBuffer
        buf = AngleBuffer(size=10)
        buf.add([1.0, 2.0, 3.0])
        avg = buf.get_average()
        np.testing.assert_array_almost_equal(avg, [1.0, 2.0, 3.0])

    def test_average_of_two_equal_entries(self):
        from src.utils.angle_buffer import AngleBuffer
        buf = AngleBuffer(size=10)
        buf.add([10.0, 20.0, 30.0])
        buf.add([10.0, 20.0, 30.0])
        avg = buf.get_average()
        np.testing.assert_array_almost_equal(avg, [10.0, 20.0, 30.0])

    def test_average_of_two_different_entries(self):
        from src.utils.angle_buffer import AngleBuffer
        buf = AngleBuffer(size=10)
        buf.add([0.0, 0.0, 0.0])
        buf.add([4.0, 8.0, 12.0])
        avg = buf.get_average()
        np.testing.assert_array_almost_equal(avg, [2.0, 4.0, 6.0])

    def test_average_of_known_pitch_values(self):
        from src.utils.angle_buffer import AngleBuffer
        buf = AngleBuffer(size=5)
        for pitch in [10.0, 20.0, 30.0]:
            buf.add([pitch, 0.0, 0.0])
        avg = buf.get_average()
        self.assertAlmostEqual(avg[0], 20.0)


class TestAngleBufferMaxSize(unittest.TestCase):
    """Buffer respects its maxlen — oldest entries are dropped."""

    def test_oldest_entry_dropped_when_full(self):
        from src.utils.angle_buffer import AngleBuffer
        buf = AngleBuffer(size=3)
        # Fill with three 0-valued entries
        for _ in range(3):
            buf.add([0.0])
        # Add a new entry; the oldest 0.0 is evicted, so avg should shift
        buf.add([9.0])
        avg = buf.get_average()
        # Buffer now holds [0.0, 0.0, 9.0] — average is 3.0
        self.assertAlmostEqual(avg[0], 3.0)

    def test_buffer_length_never_exceeds_size(self):
        from src.utils.angle_buffer import AngleBuffer
        buf = AngleBuffer(size=3)
        for i in range(10):
            buf.add([float(i)])
        self.assertLessEqual(len(buf.buffer), 3)


if __name__ == "__main__":
    unittest.main()
