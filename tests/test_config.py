"""
Tests for src/utils/config.py

Acceptance criteria covered:
- load_config returns a dict with key "camera_index" when given the default config path
- load_config with a non-existent user_path still loads defaults without error
- save_config writes a file that can be read back with correct values
- load_config with a user override file merges correctly (user key wins)
"""

import json
import os
import sys
import tempfile
import unittest

# Ensure the project root is on sys.path so src/ imports resolve
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "default_config.json")


class TestLoadConfigReturnsDict(unittest.TestCase):
    """load_config with the default path returns a dict."""

    def test_returns_dict(self):
        from src.utils.config import load_config
        result = load_config(DEFAULT_CONFIG_PATH)
        self.assertIsInstance(result, dict)


class TestLoadConfigContainsCameraIndex(unittest.TestCase):
    """load_config result contains the 'camera_index' key."""

    def test_camera_index_key_present(self):
        from src.utils.config import load_config
        result = load_config(DEFAULT_CONFIG_PATH)
        self.assertIn("camera_index", result)


class TestLoadConfigNonExistentUserPath(unittest.TestCase):
    """load_config with a non-existent user_path still loads defaults."""

    def test_missing_user_path_does_not_raise(self):
        from src.utils.config import load_config
        result = load_config(DEFAULT_CONFIG_PATH, user_path="/tmp/does_not_exist_abc123.json")
        self.assertIn("camera_index", result)

    def test_missing_user_path_returns_default_camera_index(self):
        from src.utils.config import load_config
        result = load_config(DEFAULT_CONFIG_PATH, user_path="/tmp/does_not_exist_abc123.json")
        self.assertEqual(result["camera_index"], 0)


class TestSaveConfigRoundTrip(unittest.TestCase):
    """save_config writes a file that can be read back with correct values."""

    def test_saved_value_is_readable(self):
        from src.utils.config import load_config, save_config

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "subdir", "config.json")
            original = load_config(DEFAULT_CONFIG_PATH)
            original["camera_index"] = 99

            save_config(original, path)

            with open(path, "r") as f:
                saved = json.load(f)

            self.assertEqual(saved["camera_index"], 99)

    def test_saved_file_exists(self):
        from src.utils.config import load_config, save_config

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "config.json")
            original = load_config(DEFAULT_CONFIG_PATH)

            save_config(original, path)

            self.assertTrue(os.path.isfile(path))

    def test_save_creates_parent_directories(self):
        from src.utils.config import load_config, save_config

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "nested", "deep", "config.json")
            original = load_config(DEFAULT_CONFIG_PATH)

            save_config(original, path)

            self.assertTrue(os.path.isfile(path))


class TestLoadConfigUserOverrideWins(unittest.TestCase):
    """load_config merges user overrides; user keys take precedence."""

    def test_user_key_overrides_default(self):
        from src.utils.config import load_config

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_file:
            json.dump({"camera_index": 42}, tmp_file)
            tmp_path = tmp_file.name

        try:
            result = load_config(DEFAULT_CONFIG_PATH, user_path=tmp_path)
            self.assertEqual(result["camera_index"], 42)
        finally:
            os.unlink(tmp_path)

    def test_default_keys_not_in_user_file_are_preserved(self):
        from src.utils.config import load_config

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_file:
            json.dump({"camera_index": 1}, tmp_file)
            tmp_path = tmp_file.name

        try:
            result = load_config(DEFAULT_CONFIG_PATH, user_path=tmp_path)
            # blink_threshold comes from the default — it must survive the merge
            self.assertIn("blink_threshold", result)
        finally:
            os.unlink(tmp_path)

    def test_user_adds_new_key(self):
        from src.utils.config import load_config

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_file:
            json.dump({"my_custom_key": "hello"}, tmp_file)
            tmp_path = tmp_file.name

        try:
            result = load_config(DEFAULT_CONFIG_PATH, user_path=tmp_path)
            self.assertEqual(result["my_custom_key"], "hello")
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
