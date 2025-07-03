import numpy as np
from typing import Optional
from psai.game.assertions import assertion_ring_cell


def rotate_cell(
    ring: int,
    cell: int,
    rotation: int
) -> int:
    """
    Rotates the cell index.
    """
    assertion_ring_cell(ring, cell)

    if ring == 0:
        return (cell + rotation) % 18
    elif ring == 1:
        return (cell + rotation) % 12
    elif ring == 2:
        return (cell + rotation) % 6
    else:
        assert ring == 3
        return cell
    

def get_shaded_cells(
        ring : int,
        cell : int,
        sun_pos : int
    ) -> tuple[
        Optional[tuple[int, int]],
        Optional[tuple[int, int]],
        Optional[tuple[int, int]],
    ]:
    """
    Gets the cells that are shaded by a height 3 tree on the specified cell.
    """
    assertion_ring_cell(ring, cell)

    rotated_input_cell = rotate_cell(ring, cell, sun_pos) #TODO should be minus?
    rotated_results = get_shaded_cells(ring, rotated_input_cell, 0)

    unrotated_results = []
    for ringcell in rotated_results:
        if ringcell is not None:
            assertion_ring_cell(ringcell[0], ringcell[1])
            unrotated_cell = rotate_cell(
                ringcell[0],
                ringcell[1],
                -sun_pos
            )
            unrotated_results.append((ringcell[0], unrotated_cell))
        else:
            unrotated_results.append(None)

    assert len(unrotated_results) == 3
    return tuple(unrotated_results)


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
