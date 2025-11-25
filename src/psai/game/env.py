import random
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
from psai.game.utils import find_git_root
from psai.visuals.mpl_render import MplRenderer
from pprint import pprint
from copy import deepcopy


class PhotosynthesisEnv(gym.Env):
    """
    A Gymnasium environment for the Photosynthesis board game.
    
    This environment simulates the Photosynthesis game where players manage trees
    on a hexagonal board, collecting light and scoring points.
    
    Attributes
    ----------
    observation_space : gym.spaces.Box
        The observation space with shape (469,) representing the game state.
    action_space : gym.spaces.Discrete
        The action space with 1522 possible actions.
    state_h : State
        The current human-readable game state.
    episodes_states : list[list[State]]
        Record of all states from completed episodes.
    episodes_actions : list[list[tuple[int, Action]]]
        Record of all actions from completed episodes.
    record_of_states : list[State]
        States from the current episode.
    record_of_actions : list[tuple[int, Action]]
        Actions from the current episode.
    renderer : MplRenderer, optional
        Renderer for visualizing the game state.
    
    Parameters
    ----------
    render_mode : Optional[str], default=None
        The rendering mode. If 'matplotlib', uses matplotlib renderer.
    """
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
        """
        Reset the environment to its initial state.
        
        Parameters
        ----------
        seed : int, optional
            Random seed for reproducibility.
        options : dict, optional
            Additional options for reset.
        
        Returns
        -------
        tuple[np.ndarray, dict]
            The initial observation vector and an info dictionary.
        """
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
                while True:
                    random_theta = np.random.choice(18)
                    random_loc = (0, random_theta)
                    if random_loc not in used_initial_locs:
                        break
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
        """
        Execute one step in the environment.
        
        Parameters
        ----------
        action : int
            The integer-encoded action to take.
        
        Returns
        -------
        tuple[np.ndarray, float, bool, bool, dict]
            A tuple containing:
            - observation: The new state vector
            - reward: The reward for this step
            - done: Whether the episode is finished
            - truncated: Whether the episode was truncated
            - info: Additional information dictionary
        """
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
        """
        Get a mask of valid actions for the current state.
        
        Note: Stable Baselines3's ActionMasker wrapper expects this method
        to take a single argument (the environment instance), which means
        it takes two self arguments.
        
        Parameters
        ----------
        self_object : PhotosynthesisEnv
            The environment instance.
        
        Returns
        -------
        np.ndarray
            A boolean array where True indicates valid actions.
        """
        # Stable Baselines3's ActionMasker wrapper expects this method to take a single argument: the environment instance.
        # This means it takes two self arguments.
        allowed_actions = get_allowed_actions(self_object.state_h)
        action_mask = np.zeros(self_object.action_space.n, dtype=bool) # type: ignore
        for act in allowed_actions:
            act_int = encode_human_to_int_action(act)
            action_mask[act_int] = True
        return action_mask
    
    def render(self, mode="human"):
        """
        Render the environment.
        
        Parameters
        ----------
        mode : str, default="human"
            The rendering mode.
        
        Returns
        -------
        None
        """
        print("Rendering not implemented.")

    def log_records(self):
        """
        Log the recorded states and actions to text files.
        
        Writes the episode's state and action history to files in the logs directory.
        
        Returns
        -------
        None
        """
        folder = find_git_root() / "logs/"
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
    ) -> type:
    """
    Build a multiplayer environment wrapper.
    
    Creates a wrapper class that allows multiple agents to play against each other,
    with only one agent being trained while others use pre-defined strategies.
    
    Parameters
    ----------
    env_name : type
        The base environment class to wrap (typically PhotosynthesisEnv).
    
    Returns
    -------
    type
        A wrapped environment class that supports multiplayer gameplay.
    """
    
    class MultiplayerEnvWrapper(env_name):
        """
        The step of PhotosynthesisEnv returns the next state. However,
        if we are training just one model, then the next observation is 
        found when we have looped through all players.
        """
        #TODO Score depends on cell of harversted tree.
        def __init__(
                self,
                agents: tuple[Optional[BaseAgent], BaseAgent, BaseAgent, BaseAgent],
                render_mode: Optional[str] = None,
        ):
            """
            Initialize the multiplayer environment wrapper.
            
            Parameters
            ----------
            agents : tuple[Optional[BaseAgent], BaseAgent, BaseAgent, BaseAgent]
                A tuple of 4 agents. The first agent (None) represents the learning agent.
            render_mode : Optional[str], default=None
                The rendering mode.
            """
            self.agents = agents
            self.num_players = len(agents)
            super().__init__(render_mode=render_mode)

        def active_player(self) -> int:
            """
            Get the index of the currently active player.
            
            Returns
            -------
            int
                The active player's index (0-3).
            """
            return self.state_h.active_player

        def reset(self, *, seed=None, options=None):
            """
            Reset the environment and shuffle agent positions.
            
            Parameters
            ----------
            seed : int, optional
                Random seed for reproducibility.
            options : dict, optional
                Additional options for reset.
            
            Returns
            -------
            tuple[np.ndarray, dict]
                The initial observation and info dictionary.
            """
            # Shuffle agents to put each in a random seat each game.
            random_indexes = list(range(len(self.agents)))
            random.shuffle(random_indexes)
            agents_list = [self.agents[i] for i in random_indexes]
            self.agents = tuple(agents_list)

            return super().reset(seed=seed, options=options)

        def step(self, action : int):
            """
            Execute a step in the multiplayer environment.
            
            Continues executing actions for non-learning agents until control
            returns to the learning agent.
            
            Parameters
            ----------
            action : int
                The action to execute.
            
            Returns
            -------
            tuple[np.ndarray, float, bool, bool, dict]
                The observation, reward, done flag, truncated flag, and info dict.
            """
            while True:
                action_human = decode_int_to_human_action(action)

                state, reward, done, truncated, info = super().step(action)

                if self.agents[self.state_h.active_player] is None:
                    # Agent seat
                    return state, reward, done, truncated, info
                
                else:
                    # Get next agent's action and continue the loop
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

    return MultiplayerEnvWrapper