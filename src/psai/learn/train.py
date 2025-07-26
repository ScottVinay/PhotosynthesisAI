from psai.game.env import PhotosynthesisEnv, MultiplayerEnvWrapper
from stable_baselines3 import PPO

# 1. Create environment
env = PhotosynthesisEnv(render_mode='matplotlib')

# 2. Initialize PPO agent
model = PPO("MlpPolicy", env, verbose=1)

# 3. Train the agent
model.learn(total_timesteps=10000)