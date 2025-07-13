from psai.game.assertions import assertion_loc
from typing import Optional
from dataclasses import dataclass

TSIZES = ['seed', 'small', 'medium', 'large']

@dataclass
class Cell:
    loc: tuple[int, int]
    owner: Optional[int]
    size: Optional[str]
    used: bool

    def __post_init__(self):
        self.verify()

    def verify(self):
        assertion_loc(*self.loc)
        if self.owner is not None:
            assert self.owner >= 0 and self.owner < 4
        if self.size is not None:
            assert self.size in TSIZES, f'Size is {self.size}'

@dataclass
class PlayerStats:
    light: int # the amount of light the player has
    score: int # the player's score
    seed_stash: int # the number of seed the player has in their stash.
    seed_ready: int # the number of seed the player has ready to plant.
    small_stash: int
    small_ready: int
    medium_stash: int
    medium_ready: int
    large_stash: int
    large_ready: int

    def verify(self):
        maximum_in_stash = {
            'seed': 4,
            'small': 4,
            'medium': 3,
            'large': 2,
        }
        for size in maximum_in_stash.keys():
            assert getattr(self, size + '_stash') <= maximum_in_stash[size]

@dataclass
class State:
    """
    Parameters
    ----------
    board_state : list[Cell]
        The cells of the board

    sun_pos : int < 6
        The position of the sun in the game, typically an integer representing the current sun's position.

    player_stats : dict[int, PlayerStats]

    active_player : int < 4
        The index of the active player (0, 1, 2, or 3).
    """
    board_state: list[Cell]
    sun_pos: int
    player_stats: dict[int, PlayerStats]
    active_player: int
    day: int

    def __post_init__(self):
        self.verify_board_state(self.board_state)
        self.verify_sun_pos(self.sun_pos)
        self.verify_player_stats(self.player_stats)
        self.verify_active_player(self.active_player)
        self.verify_turn(self.day)

    def verify_board_state(self, board_state : list[Cell]):
        for cell in board_state:
            cell.verify()
        list_of_locs = [cell.loc for cell in board_state]
        assert len(list_of_locs) == len(set(list_of_locs))

    def verify_sun_pos(self, sun_pos: int):
        if not (0 <= sun_pos < 6):
            raise ValueError(f"Invalid sun position: {sun_pos}. Must be in range [0, 5].")
        
    def verify_player_stats(self, player_stats: dict[int, PlayerStats]):
        for ip in range(4):
            if ip not in player_stats.keys():
                raise ValueError(f"Missing stats for player: {ip}")
            

    def verify_active_player(self, active_player: int):
        if not (0 <= active_player < 4):
            raise ValueError(f"Invalid active player index: {active_player}. Must be in range [0, 3].")
        
    def verify_turn(self, turn: int):
        assert turn >= 0 and turn < 5

    def get_cell_at_loc(self, loc: tuple[int, int]) -> Cell:
        """
        Returns the cell at the given location.
        """
        assertion_loc(*loc)
        for cell in self.board_state:
            if cell.loc == loc:
                return cell
        raise ValueError(f"No cell found at valid location {loc}.")


@dataclass
class Action:
    action_type: str
    size: Optional[str]
    origin_loc: Optional[tuple[int, int]]
    target_loc: Optional[tuple[int, int]]

    def __post_init__(self):
        assert self.action_type in [
            'purchase_tree',
            'plant_seed',
            'upgrade_tree',
            'harvest_tree',
            'end_turn',
        ]
        
        if self.size is not None:
            assert self.size in [
                'seed',
                'small',
                'medium',
                'large'
            ]

        if self.origin_loc is not None:
            assertion_loc(*self.origin_loc) 
        
        if self.target_loc is not None:
            assertion_loc(*self.target_loc) 