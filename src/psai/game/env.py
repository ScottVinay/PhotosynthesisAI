import gymnasium as gym
import numpy as np
from typing import Iterable, Optional
from psai.agents.base import BaseAgent
from psai.game.translations import decode_int_to_human_action
from dataclasses import dataclass
from psai.game.assertions import assertion_ring_cell 


@dataclass
class Cell:
    loc: tuple[int, int]
    owner: int
    size: str
    used: bool

@dataclass
class State:
    """
    Parameters
    ----------
    board_state : dict
        A dictionary representing the game board state, where keys are ring identifiers.
        The values are lists of tuples of (owner, tree_size, used) for each cell in the ring.

        - owner: str, the player who owns the cell (e.g., "p1", "p2", "empty").
        - tree_size: str, the size of the tree in the cell (e.g., "seed", "small", "medium", "large", "empty").
        - used: bool, indicates whether the cell has been used this turn.

        Example:
        {
            0: [("p1", "seed", True), ("p2", "small", False), ("p1", "medium", False), ...,]
            1: [("p4", "small", False), ("p2", "seed", True), ("empty", "empty", False), ...,]
            ...,
        }

    sun_pos : int < 6
        The position of the sun in the game, typically an integer representing the current sun's position.

    player_stats : dict
        A dictionary containing player statistics.
        Keys are "p1", "p2", "p3", "p4" and values are dictionaries with keys:
        - "light": int, the amount of light the player has
        - "score": int, the player's score
        - "seed_stash": int, the number of seed the player has in their stash.
        - "seed_ready": int, the number of seed the player has ready to plant.
        - "small_stash": int
        - "small_ready": int
        - "medium_stash": int
        - "medium_ready": int
        - "large_stash": int
        - "large_ready": int

        The price of the next tree will depend on the value of stash.

    active_player : int < 4
        The index of the active player (0, 1, 2, or 3).
    """
    board_state: dict[int, list[tuple[str, str, bool]]]
    sun_pos: int
    player_stats: dict[str, dict[str, int]]
    active_player: int
    turn: int

    def __post_init__(self):
        self.verify_board_state(self.board_state)
        self.verify_sun_pos(self.sun_pos)
        self.verify_player_stats(self.player_stats)
        self.verify_active_player(self.active_player)
        self.verify_turn(self.turn)

    def verify_board_state(self, board_state: dict[int, list[tuple[str, str, bool]]]):
        for k, v in board_state.items():
            if not k >= 0 and k < 4:
                raise ValueError(f"Invalid ring identifier: {k}")
            for cell in v:
                if len(cell) != 3:
                    raise ValueError(f"Invalid cell format: {cell}")
                owner, tree_size, used = cell
                if owner not in ["p1", "p2", "p3", "p4", "empty"]:
                    raise ValueError(f"Invalid owner: {owner}")
                if tree_size not in ["seed", "small", "medium", "large", "empty"]:
                    raise ValueError(f"Invalid tree size: {tree_size}")
                if not isinstance(used, bool):
                    raise ValueError(f"Used must be a boolean, got {used}")
                
    def verify_sun_pos(self, sun_pos: int):
        if not (0 <= sun_pos < 6):
            raise ValueError(f"Invalid sun position: {sun_pos}. Must be in range [0, 5].")
        
    def verify_player_stats(self, player_stats: dict[str, dict[str, int]]):
        maximum_in_stash = {
            'seed': 4,
            'small': 4,
            'medium': 3,
            'large': 2,
        }
        valid_players = ["p1", "p2", "p3", "p4"]
        for player in valid_players:
            if player not in player_stats:
                raise ValueError(f"Missing stats for player: {player}")
            stats = player_stats[player]
            if not isinstance(stats, dict):
                raise ValueError(f"Stats for {player} must be a dictionary.")
            required_keys = [
                "light", "score", "seed_stash", "seed_ready",
                "small_stash", "small_ready", "medium_stash", "medium_ready",
                "large_stash", "large_ready"
            ]
            for key in required_keys:
                if key not in stats or not isinstance(stats[key], int):
                    raise ValueError(f"Invalid or missing stat '{key}' for player {player}.")
                assert stats[key] >= 0
            
            for size in maximum_in_stash.keys():
                assert stats[size + '_stash'] <= maximum_in_stash[size]

    def verify_active_player(self, active_player: int):
        if not (0 <= active_player < 4):
            raise ValueError(f"Invalid active player index: {active_player}. Must be in range [0, 3].")
        
    def verify_turn(self, turn: int):
        assert turn >= 0 and turn < 5

class MultiplayerEnvWrapper:
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

    def step(self, action):
        while True:
            action_human = decode_int_to_human_action(action)
            if action_human[0] == 'end_turn':
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
        # Note: planting a seed from a tree "uses" both the tree cell and the seed cell.
        reward = 0
        done = False
        truncated = False
        info = {}

        return self.state, reward, done, truncated, info

    def render(self, mode="human"):
        print("Rendering not implemented.")
