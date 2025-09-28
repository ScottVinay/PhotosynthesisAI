import numpy as np
from pprint import pprint
import json
from psai.game.translations import encode_human_to_int_action, decode_vector_to_human_board
from psai.agents.base import BaseAgent
from sb3_contrib import MaskablePPO
from typing import Optional
import torch

class FrozenSB3(BaseAgent):
    """
    An agent that uses a pre-trained Stable Baselines 3 model to select actions.
    This is not trained and not passed to SB3's "learn" function.
    """

    def __init__(self, model_path: str) -> None:
        self.load_model(model_path)
        super().__init__()

    def load_model(self, model_path: str) -> None:
        self.model = MaskablePPO.load(model_path)

    def get_action(
            self,
            observation : np.ndarray,
            action_space_size : int,
            valid_actions_ohe: Optional[np.ndarray] = None
        ) -> int:
        """
        Gets an action index based on the current observation.
        """
        import torch

        obs_tensor = torch.as_tensor(observation).float()
        distribution = self.model.policy.get_distribution(obs_tensor)
        probs = distribution.distribution.probs.detach().cpu().numpy() # type: ignore #TODO Is probs right?

        if valid_actions_ohe is not None:
            masked_probs = probs * valid_actions_ohe
            if masked_probs.sum() == 0:
                masked_probs = valid_actions_ohe
            masked_probs = masked_probs / masked_probs.sum()
            action = np.random.choice(len(probs), p=masked_probs)
        else:
            action = np.random.choice(len(probs), p=probs)

        return int(action)