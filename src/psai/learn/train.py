print('import logging')
import logging
print('from psai.game.env import PhotosynthesisEnv, MultiplayerEnvWrapper')
from psai.game.env import PhotosynthesisEnv, MultiplayerEnvWrapper
print('from stable_baselines3 import PPO')
from stable_baselines3 import PPO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Create environment
logger.info("Creating PhotosynthesisEnv environment...")
env = PhotosynthesisEnv(render_mode='matplotlib')

# 2. Initialize PPO agent
logger.info("Initializing PPO agent...")
model = PPO("MlpPolicy", env, verbose=1)

# 3. Train the agent
logger.info("Starting training for 10000 timesteps...")
model.learn(total_timesteps=10000)
logger.info("Training complete.")