import numpy as np
from psai.game.translations import encode_human_to_vector_board, decode_vector_to_human_board
from psai.game.objects import State, Cell, PlayerStats
from psai.game.translations import encode_human_to_int_action, decode_int_to_human_action

def test_state_roundtrip(sample_game_state):
    """
    Test that encoding and decoding a state preserves all information.
    
    Verifies that a state can be encoded to a vector and decoded back
    with all attributes (board cells, player stats, game state) preserved.
    
    Parameters
    ----------
    sample_game_state : State
        A sample game state fixture for testing.
    """
    istate = sample_game_state
    vector = encode_human_to_vector_board(istate)
    dstate = decode_vector_to_human_board(vector)
    for icell in istate.board_state:
        for dcell in dstate.board_state:
            if icell.loc == dcell.loc:
                assert icell.owner == dcell.owner
                assert icell.used == dcell.used
                assert icell.size == dcell.size
                break
        else:
            raise ValueError('No matching cell found')
    assert dstate.sun_pos == istate.sun_pos
    assert dstate.hour == istate.hour
    assert dstate.player_stats == istate.player_stats
    assert dstate.active_player == istate.active_player
    assert dstate.day == istate.day
    assert dstate.n_score_cards_taken == istate.n_score_cards_taken

def test_state_roundtrip_plus(sample_game_state):
    """
    Test that double encoding produces identical vectors.
    
    Verifies that encoding → decoding → encoding produces the same
    vector as the first encoding, ensuring consistency.
    
    Parameters
    ----------
    sample_game_state : State
        A sample game state fixture for testing.
    """
    istate = sample_game_state
    vector_1 = encode_human_to_vector_board(istate)
    dstate = decode_vector_to_human_board(vector_1)
    vector_2 = encode_human_to_vector_board(dstate)
    assert np.array_equal(vector_1, vector_2), "Vectors do not match after encode-decode-encode roundtrip."

def test_action_roundtrip():
    """
    Test that the encode-decode-encode roundtrip for actions works correctly.
    
    Verifies that all possible action integers (0-1521) can be decoded to
    Action objects and then encoded back to the same integer, ensuring
    bidirectional consistency.
    """
    for iact in range(1521+1):
        action = decode_int_to_human_action(iact)
        jact = encode_human_to_int_action(action)
        assert jact == iact, f"Action encoding/decoding failed for action {action} with int {iact}. Encoded to {jact}."