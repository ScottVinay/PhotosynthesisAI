"""
This is for translating human-readable game states into vectors and vice-versa.
"""

import numpy as np

def encode_human_to_vector_board(
        board_state : dict[str, list[tuple]],
        sun_pos : int,
        player_stats : dict[str, dict[str, int]],
        active_player : int,
    ):
    """
    Convert a human-readable game state into a vector representation.
    
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
            "ring_1": [("p1", "seed", True), ("p2", "small", False), ("p1", "medium", False), ...,]
            "ring_2": [("p4", "small", False), ("p2", "seed", True), ("empty", "empty", False), ...,]
            ...,
        }

    sun_pos : int < 6
        The position of the sun in the game, typically an integer representing the current sun's position.

    player_stats : dict
        A dictionary containing player statistics.
        Keys are "p1", "p2", "p3", "p4" and values are dictionaries with keys:
        - "light": int, the amount of light the player has
        - "score": int, the player's score
        - "seeds_stash": int, the number of seeds the player has in their stash.
        - "seeds_ready": int, the number of seeds the player has ready to plant.
        - "small_stash": int
        - "small_ready": int
        - "medium_stash": int
        - "medium_ready": int
        - "large_stash": int
        - "large_ready": int

        The price of the next tree will depend on the value of stash.

    active_player : int < 4
        The index of the active player (0, 1, 2, or 3).
        
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
        ring_details = board_state[f"ring_{i_ring + 1}"]
        for owner, size, used in ring_details:
            owner_onehot[i_cell, owner_map[owner]] = 1
            tree_size_onehot[i_cell, tree_size_map[size]] = 1
            used_onehot[i_cell] = 1 if used else 0
            i_cell += 1


    # ---------------- #
    #   Sun position   #
    # ---------------- #
        
    sun_position_onehot = np.zeros(6)
    sun_position_onehot[sun_pos] = 1


    # ---------------- #
    #   Player stats   #
    # ---------------- #

    norms = {
        "light" : 10,
        "score" : 10,
        "seeds_stash" : 4,
        "seeds_ready" : 4,
        "small_stash" : 4,
        "small_ready" : 4,
        "medium_stash" : 4,
        "medium_ready" : 4,
        "large_stash" : 4,
        "large_ready" : 4,
    }

    assert set(norms.keys()) == set(player_stats["p1"].keys()), \
        "Player stats keys do not match expected keys."

    all_player_vectors = np.zeros((4, len(player_stats["p1"].keys())))
    for ip, player in enumerate(["p1", "p2", "p3", "p4"]):
        player_vector = np.array([
            player_stats[player][name] / norms[name]
            for name in sorted(norms.keys())
        ], dtype=np.float32)
        all_player_vectors[ip, :] = player_vector
    
    # ----------------- #
    #   Active player   #
    # ----------------- #

    active_onehot = np.zeros(4)
    active_onehot[active_player] = 1
            

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
    ])

    return vector



def create_rotation_index(board_moves_clockwise : bool) -> np.ndarray:
    """
    Gets the vector that rotates the board state by 1/6.

    Parameters
    ----------
    board_moves_clockwise : bool
        If True, the board is rotated clockwise; if False, counter-clockwise.
    
    Returns
    -------
    np.ndarray
        A 1D numpy array of shape equal to that of the board state vector.
        board_vector[rotation_vector] will give the rotated board state.
    """
    ...



def decode_vector_to_human_board(
        vector: np.ndarray
    ) -> tuple[
        dict[str, list[tuple]],
        int,
        dict[str, dict[str, int]],
        int
    ]:
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
    stat_names = [
        "light", "score", "seeds_stash", "seeds_ready",
        "small_stash", "small_ready", "medium_stash", "medium_ready",
        "large_stash", "large_ready"
    ]
    norms = {
        "light" : 10,
        "score" : 10,
        "seeds_stash" : 4,
        "seeds_ready" : 4,
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
        board_state[f"ring_{i_ring+1}"] = ring

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
    active_player = int(np.argmax(active_onehot))

    return board_state, sun_pos, player_stats, active_player


