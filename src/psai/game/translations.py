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
    turn_onehot[state.day] = 1
    
    # ------------------- #
    #   Resource count    #
    # ------------------- #

    n_score_cards_taken_normalized = np.array([state.n_score_cards_taken / 20.0], dtype=np.float32)
        

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
        n_score_cards_taken_normalized.flatten(),
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

    # Resource count
    n_score_cards_taken_normalized = vector[idx:idx+1]
    idx += 1
    n_score_cards_taken = int(round(n_score_cards_taken_normalized[0] * 20.0))

    state = State(
        board_state=board_state,
        sun_pos=sun_pos,
        player_stats=player_stats,
        active_player=active_player,
        day=turn,
        n_score_cards_taken=n_score_cards_taken,
    )
    return state


def encode_human_to_int_action(
        action: Action,
    ) -> int:
    """
    Convert a human-readable action into an integer representation.

    The action space is organized as follows:
    - Purchase actions: 0-3 (seed, small, medium, large)
    - Plant seed actions: 4 + (origin_cell_idx * 37 + target_cell_idx) [4 to 1372]
    - Upgrade actions: 1373 + (cell_idx * 3 + size_idx) [1373 to 1483] 
    - Harvest actions: 1484 + cell_idx [1484 to 1520]
    - End turn: 1521

    Parameters
    ----------
    action : Action
        An Action object representing the action.

    Returns
    -------
    int
        The index of the action in the action space.
    """
    
    if action.action_type == 'purchase_tree':
        if action.size is None:
            raise ValueError("Purchase action must have a size specified")
        size_map = {'seed': 0, 'small': 1, 'medium': 2, 'large': 3}
        return size_map[action.size]
    
    elif action.action_type == 'plant_seed':
        if action.origin_loc is None or action.target_loc is None:
            raise ValueError("Plant seed action must have both origin_loc and target_loc specified")
        origin_idx = loc_tuple_to_int(action.origin_loc)
        target_idx = loc_tuple_to_int(action.target_loc)
        return 4 + origin_idx * 37 + target_idx
    
    elif action.action_type == 'upgrade_tree':
        if action.target_loc is None or action.size is None:
            raise ValueError("Upgrade action must have target_loc and size specified")
        cell_idx = loc_tuple_to_int(action.target_loc)
        size_map = {'small': 0, 'medium': 1, 'large': 2}
        size_idx = size_map[action.size]
        return 1373 + cell_idx * 3 + size_idx
    
    elif action.action_type == 'harvest_tree':
        if action.target_loc is None:
            raise ValueError("Harvest action must have target_loc specified")
        cell_idx = loc_tuple_to_int(action.target_loc)
        return 1484 + cell_idx
    
    elif action.action_type == 'end_turn':
        return 1521
    
    else:
        raise ValueError(f"Unknown action type: {action.action_type}")


def decode_int_to_human_action(
        action_int: int,
    ) -> Action:
    """
    Convert an integer action index back to a human-readable Action format.

    The action space is organized as follows:
    - Purchase actions: 0-3 (seed, small, medium, large)
    - Plant seed actions: 4 + (origin_cell_idx * 37 + target_cell_idx) [4 to 1372]
    - Upgrade actions: 1373 + (cell_idx * 3 + size_idx) [1373 to 1483] 
    - Harvest actions: 1484 + cell_idx [1484 to 1520]
    - End turn: 1521

    Parameters
    ----------
    action_int : int
        The integer index of the action.

    Returns
    -------
    Action
        An Action object representing the action.
    """
    
    if 0 <= action_int <= 3:
        # Purchase action
        size_map = {0: 'seed', 1: 'small', 2: 'medium', 3: 'large'}
        return Action(
            action_type='purchase_tree',
            size=size_map[action_int],
            origin_loc=None,
            target_loc=None,
        )
    
    elif 4 <= action_int <= 1372:
        # Plant seed action
        adjusted_idx = action_int - 4
        origin_idx = adjusted_idx // 37
        target_idx = adjusted_idx % 37
        return Action(
            action_type='plant_seed',
            size=None,
            origin_loc=loc_int_to_tuple(origin_idx),
            target_loc=loc_int_to_tuple(target_idx),
        )
    
    elif 1373 <= action_int <= 1483:
        # Upgrade action
        adjusted_idx = action_int - 1373
        cell_idx = adjusted_idx // 3
        size_idx = adjusted_idx % 3
        size_map = {0: 'small', 1: 'medium', 2: 'large'}
        return Action(
            action_type='upgrade_tree',
            size=size_map[size_idx],
            origin_loc=None,
            target_loc=loc_int_to_tuple(cell_idx),
        )
    
    elif 1484 <= action_int <= 1520:
        # Harvest action
        cell_idx = action_int - 1484
        return Action(
            action_type='harvest_tree',
            size=None,
            origin_loc=None,
            target_loc=loc_int_to_tuple(cell_idx),
        )
    
    elif action_int == 1521:
        # End turn action
        return Action(
            action_type='end_turn',
            size=None,
            origin_loc=None,
            target_loc=None,
        )
    
    else:
        raise ValueError(f"Invalid action index: {action_int}. Valid range is 0-1521.")