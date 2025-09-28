from random import random
import gymnasium as gym
import numpy as np
from typing import Iterable, Optional, cast
from dataclasses import dataclass
from psai.agents.base import BaseAgent
from psai.game.translations import decode_int_to_human_action, encode_human_to_vector_board, encode_human_to_int_action
from psai.game.assertions import assertion_loc
from psai.game.objects import Action, TSIZES, VALID_CELLS, State, Cell, PlayerStats
from psai.game.update import update_state
from psai.game.endgame import check_has_game_ended, calculate_reward
from psai.game.actions import get_allowed_actions
from psai.game.update import distribute_light
from psai.visuals.mpl_render import MplRenderer
from pprint import pprint
from copy import deepcopy


class PhotosynthesisEnv(gym.Env):
    def __init__(self, render_mode: Optional[str] = None):
        super().__init__()
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(469,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(1521+1)
        self.state_h: State

        self.episodes_states: list[list[State]] = []
        self.episodes_actions: list[list[tuple[int, Action]]] = []
        self.record_of_states: list[State] = []
        self.record_of_actions: list[tuple[int, Action]] = []
        
        if render_mode == 'matplotlib':
            self.renderer = MplRenderer()

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        initial_player_stats = {
            'light': 0,
            'score': 0,
            'seed_stash': 4,
            'seed_ready': 0,
            'small_stash': 4,
            'small_ready': 0,
            'medium_stash': 3,
            'medium_ready': 0,
            'large_stash': 2,
            'large_ready': 0
        }
        self.state_h = State(
            board_state=[Cell(loc=l, owner=None, size=None, used=False) for l in VALID_CELLS],
            sun_pos=0,
            hour=0,
            player_stats={i: PlayerStats(**initial_player_stats) for i in range(4)},
            active_player=0,
            day=0,
            n_score_cards_taken=0
        )

        #--------------------------------------------
        #--------------------------------------------
        #TODO For now, initial placements are "random". This should be another pre-round and new action type.
        #TODO Add random starting player
        used_initial_locs = set()
        for i in range(2):
            for p in range(4):
                random_ind = np.random.choice(len(VALID_CELLS))
                random_loc = VALID_CELLS[random_ind]
                while random_loc in used_initial_locs:
                    random_loc = np.random.choice(VALID_CELLS)
                used_initial_locs.add(random_loc)
                self.state_h.get_cell_at_loc(random_loc).owner = p
                self.state_h.get_cell_at_loc(random_loc).size = 'small'
                self.state_h.player_stats[p].small_stash -= 1
        state_v = encode_human_to_vector_board(self.state_h)
        info = {}
        distribute_light(self.state_h)
        #--------------------------------------------
        #--------------------------------------------

        self.record_of_states = [deepcopy(self.state_h)]
        self.record_of_actions = []
        return state_v, info

    def step(self, action: int):
        action_h = decode_int_to_human_action(action)

        # This is done before the update to capture the active player correctly
        self.record_of_actions.append((self.state_h.active_player, deepcopy(action_h)))

        update_state(self.state_h, action_h)
        self.state_v = encode_human_to_vector_board(self.state_h)
        
        done = False
        truncated = False
        reward = 0

        is_ended = check_has_game_ended(self.state_h)
        if is_ended:
            done = True
            reward_dict = calculate_reward(self.state_h)
            
            # Log the episodes
            self.episodes_states.append(self.record_of_states)
            self.episodes_actions.append(self.record_of_actions)

            reward = reward_dict[0] #This gets the reward for player 0, the learning agent.
            #TODO this might be changed if the learner can change seat?
        
        # action_mask = self.get_action_mask(self.state_h)
        # info = {"action_mask": action_mask}
        info = {}

        self.record_of_states.append(deepcopy(self.state_h))
        
        return self.state_v, reward, done, truncated, info
    
    def get_action_mask(self, self_object) -> np.ndarray:
        # Stable Baselines3's ActionMasker wrapper expects this method to take a single argument: the environment instance.
        # This means it takes two self arguments.
        allowed_actions = get_allowed_actions(self_object.state_h)
        action_mask = np.zeros(self_object.action_space.n, dtype=bool) # type: ignore
        for act in allowed_actions:
            act_int = encode_human_to_int_action(act)
            action_mask[act_int] = True
        return action_mask
    
    def render(self, mode="human"):
        print("Rendering not implemented.")

    def log_records(self):
        folder = "/Users/scott/My Drive/Github/PhotosynthesisAI/logs"
        with open(f"{folder}/states.txt", "w") as f:
            for istate, state in enumerate(self.record_of_states):
                f.write(f"--- State {istate} ---\n")
                f.write(state.__repr__() + "\n\n")
        with open(f"{folder}/actions.txt", "w") as f:
            for iact, (ip, action) in enumerate(self.record_of_actions):
                f.write(f"--- Action {iact} by player {ip} ---\n")
                f.write(action.__repr__() + "\n\n")


def build_multiplayer_env(
        env_name: type,
        agents: tuple[Optional[BaseAgent], BaseAgent, BaseAgent, BaseAgent],
        render_mode: Optional[str] = None,
    ) -> gym.Env:
    
    class MultiplayerEnvWrapper(env_name):
        """
        The step of PhotosynthesisEnv returns the next state. However,
        if we are training just one model, then the next observation is 
        found when we have looped through all players.
        """
        def __init__(
                self,
                agents: tuple[Optional[BaseAgent], BaseAgent, BaseAgent, BaseAgent],
                render_mode: Optional[str] = None,
        ):
            self.agents = agents
            self.num_players = len(agents)
            super().__init__(render_mode=render_mode)

        def active_player(self) -> int:
            return self.state_h.active_player

        def step(self, action : int):
            while True:
                action_human = decode_int_to_human_action(action)

                state, reward, done, truncated, info = super().step(action)

                if self.state_h.active_player == 0:
                    # Player 0, give values to main agent
                    return state, reward, done, truncated, info
                
                else:
                    # Get next agent's action and continue the loop
                    assert self.agents[self.state_h.active_player] is not None
                    agent = cast(BaseAgent, self.agents[self.state_h.active_player])
                    valid_actions_ohe = self.get_action_mask(self)
                    action = agent.get_action(
                        observation=state,
                        action_space_size=self.action_space.n, # type: ignore
                        valid_actions_ohe=valid_actions_ohe,
                    )
                    # Debug prints
                    # print(f'--- Opponent {self.state_h.active_player} turn ---')
                    # print(f"Player chose action ({action}) {decode_int_to_human_action(action)}")
                    # print('Valid actions:')
                    # for i, valid in enumerate(valid_actions_ohe):
                    #     if valid:
                    #         print(f"  {i}: {decode_int_to_human_action(i)}")

    multiplayer_env = MultiplayerEnvWrapper(
        agents=agents,
        render_mode=render_mode
    )
    return multiplayer_env