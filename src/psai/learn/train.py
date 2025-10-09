import logging
from pprint import pprint
from psai.game.env import PhotosynthesisEnv, build_multiplayer_env
from psai.agents import RandomAgent, FrozenSB3, BaseAgent
from psai.control.config import load_training_config
from psai.game.utils import find_git_root
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.monitor import Monitor
from typing import Optional, cast

import numpy as np
import os
from datetime import datetime
import importlib.resources as pkg_resources


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = load_training_config()

# 0. Set folders
base_logs_folder = find_git_root() / 'logs/'
base_models_folder = find_git_root() / 'model_files/'

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logs_folder = os.path.join(base_logs_folder, f"run_{current_time}/")
models_folder = os.path.join(base_models_folder, f"run_{current_time}/")

os.makedirs(logs_folder, exist_ok=True)
os.makedirs(models_folder, exist_ok=True)


def play_round(
        initial_model_path: Optional[str] = None,
        training_idx: int = 0,
        logs_folder: str = '',
        timesteps: int = 1000,
    ) -> None:
    logs_subfolder = os.path.join(logs_folder, f"round_{training_idx}/")

    # 1. Create environment
    logger.info("Creating PhotosynthesisEnv environment...")

    if initial_model_path is None:
        agents = (
            None,
            RandomAgent(),
            RandomAgent(),
            RandomAgent()
        )
    else:
        agents = (
            None,
            FrozenSB3(initial_model_path),
            FrozenSB3(initial_model_path),
            FrozenSB3(initial_model_path)
        )

    multiplayer_env = build_multiplayer_env(
        PhotosynthesisEnv,
        agents=agents,
        render_mode='matplotlib',

    )
    # The string is the method name in the env that returns the mask
    masked_env = ActionMasker(multiplayer_env, "get_action_mask")

    monitored_env = Monitor(masked_env, filename = logs_subfolder + "monitor.csv")

    # 2. Initialize PPO agent
    logger.info("Initializing PPO agent...")
    model = MaskablePPO("MlpPolicy", monitored_env, verbose=1)
    if initial_model_path is not None:
        model = MaskablePPO.load(initial_model_path, env=monitored_env)

    # 3. Train the agent
    logger.info("Starting training...")
    model.learn(total_timesteps=timesteps)
    logger.info("Training complete.")

    # 4. Save the trained model
    model.save(models_folder + "trained_model_" + str(training_idx) + ".zip")


def play_many_rounds(num_rounds: int = 10, timesteps: int = 1000) -> None:
    for i in range(num_rounds):
        logger.info(f"Starting round {i+1} of {num_rounds}...")
        play_round(
            initial_model_path=None if i == 0 else models_folder + "trained_model_" + str(i-1) + ".zip",
            training_idx=i,
            logs_folder=logs_folder,
            timesteps=timesteps,
        )
        logger.info(f"Round {i+1} complete.")


if __name__ == "__main__":
    play_many_rounds(
        num_rounds=config.num_rounds,
        timesteps=config.timesteps_per_round,
    )
    print('done')
