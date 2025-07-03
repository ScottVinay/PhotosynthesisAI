def assertion_ring_cell(ring, cell):
    """
    Asserts that the ring and cell indices are valid.
    """
    assert ring >= 0 and ring <= 3
    assert cell >= 0
    if ring == 0:
        assert cell < 18
    elif ring == 1:
        assert cell < 12
    elif ring == 2:
        assert cell < 6
    elif ring == 3:
        assert cell < 1