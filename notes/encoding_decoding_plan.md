# Sequence of encoding and decoding

My proposition is to use a function I have developed that

My proposition is to use a function I have developed that maps a state vector to a human-readable json form, then use this in a function to find the set of allowable actions that are passed into a function that translates action strings into action vectors, which I use to mask the allowable actions. These are passed to the agent who chooses one of them. I then need to turn this back into a json, to calculate the effect on the board state (json board state to json board state). This is then mapped back to a state vector to update the environment.

Let $S$ be the board state, $A$ be the action representation, $v$ be vector or integer form, and $h$ be a human-readable dictionary.

1. $\quad S_v \rightarrow S_h\quad$  `decode_vector_to_human_board` ✅
2. $\quad S_h \rightarrow \{A_h\}\quad$  `get_allowed_actions`
3. $\quad \{A_h\} \rightarrow \{A_v\}\quad$  `encode_human_to_int_action`
4. $\quad \{A_v\} \rightarrow A^*_v\quad$  `agent`
5. $\quad A^*_v \rightarrow A^*_h\quad$  `decode_int_to_human_action`
6. $\quad A^*_h, S_h \rightarrow S^\prime_h\quad$  `update_board_from_action` (include rotation)
7. $\quad S^\prime_h \rightarrow S^\prime_v\quad$  `encode_human_to_vector_board` ✅

# Other helper functions

```
get_shaded_cells(
        ring : int,
        cell : int,
        sun_pos : int
    ) -> tuple[
        Optional[tuple[int, int]],
        Optional[tuple[int, int]],
        Optional[tuple[int, int]],
    ]:
    """
    Gets the cells that are shaded by a height 3 tree on the specified cell.
    """
    ...
```