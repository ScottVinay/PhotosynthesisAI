from psai.game.objects import State, Cell, PlayerStats
from psai.game.utils import loc_int_to_tuple, loc_tuple_to_int, get_shaded_locs

def test_int_tuple_roundtrip():
    """
    Test that converting from int to tuple and back gives the same result.
    """
    for i in range(37):
        loc = loc_int_to_tuple(i)
        assert loc == loc_int_to_tuple(loc_tuple_to_int(loc)), f"Failed for index {i} with location {loc}"
    
    # Test edge cases
    assert loc_int_to_tuple(0) == (0, 0)
    assert loc_int_to_tuple(36) == (3, 0)

def test_get_shaded_cells():
    """
    Test that the shaded cells are correctly identified.
    """
    # Example cell at (0, 0) with sun position 3

    test_cases = [
        ((0, 0), 0, [(1, 0), (2, 0), (3, 0)]),
        ((0, 0), 1, [(0, 17), (0, 16), (0, 15)]),
    ]

    for (ring, theta), sun_pos, expected_cells in test_cases:
        print(f"Testing shaded cells for ring {ring}, theta {theta}, sun_pos {sun_pos}")
        shaded_cells = get_shaded_locs(ring, theta, sun_pos)
        expected_set = set(expected_cells)
        assert set(shaded_cells) == expected_set, f"Expected {expected_set}, got {set(shaded_cells)} for ring {ring}, theta {theta}, sun_pos {sun_pos}"


if __name__ == "__main__":
    test_get_shaded_cells()
    print("All tests passed!")