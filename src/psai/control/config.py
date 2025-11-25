import json
from dataclasses import dataclass
from typing import Optional
import importlib.resources as pkg_resources
from psai import control  # this points to the folder containing config.json

@dataclass
class GameConfig:
    """
    Configuration settings for game mechanics.
    
    Attributes
    ----------
    sun_stays_at_zero : bool
        If True, the board rotates to keep the sun at position 0.
    reward_method : str
        The method used to calculate rewards. Valid options are:
        "score", "normed", "winner", "winning_score".
    """
    sun_stays_at_zero: bool
    reward_method: str

    def __post_init__(self):
        if self.reward_method not in ["score", "normed", "winner", "winning_score"]:
            raise ValueError(f"Invalid reward_method: {self.reward_method}")

@dataclass
class TrainingConfig:
    """
    Configuration settings for training parameters.
    
    Attributes
    ----------
    num_rounds : int
        The number of training rounds to execute.
    timesteps_per_round : int
        The number of timesteps to train in each round.
    """
    num_rounds: int
    timesteps_per_round: int

    def __post_init__(self):
        pass

# Singleton-ish instance cache
_game_config_instance: GameConfig | None = None
_training_config_instance: TrainingConfig | None = None

def load_game_config(name: Optional[str]=None) -> GameConfig:
    """
    Load the game configuration from a JSON file.
    
    Uses a singleton pattern to cache the configuration after first load.
    
    Parameters
    ----------
    name : Optional[str], default=None
        The name of the configuration file (without .json extension).
        If None, loads "default".
    
    Returns
    -------
    GameConfig
        The loaded game configuration object.
    """
    global _game_config_instance
    if _game_config_instance is None:
        if name is None:
            name = "default"
        config_path = pkg_resources.files(control).joinpath(f"game_configs/{name}.json")
        with config_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        _game_config_instance = GameConfig(**raw)
    return _game_config_instance

def load_training_config(name: Optional[str]=None) -> TrainingConfig:
    """
    Load the training configuration from a JSON file.
    
    Uses a singleton pattern to cache the configuration after first load.
    
    Parameters
    ----------
    name : Optional[str], default=None
        The name of the configuration file (without .json extension).
        If None, loads "default".
    
    Returns
    -------
    TrainingConfig
        The loaded training configuration object.
    """
    global _training_config_instance
    if _training_config_instance is None:
        if name is None:
            name = "default"
        config_path = pkg_resources.files(control).joinpath(f"training_configs/{name}.json")
        with config_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        _training_config_instance = TrainingConfig(**raw)
    return _training_config_instance