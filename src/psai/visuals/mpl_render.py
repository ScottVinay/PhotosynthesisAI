import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Optional
from psai.game.objects import State, Action, Cell, PlayerStats
import random

class MplRenderer:
    def __init__(self, figsize=(12, 8)):
        self.figsize = figsize
        
        # Colors
        self.colors = {
            'background': '#f0f8ff',  # Alice blue
            'empty_cell': '#f5f5dc',  # Beige
            'board_outline': "#000000",  # Black
            'players': ['#ff6347', '#3cb371', '#1e90ff', '#ffa500'],  # Player colors
            'sun': '#ffd700',  # Gold
            'used_colour': "#20202080",  # Semi-transparent grey
        }
        
        # Board layout
        self.board_center = (0, 0)
        self.ring_radii = [3, 2, 1, 0]  # Normalized radii
        self.cell_radius = 0.5
        
    def polar_to_cartesian(self, ring: int, theta: int) -> tuple[float, float]:
        """Convert ring-theta coordinates to x,y coordinates."""
        if ring == 3:  # Center
            return self.board_center
            
        radius = self.ring_radii[ring]
        positions_in_ring = [18, 12, 6, 1][ring]
        
        # Calculate angle - start from top and go clockwise
        angle = (theta / positions_in_ring) * 2 * np.pi - np.pi/2
        
        y = self.board_center[1] + radius * np.sin(-angle)
        x = self.board_center[0] + radius * np.cos(-angle)
        
        return (x, y)
    
    def render_state(self, state: State, save_path: Optional[str] = None, show: bool = True):
        """Render the complete game state."""
        fig, (ax_board, ax_info) = plt.subplots(1, 2, figsize=self.figsize, 
                                               gridspec_kw={'width_ratios': [2, 1]})
        
        # Set up board axis
        ax_board.set_xlim(-4, 4)
        ax_board.set_ylim(-4, 4)
        ax_board.axis('off')
        ax_board.set_aspect('equal')
        # ax_board.set_title('Photosynthesis Game Board', fontsize=16, fontweight='bold')
        ax_board.set_facecolor(self.colors['background'])
        
        # Draw board cells
        for cell in state.board_state:
            self._draw_cell(ax_board, cell)
        
        # Draw sun
        self._draw_sun(ax_board, state.sun_pos)
        
        # Draw info panel
        self._draw_info_panel(ax_info, state)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            
        if show:
            plt.show()
        else:
            plt.close()
            
    def _draw_cell(self, ax, cell: Cell):
        """Draw a single cell on the board."""
        x, y = self.polar_to_cartesian(*cell.loc)
        
        # Draw empty cell background
        circle = patches.Circle((x, y), self.cell_radius, 
                              facecolor=self.colors['empty_cell'],
                              edgecolor=self.colors['board_outline'], 
                              linewidth=1)
        ax.add_patch(circle)
        
        # Draw tree if present
        if cell.size is not None and cell.owner is not None:
            size_multipliers = {'seed': 0.1, 'small': 0.3, 'medium': 0.6, 'large': 0.95}
            tree_radius = self.cell_radius * size_multipliers[cell.size]
            
            # Blend player color with tree color
            player_color = self.colors['players'][cell.owner]
            
            tree_circle = patches.Circle((x, y), tree_radius,
                                       facecolor=player_color,
                                       edgecolor=player_color,
                                       linewidth=2)
            ax.add_patch(tree_circle)
            
            # Draw used overlay if cell is used
            if cell.used:
                # Draw a line through the cell
                line = patches.Rectangle((x - self.cell_radius, y), 2 * self.cell_radius, 0.1 * self.cell_radius,
                                         facecolor=self.colors['used_colour'], alpha=0.5)
                ax.add_patch(line)
        
        # Draw location label
        # ax.text(x, y - self.cell_radius - 0.15, f"{cell.loc[0]},{cell.loc[1]}", 
        #        ha='center', va='top', fontsize=8, alpha=0.7)
    
    def _draw_sun(self, ax, sun_pos: int):
        """Draw the sun position indicator."""
        sun_radius = 3.5
        angle = (sun_pos / 6) * 2 * np.pi - np.pi/2
        
        sun_x = self.board_center[0] + sun_radius * np.cos(angle)
        sun_y = self.board_center[1] + sun_radius * np.sin(angle)
        
        # Draw sun
        sun_circle = patches.Circle((sun_x, sun_y), 0.2,
                                  facecolor=self.colors['sun'],
                                  edgecolor='orange', linewidth=2)
        ax.add_patch(sun_circle)
        
        # Draw sun rays
        for i in range(8):
            ray_angle = (i / 8) * 2 * np.pi
            ray_start_x = sun_x + 0.25 * np.cos(ray_angle)
            ray_start_y = sun_y + 0.25 * np.sin(ray_angle)
            ray_end_x = sun_x + 0.35 * np.cos(ray_angle)
            ray_end_y = sun_y + 0.35 * np.sin(ray_angle)
            ax.plot([ray_start_x, ray_end_x], [ray_start_y, ray_end_y], 
                   color=self.colors['sun'], linewidth=2)
            
    
    def _draw_info_panel(self, ax, state: State):
        """Draw the information panel."""
        ax.axis('off')
        
        # Game info
        game_info = [
            f"Day: {state.day + 1}",
            f"Active Player: {state.active_player}",
            f"Score Cards Taken: {state.n_score_cards_taken}",
            "",
        ]
        
        # Player stats
        y_pos = 0.95
        for line in game_info:
            ax.text(0.05, y_pos, line, transform=ax.transAxes, 
                   fontsize=12, fontweight='bold')
            y_pos -= 0.08
        
        # Player statistics
        ax.text(0.05, y_pos, "Player Stats:", transform=ax.transAxes,
               fontsize=14, fontweight='bold')
        y_pos -= 0.1
        
        for player_id, stats in state.player_stats.items():
            color = self.colors['players'][player_id]
            active_marker = " (ACTIVE)" if player_id == state.active_player else ""
            
            ax.text(0.05, y_pos, f"Player {player_id}{active_marker}", 
                   transform=ax.transAxes, fontsize=12, fontweight='bold', color=color)
            y_pos -= 0.06
            
            stats_text = [
                f"  Light: {stats.light}  Score: {stats.score}",
                f"  Seeds: {stats.seed_stash}+{stats.seed_ready}",
                f"  Small: {stats.small_stash}+{stats.small_ready}",
                f"  Medium: {stats.medium_stash}+{stats.medium_ready}",
                f"  Large: {stats.large_stash}+{stats.large_ready}",
            ]
            
            for line in stats_text:
                ax.text(0.05, y_pos, line, transform=ax.transAxes, fontsize=10)
                y_pos -= 0.04
            
            y_pos -= 0.03  # Extra spacing between players


def sample_game_state():
    # Possible values
    owners = [None, 0, 1, 2, 3]
    sizes = [None, 'seed', 'small', 'medium', 'large']

    board_state = []
    # Define cell locations for rings 0, 1, 2, 3
    ring_positions = {0: 18, 1: 12, 2: 6, 3: 1}
    for ring, n_positions in ring_positions.items():
        for theta in range(n_positions):
            owner = random.choice(owners)
            size = random.choice(sizes) if owner is not None else None
            used = random.choice([True, False])
            board_state.append(
                Cell(loc=(ring, theta), owner=owner, size=size, used=used)
            )
    sun_pos = 0
    hour = 0
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
    n_score_cards_taken = 15
    return State(
        board_state=board_state,
        sun_pos=sun_pos,
        hour=hour,
        player_stats=player_stats,
        active_player=active_player,
        day=turn,
        n_score_cards_taken=n_score_cards_taken,
    )

if __name__ == "__main__":
    state = sample_game_state()
    renderer = MplRenderer()

    renderer.render_state(state)
    