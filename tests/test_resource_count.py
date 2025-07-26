"""
Test script to verify that the new n_score_cards_taken attribute works correctly
"""

import sys
import os
from psai.game.objects import State, Cell, PlayerStats
from psai.game.translations import encode_human_to_vector_board, decode_vector_to_human_board
import numpy as np

def create_minimal_state(n_score_cards_taken: int):
    """Create a minimal state for testing"""
    # Create minimal board state with just one cell
    board_state = [Cell(loc=(0, 0), owner=None, size=None, used=False)]
    
    # Add remaining cells to complete the board
    for ring in range(4):
        if ring == 0:
            max_theta = 18
            start_cell = 1 if ring == 0 else 0 
        elif ring == 1:
            max_theta = 12
            start_cell = 0
        elif ring == 2:
            max_theta = 6
            start_cell = 0
        elif ring == 3:
            max_theta = 1
            start_cell = 0
            
        for theta in range(start_cell, max_theta):
            board_state.append(Cell(loc=(ring, theta), owner=None, size=None, used=False))
    
    player_stats = {}
    for i in range(4):
        player_stats[i] = PlayerStats(
            light=0, score=0, seed_stash=4, seed_ready=0,
            small_stash=4, small_ready=0, medium_stash=3, medium_ready=0,
            large_stash=2, large_ready=0
        )
    
    return State(
        board_state=board_state,
        sun_pos=0,
        hour=0,
        player_stats=player_stats,
        active_player=0,
        day=0,
        n_score_cards_taken=n_score_cards_taken
    )

def test_n_score_cards_taken_encoding():
    """Test that n_score_cards_taken is correctly encoded and decoded"""
    print("Testing n_score_cards_taken encoding/decoding...")
    
    # Test various n_score_cards_taken values
    test_values = [0, 5, 10, 15, 20]
    
    for n_score_cards_taken in test_values:
        print(f"  Testing n_score_cards_taken = {n_score_cards_taken}")
        
        # Create state with this n_score_cards_taken
        original_state = create_minimal_state(n_score_cards_taken)
        
        # Encode to vector
        vector = encode_human_to_vector_board(original_state)
        print(f"    Vector shape: {vector.shape}")
        
        # Decode back to state
        decoded_state = decode_vector_to_human_board(vector)
        
        # Check that n_score_cards_taken is preserved
        assert decoded_state.n_score_cards_taken == n_score_cards_taken, \
            f"Resource count mismatch: expected {n_score_cards_taken}, got {decoded_state.n_score_cards_taken}"
        
        print(f"    ✓ Resource count correctly preserved: {decoded_state.n_score_cards_taken}")
    
    print("All n_score_cards_taken tests passed!")

def test_vector_size():
    """Test that the vector has the expected size"""
    print("Testing vector size...")
    
    state = create_minimal_state(10)
    vector = encode_human_to_vector_board(state)
    
    expected_size = 469  # As calculated: 185+185+37+6+6+40+4+5+1
    actual_size = vector.shape[0]
    
    print(f"Expected vector size: {expected_size}")
    print(f"Actual vector size: {actual_size}")
    
    assert actual_size == expected_size, \
        f"Vector size mismatch: expected {expected_size}, got {actual_size}"
    
    print("✓ Vector size is correct!")

if __name__ == "__main__":
    test_vector_size()
    test_n_score_cards_taken_encoding()
    print("\nAll tests passed successfully! 🎉")
