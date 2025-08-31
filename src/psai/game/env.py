import gymnasium as gym
import numpy as np
from typing import Iterable, Optional
from dataclasses import dataclass
from psai.agents.base import BaseAgent
from psai.game.translations import decode_int_to_human_action, encode_human_to_vector_board
from psai.game.assertions import assertion_loc
from psai.game.objects import Action, TSIZES, VALID_CELLS, State, Cell, PlayerStats
from psai.game.update import update_state
from psai.game.endgame import check_has_game_ended, calculate_reward
from psai.visuals.mpl_render import MplRenderer

class MultiplayerEnvWrapper(gym.Env):
    """
    The step of PhotosynthesisEnv returns the next state. However,
    if we are training just one model, then the next observation is 
    found when we have looped through all players.
    """
    def __init__(self, env: gym.Env, *agents: BaseAgent):
        self.env = env
        self.agents = agents
        self.num_players = len(agents)
        self.current_player = 0
        #TODO I think that agents[0] should be None if it is trained with SB3.

    def reset(self, *, seed=None, options=None):
        self.current_player = 0
        return self.env.reset(seed=seed, options=options)

    def step(self, action : int):
        while True:
            action_human = decode_int_to_human_action(action)
            if action_human.action_type == 'end_turn':
                self.current_player = (self.current_player + 1) % self.num_players

            state, reward, done, truncated, info = self.env.step(action)

            if self.current_player == 0:
                # End of round, return to main agent
                return state, reward, done, truncated, info
            else:
                # Get next agent's action and continue the loop
                action = self.agents[self.current_player].get_action(
                    state,
                    self.env.action_space.n # type: ignore
                )


class PhotosynthesisEnv(gym.Env):
    # TODO
    def __init__(self, render_mode: Optional[str] = None):
        super().__init__()
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(469,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(1521+1)
        self.state_h: State
        
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
        #TODO For now, initial placements are random. This should be another pre-round and new action type.
        for i in range(2):
            for p in range(4):
                self.state_h.get_cell_at_loc((i, p)).owner = p
                self.state_h.get_cell_at_loc((i, p)).size = 'small'
        state_v = encode_human_to_vector_board(self.state_h)
        info = {}
        return state_v, info

    def step(self, action: int):
        action_h = decode_int_to_human_action(action)
        update_state(self.state_h, action_h)
        self.state_v = encode_human_to_vector_board(self.state_h)
        
        done = False
        truncated = False
        reward = 0

        is_ended = check_has_game_ended(self.state_h)
        if is_ended:
            done = True
            reward_dict = calculate_reward(self.state_h)

            reward = reward_dict[self.state_h.active_player] #TODO not right(?) just to get working
        
        info = {}

        return self.state_v, reward, done, truncated, info

    def render(self, mode="human"):
        print("Rendering not implemented.")
