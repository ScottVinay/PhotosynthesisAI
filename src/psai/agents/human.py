import numpy as np
from typing import Optional
from pprint import pprint
import json
from psai.game.translations import encode_human_to_int_action, decode_vector_to_human_board
from psai.agents.base import BaseAgent

class HumanAgent(BaseAgent):
    """
    Agent for human input.
    This agent allows a human player to input their actions in a human-readable format.
    It prompts the user to enter their action as a JSON string, which is then converted
    into an integer action index that the environment can understand.
    """

    def get_action(
            self,
            observation : np.ndarray,
            action_space_size : int,
            valid_actions_ohe: Optional[np.ndarray] = None
        ) -> int:
        """
        Gets an action index based on the current observation.
        """
        pprint(decode_vector_to_human_board(observation))
        while True:
            action_dict_str = input("Enter your action number:\n")
            action_dict = json.loads(action_dict_str)
            #TODO dict to Action
            action_int = encode_human_to_int_action(action_dict)
            if valid_actions_ohe is not None and valid_actions_ohe[action_int] == 0:
                print("Invalid action, please try again.")
                continue
            break
        return action_int