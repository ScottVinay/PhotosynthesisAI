"""
This is for translating human-readable game states into vectors and vice-versa.
"""

import numpy as np
from psai.game.env import State

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

    owner_map = {"empty": 0, "p1": 1, "p2": 2, "p3": 3, "p4": 4}
    tree_size_map = {"empty": 0, "seed": 1, "small": 2, "medium": 3, "large": 4}

    i_cell = 0
    for i_ring in range(4):
        ring_details = state.board_state[i_ring]
        for owner, size, used in ring_details:
            owner_onehot[i_cell, owner_map[owner]] = 1
            tree_size_onehot[i_cell, tree_size_map[size]] = 1
            used_onehot[i_cell] = 1 if used else 0
            i_cell += 1


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

    assert set(norms.keys()) == set(state.player_stats["p1"].keys()), \
        "Player stats keys do not match expected keys."

    all_player_vectors = np.zeros((4, len(state.player_stats["p1"].keys())))
    for ip, player in enumerate(["p1", "p2", "p3", "p4"]):
        player_vector = np.array([
            state.player_stats[player][name] / norms[name]
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
    board_state : dict
        As described in encode_human_to_vector.
    sun_pos : int
        Sun position.
    player_stats : dict
        Player statistics.
    active_player : int
        Index of the active player.
    """
    owner_map = {0: "empty", 1: "p1", 2: "p2", 3: "p3", 4: "p4"}
    tree_size_map = {0: "empty", 1: "seed", 2: "small", 3: "medium", 4: "large"}
    player_names = ["p1", "p2", "p3", "p4"]
    
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

    board_state = {}
    i_cell = 0
    for i_ring in range(4):
        ring = []
        for _ in range(0, [12, 12, 6, 7][i_ring]):
            owner_idx = int(np.argmax(owner_onehot[i_cell]))
            size_idx = int(np.argmax(tree_size_onehot[i_cell]))
            used = bool(round(used_onehot[i_cell]))
            ring.append((owner_map[owner_idx], tree_size_map[size_idx], used))
            i_cell += 1
        board_state[i_ring] = ring

    # Sun position
    sun_position_onehot = vector[idx:idx+6]
    sun_pos = int(np.argmax(sun_position_onehot))
    idx += 6

    # Player stats
    all_player_vectors = vector[idx:idx+4*10].reshape((4, 10))
    idx += 4*10
    player_stats = {}
    for ip, player in enumerate(player_names):
        stats = {}
        for i, name in enumerate(sorted(norms.keys())):
            stats[name] = int(round(all_player_vectors[ip, i] * norms[name]))
        player_stats[player] = stats

    # Active player
    active_onehot = vector[idx:idx+4]
    idx += 4
    active_player = int(np.argmax(active_onehot))

    # Turn
    turn_onehot = vector[idx:idx+5]
    idx += 4
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
        action: dict,
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
    
    return 0  # Replace with actual logic to convert action to integer index.


def decode_int_to_human_action(
        action: int,
    ) -> dict:
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
    
    return {}