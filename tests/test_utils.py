from psai.game.objects import State, Cell, PlayerStats
from psai.game.utils import loc_int_to_tuple, loc_tuple_to_int

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