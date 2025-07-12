import numpy as np
from psai.game.translations import encode_human_to_vector_board, decode_vector_to_human_board
from psai.game.objects import State, Cell, PlayerStats

def sample_game_state():
    board_state = [
        Cell(loc=(0,0), owner=0, size='small', used=True),
        Cell(loc=(0,1), owner=None, size=None, used=False),
        Cell(loc=(0,2), owner=1, size='medium', used=False),
        Cell(loc=(0,3), owner=0, size='small', used=True),
        Cell(loc=(0,4), owner=None, size=None, used=False),
        Cell(loc=(0,5), owner=1, size='medium', used=False),
        Cell(loc=(0,6), owner=0, size='small', used=True),
        Cell(loc=(0,7), owner=None, size=None, used=False),
        Cell(loc=(0,8), owner=1, size='medium', used=False),
        Cell(loc=(0,9), owner=3, size='large', used=True),
        Cell(loc=(0,10), owner=2, size=None, used=False),
        Cell(loc=(0,11), owner=1, size='seed', used=False),
        Cell(loc=(0,12), owner=3, size='large', used=True),
        Cell(loc=(0,13), owner=2, size=None, used=False),
        Cell(loc=(0,14), owner=1, size='seed', used=False),
        Cell(loc=(0,15), owner=1, size='seed', used=False),
        Cell(loc=(0,16), owner=3, size='large', used=True),
        Cell(loc=(0,17), owner=2, size=None, used=False),
        Cell(loc=(1,0), owner=1, size='seed', used=False),
        Cell(loc=(1,1), owner=0, size='seed', used=True),
        Cell(loc=(1,2), owner=1, size='seed', used=False),
        Cell(loc=(1,3), owner=0, size='seed', used=True),
        Cell(loc=(1,4), owner=3, size='medium', used=False),
        Cell(loc=(1,5), owner=2, size='seed', used=True),
        Cell(loc=(1,6), owner=1, size='small', used=False),
        Cell(loc=(1,7), owner=0, size='seed', used=True),
        Cell(loc=(1,8), owner=1, size='seed', used=False),
        Cell(loc=(1,9), owner=0, size='seed', used=True),
        Cell(loc=(1,10), owner=1, size='seed', used=False),
        Cell(loc=(1,11), owner=0, size='seed', used=True),
        Cell(loc=(2,0), owner=3, size='medium', used=False),
        Cell(loc=(2,1), owner=2, size='seed', used=True),
        Cell(loc=(2,2), owner=1, size='small', used=False),
        Cell(loc=(2,3), owner=0, size='seed', used=True),
        Cell(loc=(2,4), owner=1, size='small', used=False),
        Cell(loc=(2,5), owner=0, size='seed', used=True),
        Cell(loc=(3,0), owner=3, size='large', used=False),
    ]
    sun_pos = 3
    player_stats = {
        0: PlayerStats(
            light=5, score=2, seed_stash=1, seed_ready=2,
            small_stash=3, small_ready=1, medium_stash=0, medium_ready=1,
            large_stash=2, large_ready=0
        ),
        1: PlayerStats(
            light=7, score=4, seed_stash=2, seed_ready=1,
            small_stash=2, small_ready=2, medium_stash=1, medium_ready=0,
            large_stash=1, large_ready=1
        ),
        2: PlayerStats(
            light=3, score=6, seed_stash=0, seed_ready=3,
            small_stash=1, small_ready=3, medium_stash=2, medium_ready=2,
            large_stash=0, large_ready=2
        ),
        3: PlayerStats(
            light=10, score=8, seed_stash=4, seed_ready=0,
            small_stash=0, small_ready=0, medium_stash=4, medium_ready=4,
            large_stash=4, large_ready=4
        ),
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
    assert dstate.player_stats == istate.player_stats
    assert dstate.active_player == istate.active_player
    assert dstate.turn == istate.turn

def test_encode_decode_encode():
    istate = sample_game_state()
    vector_1 = encode_human_to_vector_board(istate)
    dstate = decode_vector_to_human_board(vector_1)
    vector_2 = encode_human_to_vector_board(dstate)
    assert np.array_equal(vector_1, vector_2), "Vectors do not match after encode-decode-encode roundtrip."