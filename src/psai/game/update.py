"""
File for the main function for updating the state of the game.
"""

from psai.game.assertions import assertion_loc
from psai.game.objects import State, Cell, Action, PlayerStats
from psai.game.actions import get_purchase_cost
from psai.game.utils import get_score_from_n_score_cards_taken

def update_state(
        state: State,
        action: Action
    ) -> None:
    """
    Update the game state based on the given action.
    
    Parameters
    ----------
    state : State
        The current game state.
    action : Action
        The action to be applied to the game state.
    
    Returns
    -------
    State
        The updated game state.
    """

    # 'purchase_tree'
    # 'plant_seed'
    # 'upgrade_tree'
    # 'harvest_tree'
    # 'end_turn'

    #-------------------#
    #   Purchase tree   #
    #-------------------#
    
    if action.action_type == 'purchase_tree':
        size = action.size
        assert size is not None
        assert type(size) == str
        
        stash_attr = size + '_stash'
        ready_attr = size + '_ready'

        # Remove the light
        state.player_stats[state.active_player].light -= get_purchase_cost(
            tree_size=size,
            stash_size=getattr(state.player_stats[state.active_player], stash_attr)
        )

        # Update the stash and ready counts
        setattr(state.player_stats[state.active_player], stash_attr, getattr(state.player_stats[state.active_player], stash_attr) - 1)
        setattr(state.player_stats[state.active_player], ready_attr, getattr(state.player_stats[state.active_player], ready_attr) + 1)
        

    #----------------#
    #   Plant seed   #
    #----------------#

    elif action.action_type == 'plant_seed':
        origin_loc = action.origin_loc
        target_loc = action.target_loc
        
        assert origin_loc is not None
        assert target_loc is not None
        
        # Get the cells at the specified locations
        origin_cell = state.get_cell_at_loc(origin_loc)
        target_cell = state.get_cell_at_loc(target_loc)

        # Update the target cell
        target_cell.owner = state.active_player
        target_cell.size = 'seed'
        target_cell.used = True
        
        # Update the origin cell to used
        origin_cell.used = True
        
        # Update player stats
        state.player_stats[state.active_player].seed_ready -= 1


    #------------------#
    #   Upgrade tree   #
    #------------------#

    elif action.action_type == 'upgrade_tree':
        target_loc = action.target_loc
        size = action.size
        
        assert target_loc is not None
        assert size is not None
        
        # Get the cell at the target location
        target_cell = state.get_cell_at_loc(target_loc)

        # Update the cell size
        if size == 'seed':
            target_cell.size = 'small'
            state.player_stats[state.active_player].seed_stash += 1
            state.player_stats[state.active_player].small_ready -= 1
            state.player_stats[state.active_player].light -= 1
        elif size == 'small':
            target_cell.size = 'medium'
            state.player_stats[state.active_player].small_stash += 1
            state.player_stats[state.active_player].medium_ready -= 1
            state.player_stats[state.active_player].light -= 2
        elif size == 'medium':
            target_cell.size = 'large'
            state.player_stats[state.active_player].medium_stash += 1
            state.player_stats[state.active_player].large_ready -= 1
            state.player_stats[state.active_player].light -= 3

        
    #------------------#
    #   Harvest tree   #
    #------------------#

    elif action.action_type == 'harvest_tree':
        target_loc = action.target_loc
        
        assert target_loc is not None
        
        # Get the cell at the target location
        target_cell = state.get_cell_at_loc(target_loc)

        # Update the cell to used
        target_cell.used = True
        
        # Update player stats
        state.player_stats[state.active_player].score += get_score_from_n_score_cards_taken(state.n_score_cards_taken)
        state.n_score_cards_taken += 1
        state.player_stats[state.active_player].large_stash += 1
        state.player_stats[state.active_player].light -= 4

        # Remove the tree from the board
        target_cell.size = None
        target_cell.owner = None

    
    #--------------#
    #   End turn   #
    #--------------#

    elif action.action_type == 'end_turn':    
        # Update active player
        state.active_player = (state.active_player + 1) % 4

        if state.active_player == 0:
            # Rotate the sun position if all players have gone.
            state.sun_pos = (state.sun_pos + 1) % 6
            # Also update the hour (same as sun_pos)
            state.hour = (state.hour + 1) % 6

            # Increment the turn counter if the sun position is at 0
            if state.sun_pos == 0:
                # Reset the used status for all cells
                state.day += 1
        
        # Reset used status for all cells
        for cell in state.board_state:
            cell.used = False
        
        #TODO Rotate the board state?
        #TODO Sun back to 0?


def distribute_light(state: State) -> None:
    """
    Distribute light to all players based on the current sun position.

    Parameters
    ----------
    state : State
        The current game state.
    """
    ...
    #TODO complete
