import json
from dataclasses import dataclass
from typing import Optional
import importlib.resources as pkg_resources
from psai import control  # this points to the folder containing config.json

@dataclass
class ControlConfig:
    sun_stays_at_zero: bool
    reward_method: str

    def __post_init__(self):
        if self.reward_method not in ["score", "normed", "winner"]:
            raise ValueError(f"Invalid reward_method: {self.reward_method}")

# Singleton-ish instance cache
_config_instance: ControlConfig | None = None

def load_config(name: Optional[str]=None) -> ControlConfig:
    global _config_instance
    if _config_instance is None:
        if name is None:
            name = "default"
        config_path = pkg_resources.files(control).joinpath(f"configs/{name}.json")
        with config_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        _config_instance = ControlConfig(**raw)
    return _config_instance