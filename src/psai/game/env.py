import gymnasium as gym
import numpy as np
from typing import Iterable, Optional
from psai.agents.base import BaseAgent
from psai.game.translations import decode_int_to_human_action
from dataclasses import dataclass
from psai.game.assertions import assertion_loc
from psai.game.objects import Action, TSIZES, State, Cell, PlayerStats
import psai.visuals.mpl_render as mpl_render

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
        self.action_space = gym.spaces.Discrete(5)
        self.state = np.zeros(10)
        if render_mode == 'matplotlib':
            self.renderer = mpl_render.MplRenderer()

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
