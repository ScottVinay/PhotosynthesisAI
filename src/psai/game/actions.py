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
    {
        'action_type' : str,
        'size' : Optional[str], # 'seed', 'small', 'medium', 'large'
        'origin_cell' : Optional[tuple[int, int]], # (ring, cell) 
        'target_cell' : Optional[tuple[int, int]], # (ring, cell)
    )

The entry `origin_cell` is used for the tree that originates a seed only.
The entry `size` is used for the purchase option only.

"""

from psai.game.env import State
from psai.game.assertions import assertion_ring_cell
from typing import Literal, Optional
from dataclasses import dataclass


@dataclass
class Action:
    action_type: str
    size: Optional[str]
    origin_cell: Optional[tuple[int, int]]
    target_cell: Optional[tuple[int, int]]

    def __post_init__(self):
        assert self.action_type in [
            'purchase_tree',
            'plant_seed',
            'harvest_tree',
            'end_turn',
        ]
        
        if self.size is not None:
            assert self.size in [
                'seed',
                'small',
                'medium',
                'large'
            ]

        if self.origin_cell is not None:
            assertion_ring_cell(*self.origin_cell) 
        
        if self.target_cell is not None:
            assertion_ring_cell(*self.target_cell) 


def get_allowed_actions(state : State) -> list[Action]:
    """
    Returns a list of allowed actions for the current game state.
    """
    allowed_actions = []

    # ------------ #
    #   Purchase   #
    # ------------ #

    ap = 'p' + str(state.active_player + 1)
    light = state.player_stats[ap]['light']

    for tree_size in ['seed', 'small', 'medium', 'large']:
        stash_size = state.player_stats[ap][tree_size + '_stash']
        if stash_size >= 1 and light >= get_purchase_cost(
                tree_size = tree_size,
                stash_size = stash_size
            ):
            act = Action(
                action_type='purchase_tree',
                size=tree_size,
                origin_cell=None,
                target_cell=None,
            )
            allowed_actions.append(act)

    # --------- #
    #   Plant   #
    # --------- #

    if state.player_stats[ap]

    return allowed_actions


def get_purchase_cost(
        tree_size : str,
        stash_size : int
    ) -> int:
    """
    Gets the cost of an action in light points. Note, the cost of buying a tree
    depends on the number already bought.   

    Parameters
    ----------
    action
    """
    ...