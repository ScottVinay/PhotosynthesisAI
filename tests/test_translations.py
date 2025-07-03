import numpy as np
from psai.game.translations import encode_human_to_vector_board, decode_vector_to_human_board
from psai.game.env import State

def sample_game_state():
    board_state = {
        "ring_1": [("p1", "seed", True)] * 3*6,
        "ring_2": [("p2", "small", False)] * 2*6,
        "ring_3": [("empty", "empty", False)] * 6,
        "ring_4": [("p3", "large", True)] * 1,
    }
    sun_pos = 3
    player_stats = {
        "p1": {
            "light": 5, "score": 2, "seed_stash": 1, "seed_ready": 2,
            "small_stash": 3, "small_ready": 1, "medium_stash": 0, "medium_ready": 1,
            "large_stash": 2, "large_ready": 0
        },
        "p2": {
            "light": 7, "score": 4, "seed_stash": 2, "seed_ready": 1,
            "small_stash": 2, "small_ready": 2, "medium_stash": 1, "medium_ready": 0,
            "large_stash": 1, "large_ready": 1
        },
        "p3": {
            "light": 3, "score": 6, "seed_stash": 0, "seed_ready": 3,
            "small_stash": 1, "small_ready": 3, "medium_stash": 2, "medium_ready": 2,
            "large_stash": 0, "large_ready": 2
        },
        "p4": {
            "light": 10, "score": 8, "seed_stash": 4, "seed_ready": 0,
            "small_stash": 0, "small_ready": 0, "medium_stash": 4, "medium_ready": 4,
            "large_stash": 4, "large_ready": 4
        },
    }
    active_player = 2
    turn = 0
    return State(
        board_state=board_state,
        sun_pos=sun_pos,
        player_stats=player_stats,
        active_player=active_player,
        turn=turn,
    )

def test_encode_decode_roundtrip():
    istate = sample_game_state()
    vector = encode_human_to_vector_board(istate)
    dstate = decode_vector_to_human_board(vector)
    for k, v in istate.board_state.items():
        assert len(dstate.board_state[k]) == len(v)
        for i, (owner, tree_size, is_seed) in enumerate(v):
            decoded_owner, decoded_tree_size, decoded_is_seed = dstate.board_state[k][i]
            assert owner == decoded_owner
            assert tree_size == decoded_tree_size
            assert is_seed == decoded_is_seed
    assert dstate.sun_pos == istate.sun_pos
    assert dstate.player_stats == istate.player_stats
    assert dstate.active_player == istate.active_player
    assert dstate.turn == istate.turn

def test_encode_decode_encode():
    istate = sample_game_state()
    vector_1 = encode_human_to_vector_board(istate)
    dstate = decode_vector_to_human_board(vector_1)
    vector_2 = encode_human_to_vector_board(dstate)
    assert np.array_equal(vector_1, vector_2), "Vectors do not match after encode-decode-encode roundtrip."