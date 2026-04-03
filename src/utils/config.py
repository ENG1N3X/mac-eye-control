import json
import os


def load_config(default_path: str, user_path: str = None) -> dict:
    with open(default_path, "r") as f:
        config = json.load(f)
    if user_path and os.path.exists(user_path):
        with open(user_path, "r") as f:
            overrides = json.load(f)
        config.update(overrides)
    return config


def save_config(config: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
