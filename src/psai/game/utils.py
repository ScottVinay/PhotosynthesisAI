import numpy as np
from typing import Optional
from psai.game.assertions import assertion_loc


def rotate_cell(
    ring: int,
    theta: int,
    rotation: int
) -> int:
    """
    Rotates the cell index.
    """
    assertion_loc(ring, theta)

    if ring == 0:
        return (theta + rotation) % 18
    elif ring == 1:
        return (theta + rotation) % 12
    elif ring == 2:
        return (theta + rotation) % 6
    else:
        assert ring == 3
        return theta
    

def get_shaded_cells(
        ring : int,
        theta : int,
        sun_pos : int
    ) -> tuple[
        Optional[tuple[int, int]],
        Optional[tuple[int, int]],
        Optional[tuple[int, int]],
    ]:
    """
    Gets the cells that are shaded by a height 3 tree on the specified cell.
    """
    assertion_loc(ring, theta)

    rotated_input_cell = rotate_cell(ring, theta, sun_pos) #TODO should be minus?
    rotated_results = get_shaded_cells(ring, rotated_input_cell, 0)

    unrotated_results = []
    for loc in rotated_results:
        if loc is not None:
            assertion_loc(loc[0], loc[1])
            unrotated_cell = rotate_cell(
                loc[0],
                loc[1],
                -sun_pos
            )
            unrotated_results.append((loc[0], unrotated_cell))
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


def loc_tuple_to_int(loc: tuple[int, int]) -> int:
    """
    Converts a cell location (ring, theta) to an integer index.

    Parameters
    ----------
    loc : tuple[int, int]
        A tuple representing the cell location, where the first element is the ring (0-3)
        and the second element is the cell index within that ring (0-17 for ring 0, 0-11 for ring 1, etc.). 

    Returns
    -------
    int
        An integer index corresponding to the cell location.
    """
    ring = loc[0]
    theta = loc[1]
    if ring == 0:
        prefix = 0
    elif ring == 1:
        prefix = 18
    elif ring == 2:
        prefix = 30
    elif ring == 3:
        prefix = 36
    return prefix + theta


def loc_int_to_tuple(ind: int) -> tuple[int, int]:
    """
    Converts an integer index to a cell location (ring, theta).
    Parameters
    ----------
    ind : int
        An integer index representing the cell location.
    Returns 
    -------
    tuple[int, int]
        A tuple where the first element is the ring (0-3) and the second element is the cell index within that ring.
    """
    assert isinstance(ind, int), f"Expected an integer index, got {type(ind)}"
    assert 0 <= ind < 37, f"Index {ind} out of bounds (0-36)"

    if ind < 18:
        ring = 0
        theta = ind - 0
    elif ind < 30:
        ring = 1
        theta = ind - 18
    elif ind < 36:
        ring = 2
        theta = ind - 30
    else:
        ring = 3
        theta = 0
    return ring, theta
    