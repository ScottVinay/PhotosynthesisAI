"""
This is for translating human-readable game states into vectors and vice-versa.
"""

import numpy as np
from psai.game.objects import State, Cell, Action, PlayerStats
from psai.game.utils import loc_int_to_tuple, loc_tuple_to_int
from psai.game.assertions import assertion_loc

def encode_human_to_vector_board(
        state : State,
    ):
    """
    Convert a human-readable game state into a vector representation.
        
    Returns
    -------
    np.ndarray : A vector representation of the game state.
    """
    # Assertions

    # --------------- #
    #   Board state   #
    # --------------- #
    owner_onehot = np.zeros((37, 5))
    tree_size_onehot = np.zeros((37, 5))
    used_onehot = np.zeros(37,)

    
    tree_size_map = {None: 0, "seed": 1, "small": 2, "medium": 3, "large": 4}

    for cell in state.board_state:
        index = loc_tuple_to_int(cell.loc)
        owner_idx = cell.owner if cell.owner is not None else 4  # Use index 4 for None/no owner
        owner_onehot[index, owner_idx] = 1
        tree_size_onehot[index, tree_size_map[cell.size]] = 1
        used_onehot[index] = int(cell.used)


    # ---------------- #
    #   Sun position   #
    # ---------------- #
        
    sun_position_onehot = np.zeros(6)
    sun_position_onehot[state.sun_pos] = 1


    # ---------------- #
    #   Player stats   #
    # ---------------- #

    norms = {
        "light" : 10,
        "score" : 10,
        "seed_stash" : 4,
        "seed_ready" : 4,
        "small_stash" : 4,
        "small_ready" : 4,
        "medium_stash" : 4,
        "medium_ready" : 4,
        "large_stash" : 4,
        "large_ready" : 4,
    }

    all_player_vectors = np.zeros((4, len(norms.keys())))
    for ip in range(4):
        player_vector = np.array([
            getattr(state.player_stats[ip], name) / norms[name]
            for name in sorted(norms.keys())
        ], dtype=np.float32)
        all_player_vectors[ip, :] = player_vector
    
    # ----------------- #
    #   Active player   #
    # ----------------- #

    active_onehot = np.zeros(4)
    active_onehot[state.active_player] = 1
    
    
    # -------- #
    #   Turn   #
    # -------- #

    turn_onehot = np.zeros(5)
    turn_onehot[state.turn] = 1
        

    # ----------- #
    #   Combine   #
    # ----------- #

    vector = np.concatenate([
        owner_onehot.flatten(),
        tree_size_onehot.flatten(),
        used_onehot.flatten(),
        sun_position_onehot.flatten(),
        all_player_vectors.flatten(),
        active_onehot.flatten(),
        turn_onehot.flatten(),
    ])

    return vector


def decode_vector_to_human_board(vector: np.ndarray) -> State:
    """
    Convert a vector representation of the game state back to a human-readable format.

    Returns
    -------
    State : A human-readable representation of the game state.
    """
    tree_size_map = {0: None, 1: "seed", 2: "small", 3: "medium", 4: "large"}
    
    norms = {
        "light" : 10,
        "score" : 10,
        "seed_stash" : 4,
        "seed_ready" : 4,
        "small_stash" : 4,
        "small_ready" : 4,
        "medium_stash" : 4,
        "medium_ready" : 4,
        "large_stash" : 4,
        "large_ready" : 4,
    }

    idx = 0

    # Board state
    owner_onehot = vector[idx:idx+37*5].reshape((37, 5))
    idx += 37*5
    tree_size_onehot = vector[idx:idx+37*5].reshape((37, 5))
    idx += 37*5
    used_onehot = vector[idx:idx+37]
    idx += 37

    board_state = []
    for i_cell in range(37):
        owner_idx = int(np.argmax(owner_onehot[i_cell]))
        size_idx = int(np.argmax(tree_size_onehot[i_cell]))
        used = bool(round(used_onehot[i_cell]))
        loc = loc_int_to_tuple(i_cell)
        assertion_loc(*loc)
        cell = Cell(
            loc=loc,
            owner=owner_idx if owner_idx != 4 else None,  # Index 4 means no owner
            size=tree_size_map[size_idx],
            used=used,
        )
        board_state.append(cell)

    # Sun position
    sun_position_onehot = vector[idx:idx+6]
    sun_pos = int(np.argmax(sun_position_onehot))
    idx += 6

    # Player stats
    all_player_vectors = vector[idx:idx+4*10].reshape((4, 10))
    idx += 4*10
    player_stats = {}
    for ip in range(4):
        stats = {}
        for i, name in enumerate(sorted(norms.keys())):
            stats[name] = int(round(all_player_vectors[ip, i] * norms[name]))
        player_stats[ip] = PlayerStats(**stats)

    # Active player
    active_onehot = vector[idx:idx+4]
    idx += 4
    active_player = int(np.argmax(active_onehot))

    # Turn
    turn_onehot = vector[idx:idx+5]
    idx += 5
    turn = int(np.argmax(turn_onehot))

    state = State(
        board_state=board_state,
        sun_pos=sun_pos,
        player_stats=player_stats,
        active_player=active_player,
        turn=turn,
    )
    return state


def encode_human_to_int_action(
        action: Action,
    ) -> int:
    """
    Convert a human-readable action into an integer representation.

    Parameters
    ----------
    action : dict
        A dictionary representing the action, typically with keys like "action_type", "target", etc.

    Returns
    -------
    int
        The index of the action in the action space.
    """
    
    # This is a placeholder implementation.
    # You would need to define how to convert the action dictionary to an integer.
    #TODO
    return 0  # Replace with actual logic to convert action to integer index.


def decode_int_to_human_action(
        action: int,
    ) -> Action:
    """
    Convert a vector representation of an action back to a human-readable format.

    Parameters
    ----------
    vector : np.ndarray
        A 1D numpy array representing the action.
    action_space_size : int
        The size of the action space.

    Returns
    -------
    int
        The index of the action in the action space.
    """
    #TODO
    ...