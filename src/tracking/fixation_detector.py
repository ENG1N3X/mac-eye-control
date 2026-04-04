import collections
import numpy as np


class GazeFixationDetector:
    """Detects when the user is fixating on a point by measuring iris stability.

    Fixation is detected when the standard deviation of iris_dx and iris_dy
    over the last N frames is below a threshold.
    """

    def __init__(self, config: dict) -> None:
        self._std_threshold = config.get("fixation_std_threshold", 2.0)
        self._window = config.get("fixation_window_frames", 12)
        self._history_dx: collections.deque = collections.deque(maxlen=self._window)
        self._history_dy: collections.deque = collections.deque(maxlen=self._window)

    def update(self, iris_dx: float, iris_dy: float) -> None:
        self._history_dx.append(iris_dx)
        self._history_dy.append(iris_dy)

    def is_fixated(self) -> bool:
        if len(self._history_dx) < self._window:
            return False
        return (float(np.std(self._history_dx)) < self._std_threshold and
                float(np.std(self._history_dy)) < self._std_threshold)

    def progress(self) -> float:
        """Return 0.0–1.0: how close to fixation (1.0 = fixated)."""
        if len(self._history_dx) < 2:
            return 0.0
        std = max(float(np.std(self._history_dx)), float(np.std(self._history_dy)))
        return max(0.0, min(1.0, 1.0 - std / self._std_threshold))

    def reset(self) -> None:
        self._history_dx.clear()
        self._history_dy.clear()
