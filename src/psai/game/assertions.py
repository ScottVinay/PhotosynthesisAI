def assertion_loc(ring, theta):
    """
    Asserts that the ring and theta indices are valid.
    """
    error_string = f'Ring = {ring}, Theta = {theta}'
    assert ring >= 0 and ring <= 3, error_string
    assert theta >= 0, error_string
    if ring == 0:
        assert theta < 18, error_string
    elif ring == 1:
        assert theta < 12, error_string
    elif ring == 2:
        assert theta < 6, error_string
    elif ring == 3:
        assert theta < 1, error_string