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
        # Ensure batch dimension and correct device/dtype
        # obs_to_tensor handles np -> torch and adds batch dim
        with torch.no_grad():
            obs_tensor, _ = self.model.policy.obs_to_tensor(observation)  # shape [1, obs_dim], on correct device

            # Prepare mask for MaskablePPO: bool tensor shape [batch, n_actions]
            action_masks = None
            if valid_actions_ohe is not None:
                mask = torch.as_tensor(valid_actions_ohe.astype(bool))
                if mask.ndim == 1:
                    mask = mask.unsqueeze(0)  # -> [1, n_actions]
                action_masks = mask
            else:
                action_masks = torch.ones((1, action_space_size), dtype=torch.bool)

            # Get masked categorical distribution
            dist = self.model.policy.get_distribution(obs_tensor, action_masks=action_masks) # type: ignore

            # Probabilities for the single batch item
            probs = dist.distribution.probs.squeeze(0).cpu().numpy()  # type: ignore

            # Sample according to probs (already masked & renormalized if mask was given)
            # action = np.random.choice(len(probs), p=probs)
            action = np.argmax(probs)  # Greedy action selection

        return int(action)