"""
This is for translating human-readable game states into vectors and vice-versa.
"""

import numpy as np

def encode_human_to_vector(
        board_state : dict[str, tuple],
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
        The values are tuples of (owner, tree_size, used) for each cell in the ring.

        - owner: str, the player who owns the cell (e.g., "p1", "p2", "empty").
        - tree_size: str, the size of the tree in the cell (e.g., "seed", "small", "medium", "large", "empty").
        - used: bool, indicates whether the cell has been used this turn.

        Example:
        {
            "ring_1": ("p1", "seed", True), ("p2", "small", False), ("p1", "medium", False), ...,
            "ring_2": ("p4", "small", False), ("p2", "seed", True), ("empty", "empty", False), ...,
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
        
        TODO Mention in blog: Also note that we technically do not need "ready",
        since this is available as the values on board minus stash, but it probably helps.
        

    active_player : int < 4
        The index of the active player (0, 1, 2, or 3).
        
        
    Returns
    -------
    np.ndarray : A vector representation of the game state.
    """
    assert 1==1
    ...


def create_rotation_index() -> np.ndarray:
    ...



# def encode_board_state(board, sun_pos, player_stats, active_player):
#     """
#     board: list of 37 cells, each cell is (owner, tree_size)
#     sun_pos: int 0-5
#     player_stats: list of dicts, each with keys 'light', 'score', 'seeds', 'small', 'medium', 'large'
#     active_player: int 0-3
#     """
#     # Board grid: 37 cells × (owner, size)
#     # We'll one-hot encode owner (5 options: 0=None, 1-4), and tree_size (0-5)
#     owner_onehot = np.zeros((37, 5))
#     size_onehot = np.zeros((37, 6))
#     for i, (owner, size) in enumerate(board):
#         owner_onehot[i, owner] = 1
#         size_onehot[i, size] = 1

#     # Flatten board
#     board_flat = np.concatenate([owner_onehot.flatten(), size_onehot.flatten()])

#     # Sun position (one-hot)
#     sun_onehot = np.zeros(6)
#     sun_onehot[sun_pos] = 1

#     # Player stats
#     stats_flat = []
#     for stats in player_stats:
#         stats_flat.extend([
#             stats['light'],
#             stats['score'],
#             stats['seeds'],
#             stats['small'],
#             stats['medium'],
#             stats['large'],
#         ])
#     stats_flat = np.array(stats_flat, dtype=np.float32)

#     # Player turn (one-hot)
#     turn_onehot = np.zeros(4)
#     turn_onehot[active_player] = 1

#     # Final state vector
#     state_vec = np.concatenate([board_flat, sun_onehot, stats_flat, turn_onehot])
#     return state_vec
