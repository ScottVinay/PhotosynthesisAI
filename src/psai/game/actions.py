"""
Here we have functions that deal with actions, such
as determining which actions are allowed based on the current game state.

The general kinds of action in the game are:
    - Purchase a tree and move it to the ready area.
    - Plant a seed in a cell.
    - Upgrade a seed or tree to the next level.
    - Harvest a tree.
    - End turn.

The human-readable actions are described as
    action_type: str
    size: Optional[str]
    origin_loc: Optional[tuple[int, int]]
    target_loc: Optional[tuple[int, int]]

The entry `origin_loc` is used for the tree that originates a seed only.
The entry `size` is used for the purchase option only.

"""

from psai.game.objects import State, Action, TSIZES
from psai.game.assertions import assertion_loc
from typing import Literal, Optional
from dataclasses import dataclass


def get_allowed_actions(state : State) -> list[Action]:
    """
    Returns a list of allowed actions for the current game state.
    """
    allowed_actions = []

    light = state.player_stats[state.active_player].light

    # ------------ #
    #   Purchase   #
    # ------------ #

    for tree_size in TSIZES:
        stash_size = getattr(state.player_stats[state.active_player], tree_size + '_stash')
        if stash_size >= 1 and light >= get_purchase_cost(
                tree_size = tree_size,
                stash_size = stash_size
            ):
            act = Action(
                action_type='purchase_tree',
                size=tree_size,
                origin_loc=None,
                target_loc=None,
            )
            allowed_actions.append(act)

    #TODO Plant initial - outer ring, no origin. Include distribute_light(state)

    # --------- #
    #   Plant   #
    # --------- #

    player_stats = state.player_stats[state.active_player]

    # Get all empty cells (no tree/seed)
    empty_cells = [cell for cell in state.board_state if cell.size is None]
    
    # For each empty cell, check if we can plant a seed there
    for target_cell in empty_cells:
        if player_stats.seed_ready > 0:
            # Check if there's a tree of the current player that can spread a seed to this location
            for origin_cell in state.board_state:
                if (origin_cell.owner == state.active_player and 
                    origin_cell.size is not None and 
                    not origin_cell.used and
                    not target_cell.used and
                    light >= 1 and
                    can_spread_seed(origin_cell, target_cell)):
                    
                    act = Action(
                        action_type='plant_seed',
                        size=None,
                        origin_loc=origin_cell.loc,
                        target_loc=target_cell.loc,
                    )
                    allowed_actions.append(act)

    # ----------- #
    #   Upgrade   #
    # ----------- #
    
    # For each tree owned by the active player, check if it can be upgraded
    for cell in state.board_state:
        if (cell.owner == state.active_player and 
            cell.size is not None and 
            not cell.used):
            
            if cell.size == 'seed' and player_stats.small_ready > 0 and light >= 1:
                act = Action(
                    action_type='upgrade_tree',
                    size='seed',
                    origin_loc=None,
                    target_loc=cell.loc,
                )
                allowed_actions.append(act)
                
            elif cell.size == 'small' and player_stats.medium_ready > 0 and light >= 2:
                act = Action(
                    action_type='upgrade_tree', 
                    size='small',
                    origin_loc=None,
                    target_loc=cell.loc,
                )
                allowed_actions.append(act)
                
            elif cell.size == 'medium' and player_stats.large_ready > 0 and light >= 3:
                act = Action(
                    action_type='upgrade_tree',
                    size='medium', 
                    origin_loc=None,
                    target_loc=cell.loc,
                )
                allowed_actions.append(act)

    # ---------- #
    #  Harvest   #
    # ---------- #
    
    # Large trees can be harvested for points
    for cell in state.board_state:
        if (cell.owner == state.active_player and 
            cell.size == 'large' and
            light >= 4 and
            not cell.used):
            
            act = Action(
                action_type='harvest_tree',
                size=None,
                origin_loc=None,
                target_loc=cell.loc,
            )
            allowed_actions.append(act)

    # ----------- #
    #  End Turn   #
    # ----------- #
    
    # Player can always choose to end their turn
    act = Action(
        action_type='end_turn',
        size=None,
        origin_loc=None,
        target_loc=None,
    )
    allowed_actions.append(act)

    return allowed_actions


def can_spread_seed(origin_cell, target_cell) -> bool:
    """
    Check if a tree can spread a seed to a target location.
    
    Parameters
    ----------
    origin_cell : Cell
        The cell containing the tree that wants to spread a seed.
    target_cell : Cell  
        The target cell where the seed would be planted.
        
    Returns
    -------
    bool
        True if the seed can be spread, False otherwise.
    """
    #TODO Check this function
    # Calculate distance between cells
    origin_ring, origin_theta = origin_cell.loc
    target_ring, target_theta = target_cell.loc
    
    # Simple distance calculation - this would need to be implemented properly
    # based on the hexagonal board geometry
    # For now, use a simple approximation
    
    # Seeds can only be spread up to a distance equal to the tree size
    spread_distance = {
        'seed': 1,
        'small': 1, 
        'medium': 2,
        'large': 3
    }
    
    max_distance = spread_distance.get(origin_cell.size, 0)
    
    # Simple ring-based distance (this is a simplification)
    if origin_ring == target_ring:
        # Same ring - check angular distance
        if origin_ring == 0:
            theta_distance = min(abs(origin_theta - target_theta), 
                               18 - abs(origin_theta - target_theta))
        elif origin_ring == 1:
            theta_distance = min(abs(origin_theta - target_theta),
                               12 - abs(origin_theta - target_theta))
        elif origin_ring == 2:
            theta_distance = min(abs(origin_theta - target_theta),
                               6 - abs(origin_theta - target_theta))
        else:  # ring 3
            theta_distance = 0
        return theta_distance <= max_distance
    else:
        # Different rings - use ring distance as approximation
        ring_distance = abs(origin_ring - target_ring)
        return ring_distance <= max_distance


def get_purchase_cost(
        tree_size : str,
        stash_size : int
    ) -> int:
    """
    Gets the cost of an action in light points. Note, the cost of buying a tree
    depends on the number already bought.   

    Parameters
    ----------
    tree_size : str
        The size of the tree to be purchased, one of 'seed', 'small', 'medium', 'large'.
    
    stash_size : int
        The number of trees of that size remaining in the player's stash.
    """
    costs = {
        'seed': [1e9, 2, 2, 1, 1],
        'small': [1e9, 3, 3, 2, 2],
        'medium': [1e9, 4, 3, 3],
        'large': [1e9, 5, 4],
    }
    return costs[tree_size][stash_size]