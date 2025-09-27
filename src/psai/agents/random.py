import numpy as np
from typing import Optional
from psai.agents.base import BaseAgent

class RandomAgent(BaseAgent):
    """
    Agent that takes random actions.
    """
    
    def get_action(
            self,
            observation : np.ndarray,
            action_space_size : int,
            valid_actions_ohe: Optional[np.ndarray] = None
        ) -> int:
        """
        """
        # Generate a random action index within the action space
        if valid_actions_ohe is not None:
            valid_indices = np.where(valid_actions_ohe == 1)[0]
            action_int = np.random.choice(valid_indices)
        else:
            action_int = np.random.randint(0, action_space_size)
        return action_int