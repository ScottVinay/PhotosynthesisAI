print('import logging')
import logging; from pprint import pprint
print('from psai.game.env import PhotosynthesisEnv, MultiplayerEnvWrapper')
from psai.game.env import PhotosynthesisEnv, build_multiplayer_env
from psai.agents import RandomAgent
print('from stable_baselines3 import PPO')
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.monitor import Monitor
from typing import Optional, Dict, Union, Tuple, List, cast

import numpy as np
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logfolder = '/Users/scott/My Drive/Github/PhotosynthesisAI/logs/'

# 1. Create environment
logger.info("Creating PhotosynthesisEnv environment...")
multiplayer_env = build_multiplayer_env(
    PhotosynthesisEnv,
    agents=(
        None,
        RandomAgent(),
        RandomAgent(),
        RandomAgent()
    ),
    render_mode='matplotlib',
)
masked_env = ActionMasker(multiplayer_env, "get_action_mask") # The string is the method name in the env that returns the mask
monitored_env = Monitor(masked_env, filename = logfolder + "monitor.csv")

# 2. Initialize PPO agent
logger.info("Initializing PPO agent...")
model = MaskablePPO("MlpPolicy", monitored_env, verbose=1)

# 3. Train the agent
logger.info("Starting training for 30000 timesteps...")
model.learn(total_timesteps=30000)
logger.info("Training complete.")

from stable_baselines3.common.monitor import load_results
results = load_results(logfolder)   # 1 row per finished episode

episode_wins = (results['r']>0).astype(int).values
episode_rewards = (results['r']).astype(int).values

rolling_mean_wins = np.convolve(
    cast(np.ndarray, episode_wins),
    np.ones(10)/10, mode='valid'
)
rolling_mean_rewards = np.convolve(
    cast(np.ndarray, episode_rewards),
    np.ones(10)/10, mode='valid'
)

print('Rolling mean of wins:')
pprint(rolling_mean_wins)

print('Rolling mean of rewards:')
pprint(rolling_mean_rewards)

print('done')
