import numpy as np
from typing import Optional
from psai.game.assertions import assertion_loc


def rotate_loc(
    ring: int,
    theta: int,
    rotation: int
) -> tuple[int, int]:
    """
    Rotates the cell index.
    """
    assertion_loc(ring, theta)

    n = rotation * (3 - ring)  

    if ring == 0:
        new_theta = (theta + n) % 18
    elif ring == 1:
        new_theta = (theta + n) % 12
    elif ring == 2:
        new_theta = (theta + n) % 6
    else:
        assert ring == 3
        new_theta = theta
    return (ring, new_theta)
    

def get_shaded_locs(
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

    if sun_pos != 0:
        rotated_input_loc = rotate_loc(ring, theta, -sun_pos)
        rotated_results = get_shaded_locs(*rotated_input_loc, 0)
        
        shaded_locs = []
        for loc in rotated_results:
            if loc is not None:
                assertion_loc(loc[0], loc[1])
                unrotated_loc = rotate_loc(
                    loc[0],
                    loc[1],
                    sun_pos
                )
                shaded_locs.append(unrotated_loc)
            else:
                shaded_locs.append(None)

        assert len(shaded_locs) == 3

    else:
        mapping = {
            (0, 0): [(1, 0), (2, 0), (3, 0)],
            (0, 1): [(1, 1), (2, 1), (2, 2)],
            (0, 2): [(1, 2), (1, 3), (1, 4)],
            (0, 3): [(0, 4), (0, 5), (0, 6)],
            (0, 4): [(0, 5), (0, 6), None],
            (0, 5): [(0, 6), None, None],
            (0, 6): [None, None, None],
            (0, 7): [None, None, None],
            (0, 8): [None, None, None],
            (0, 9): [None, None, None],
            (0, 10): [None, None, None],
            (0, 11): [None, None, None],
            (0, 12): [None, None, None],
            (0, 13): [(0, 12), None, None],
            (0, 14): [(0, 13), (0, 12), None],
            (0, 15): [(0, 14), (0, 13), (0, 12)],
            (0, 16): [(1, 10), (1, 9), (1, 8)],
            (0, 17): [(1, 11), (2, 5), (2, 4)],
            (1, 0): [(2, 0), (3, 0), None],
            (1, 1): [(2, 1), (2, 2), (1, 5)],
            (1, 2): [(1, 3), (1, 4), (0, 7)],
            (1, 3): [(1, 4), (0, 7), None],
            (1, 4): [(0, 7), None, None],
            (1, 5): [(0, 8), None, None],
            (1, 6): [(0, 9), None, None],
            (1, 7): [(0, 10), None, None],
            (1, 8): [(0, 11), None, None],
            (1, 9): [(1, 8), (0, 11), None],
            (1, 10): [(1, 9), (1, 8), (0, 11)],
            (1, 11): [(2, 5), (2, 4), (1, 7)],
            (2, 0): [(3, 0), (2, 3), (1, 6)],
            (2, 1): [(2, 2), (1, 5), (0, 8)],
            (2, 2): [(1, 5), (0, 8), None],
            (2, 3): [(1, 6), (0, 9), None],
            (2, 4): [(1, 7), (0, 10), None],
            (2, 5): [(2, 4), (1, 7), (0, 10)],
            (3, 0): [(2, 3), (1, 6), (0, 9)],
        }
        shaded_locs = mapping[(ring, theta)]

    return (shaded_locs[0], shaded_locs[1], shaded_locs[2])

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
    