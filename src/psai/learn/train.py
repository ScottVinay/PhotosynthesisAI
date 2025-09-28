print('import logging')
import logging; from pprint import pprint
print('from psai.game.env import PhotosynthesisEnv, MultiplayerEnvWrapper')
from psai.game.env import PhotosynthesisEnv, build_multiplayer_env
from psai.agents import RandomAgent
print('from stable_baselines3 import PPO')
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
import numpy as np
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

#TODO Document: why env masker?
masked_env = ActionMasker(multiplayer_env, "get_action_mask") # The string is the method name in the env that returns the mask

# 2. Initialize PPO agent
logger.info("Initializing PPO agent...")
model = MaskablePPO("MlpPolicy", masked_env, verbose=1)

# 3. Train the agent
logger.info("Starting training for 10000 timesteps...")
model.learn(total_timesteps=10000)
logger.info("Training complete.")