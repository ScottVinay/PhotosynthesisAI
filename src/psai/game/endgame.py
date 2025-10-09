from psai.game.objects import State
from psai.control.config import load_game_config


def check_has_game_ended(state: State) -> bool:
    if state.day == 3 and state.hour == 5:
        return True
    return False


def calculate_reward(state: State) -> dict[int, float]:
    """
    Calculate the reward for the current game state.

    Parameters
    ----------
    state : State
        The current game state.

    Returns
    -------
    dict[int, float]
        A dictionary mapping player IDs to their calculated rewards.
    """
    config = load_game_config()
    if config.reward_method == "score":
        reward = {}
        for i, player_stats in state.player_stats.items():
            reward[i] = player_stats.score

    elif config.reward_method == "normed":
        reward = {}
        max_score = max(player_stats.score for player_stats in state.player_stats.values())
        for i, player_stats in state.player_stats.items():
            reward[i] = player_stats.score / max_score if max_score > 0 else 0.
    
    elif config.reward_method == "winning_score":
        reward = {}
        max_score = max(player_stats.score for player_stats in state.player_stats.values())
        for i, player_stats in state.player_stats.items():
            reward[i] = player_stats.score if player_stats.score == max_score else 0.

    elif config.reward_method == "winner":
        reward = {}
        max_score = max(player_stats.score for player_stats in state.player_stats.values())
        for i, player_stats in state.player_stats.items():
            reward[i] = 1.0 if player_stats.score == max_score else 0.0
        #TODO Implement tie-breaker logic

    return reward