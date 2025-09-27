import numpy as np
from typing import Optional

class BaseAgent:
    """
    Base class for all agents.
    Note, if using an SB3 agent, we should inherit
    from both this class and the SB3 agent class.
    """

    def transform_state_vector(self, observation: np.ndarray) -> np.ndarray:
        """
        Transforms the observation vector into a format suitable for the agent.
        This method should be overridden by subclasses if specific transformations are needed.
        """
        return observation

    def get_action(
            self,
            observation : np.ndarray,
            action_space_size : int,
            valid_actions_ohe: Optional[np.ndarray] = None
        ) -> int:
        """
        Gets an action index based on the current observation.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")