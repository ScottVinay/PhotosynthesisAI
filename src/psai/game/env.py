import gymnasium as gym
import numpy as np

class PhotosynthesisEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(10,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(5)
        self.state = np.zeros(10)

    def reset(self, *, seed=None, options=None):
        self.state = np.zeros(10)
        return self.state, {}

    def step(self, action):
        # Apply action logic here
        reward = 0
        done = False
        truncated = False
        info = {}
        return self.state, reward, done, truncated, info

    def calculate_cost(self, action) -> int:
        """
        Gets the cost of an action in light points. Note, the cost of buying a tree
        depends on the number already bought.   

        Parameters
        ----------
        action
        """
        ...

    def render(self, mode="human"):
        print("Rendering not implemented.")
