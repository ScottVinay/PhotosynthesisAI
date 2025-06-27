import numpy as np
from psai.agents.base import BaseAgent

class RandomAgent(BaseAgent):
    """
    Agent that takes random actions.
    """
    
    def get_action(self, observation : np.ndarray, action_space_size : int) -> int:
        """
        """
        # Generate a random action index within the action space
        action_int = np.random.randint(0, action_space_size)
        return action_int