import pygame
import math
import sys
from typing import Optional
from psai.game.objects import State, Action, Cell, PlayerStats

# Color constants
COLORS = {
    'background': (240, 248, 255),  # Alice blue
    'board': (139, 69, 19),         # Saddle brown
    'empty_cell': (245, 245, 220),  # Beige
    'players': [
        (255, 99, 71),   # Tomato - Player 0
        (60, 179, 113),  # Medium sea green - Player 1  
        (30, 144, 255),  # Dodger blue - Player 2
        (255, 165, 0),   # Orange - Player 3
    ],
    'tree_sizes': {
        'seed': (160, 82, 45),      # Saddle brown
        'small': (34, 139, 34),     # Forest green
        'medium': (0, 128, 0),      # Green
        'large': (0, 100, 0),       # Dark green
    },
    'text': (0, 0, 0),              # Black
    'sun': (255, 215, 0),           # Gold
    'used_overlay': (255, 0, 0, 100),  # Semi-transparent red
}

class GameRenderer:
    def __init__(self, width=1200, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Photosynthesis AI")
        
        # Font setup
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)
        
        # Board layout parameters
        self.board_center = (400, 400)
        self.ring_radii = [80, 140, 200, 240]  # Radii for rings 0, 1, 2, 3
        self.cell_radius = 15
        
        # UI layout
        self.info_panel_x = 820
        self.info_panel_width = 360
        
        self.running = True
        
    def polar_to_cartesian(self, ring: int, theta: int) -> tuple[int, int]:
        """Convert ring-theta coordinates to screen x,y coordinates."""
        if ring == 3:  # Center
            return self.board_center
            
        radius = self.ring_radii[ring]
        
        # Calculate number of positions in this ring
        positions_in_ring = [18, 12, 6, 1][ring]
        
        # Calculate angle - start from top and go clockwise
        angle = (theta / positions_in_ring) * 2 * math.pi - math.pi/2
        
        x = self.board_center[0] + radius * math.cos(angle)
        y = self.board_center[1] + radius * math.sin(angle)
        
        return (int(x), int(y))
    
    def draw_cell(self, cell: Cell):
        """Draw a single cell on the board."""
        x, y = self.polar_to_cartesian(cell.loc[0], cell.loc[1])
        
        # Draw empty cell background
        pygame.draw.circle(self.screen, COLORS['empty_cell'], (x, y), self.cell_radius)
        pygame.draw.circle(self.screen, COLORS['board'], (x, y), self.cell_radius, 2)
        
        # Draw tree if present
        if cell.size is not None and cell.owner is not None:
            # Tree size determines radius
            size_multipliers = {'seed': 0.3, 'small': 0.5, 'medium': 0.7, 'large': 0.9}
            tree_radius = int(self.cell_radius * size_multipliers[cell.size])
            
            # Draw tree with player color and size-specific tint
            player_color = COLORS['players'][cell.owner]
            tree_color = COLORS['tree_sizes'][cell.size]
            
            # Blend player color with tree color
            blended_color = tuple((p + t) // 2 for p, t in zip(player_color, tree_color))
            
            pygame.draw.circle(self.screen, blended_color, (x, y), tree_radius)
            
            # Draw used overlay if cell is used
            if cell.used:
                overlay_surface = pygame.Surface((tree_radius * 2, tree_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(overlay_surface, COLORS['used_overlay'], 
                                 (tree_radius, tree_radius), tree_radius)
                self.screen.blit(overlay_surface, (x - tree_radius, y - tree_radius))
        
        # Draw location label for debugging (small text)
        loc_text = self.font_small.render(f"{cell.loc[0]},{cell.loc[1]}", True, COLORS['text'])
        text_rect = loc_text.get_rect(center=(x, y + self.cell_radius + 10))
        self.screen.blit(loc_text, text_rect)
    
    def draw_sun(self, sun_pos: int, hour: int):
        """Draw the sun position indicator."""
        # Sun positions around the board
        sun_radius = 300
        angle = (sun_pos / 6) * 2 * math.pi - math.pi/2
        
        sun_x = self.board_center[0] + sun_radius * math.cos(angle)
        sun_y = self.board_center[1] + sun_radius * math.sin(angle)
        
        # Draw sun
        pygame.draw.circle(self.screen, COLORS['sun'], (int(sun_x), int(sun_y)), 25)
        pygame.draw.circle(self.screen, COLORS['text'], (int(sun_x), int(sun_y)), 25, 2)
        
        # Draw sun rays
        for i in range(8):
            ray_angle = (i / 8) * 2 * math.pi
            ray_start_x = sun_x + 30 * math.cos(ray_angle)
            ray_start_y = sun_y + 30 * math.sin(ray_angle)
            ray_end_x = sun_x + 40 * math.cos(ray_angle)
            ray_end_y = sun_y + 40 * math.sin(ray_angle)
            pygame.draw.line(self.screen, COLORS['sun'], 
                           (ray_start_x, ray_start_y), (ray_end_x, ray_end_y), 3)
        
        # Draw sun position and hour text
        sun_text = self.font_medium.render(f"Sun: {sun_pos} | Hour: {hour}", True, COLORS['text'])
        self.screen.blit(sun_text, (int(sun_x) - 50, int(sun_y) - 60))
    
    def draw_player_stats(self, player_stats: dict[int, PlayerStats], active_player: int):
        """Draw player statistics panel."""
        y_offset = 50
        
        # Title
        title = self.font_large.render("Player Stats", True, COLORS['text'])
        self.screen.blit(title, (self.info_panel_x, y_offset))
        y_offset += 40
        
        for player_id, stats in player_stats.items():
            # Player header with color
            player_color = COLORS['players'][player_id]
            active_marker = " (ACTIVE)" if player_id == active_player else ""
            player_text = self.font_medium.render(f"Player {player_id}{active_marker}", True, player_color)
            self.screen.blit(player_text, (self.info_panel_x, y_offset))
            y_offset += 25
            
            # Stats
            stats_lines = [
                f"Light: {stats.light}  Score: {stats.score}",
                f"Seeds: {stats.seed_stash}+{stats.seed_ready}",
                f"Small: {stats.small_stash}+{stats.small_ready}",
                f"Medium: {stats.medium_stash}+{stats.medium_ready}",
                f"Large: {stats.large_stash}+{stats.large_ready}",
            ]
            
            for line in stats_lines:
                stat_text = self.font_small.render(line, True, COLORS['text'])
                self.screen.blit(stat_text, (self.info_panel_x + 20, y_offset))
                y_offset += 18
            
            y_offset += 10  # Extra spacing between players
    
    def draw_game_info(self, state: State):
        """Draw general game information."""
        y_offset = 350
        
        info_lines = [
            f"Day: {state.day + 1}",
            f"Score Cards Taken: {state.n_score_cards_taken}",
            "",
            "Actions:",
            "- purchase_tree",
            "- plant_seed", 
            "- upgrade_tree",
            "- harvest_tree",
            "- end_turn",
        ]
        
        for line in info_lines:
            if line == "Actions:":
                text = self.font_medium.render(line, True, COLORS['text'])
            else:
                text = self.font_small.render(line, True, COLORS['text'])
            self.screen.blit(text, (self.info_panel_x, y_offset))
            y_offset += 20
    
    def render_state(self, state: State):
        """Render the complete game state."""
        # Clear screen
        self.screen.fill(COLORS['background'])
        
        # Draw board cells
        for cell in state.board_state:
            self.draw_cell(cell)
        
        # Draw sun
        self.draw_sun(state.sun_pos, state.hour)
        
        # Draw UI panels
        self.draw_player_stats(state.player_stats, state.active_player)
        self.draw_game_info(state)
        
        # Update display
        pygame.display.flip()
    
    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def get_action_from_input(self) -> Optional[Action]:
        """Get action from command line input."""
        print("\nEnter action (or 'quit' to exit):")
        print("Format: action_type [size] [origin_ring,origin_theta] [target_ring,target_theta]")
        print("Example: plant_seed seed 1,5 0,10")
        print("Example: end_turn")
        
        user_input = input("> ").strip()
        
        if user_input.lower() == 'quit':
            return None
            
        parts = user_input.split()
        if not parts:
            print("Invalid input. Please try again.")
            return self.get_action_from_input()
        
        action_type = parts[0]
        size = None
        origin_loc = None
        target_loc = None
        
        try:
            if len(parts) > 1 and parts[1] in ['seed', 'small', 'medium', 'large']:
                size = parts[1]
                parts = parts[1:]  # Remove size from parts for further processing
            
            if len(parts) > 1:
                origin_coords = parts[1].split(',')
                if len(origin_coords) == 2:
                    origin_loc = (int(origin_coords[0]), int(origin_coords[1]))
            
            if len(parts) > 2:
                target_coords = parts[2].split(',')
                if len(target_coords) == 2:
                    target_loc = (int(target_coords[0]), int(target_coords[1]))
            
            return Action(
                action_type=action_type,
                size=size,
                origin_loc=origin_loc,
                target_loc=target_loc
            )
            
        except (ValueError, IndexError) as e:
            print(f"Invalid input format: {e}. Please try again.")
            return self.get_action_from_input()
    
    def run_interactive(self, initial_state: State):
        """Run the interactive visualization."""
        current_state = initial_state
        clock = pygame.time.Clock()
        
        print("Photosynthesis AI Interactive Visualization")
        print("Close the window or press ESC to exit")
        print("Enter actions in the terminal")
        
        while self.running:
            # Handle pygame events
            if not self.handle_events():
                break
            
            # Render current state
            self.render_state(current_state)
            
            # Get action from user (this will block)
            action = self.get_action_from_input()
            if action is None:  # User wants to quit
                break
            
            print(f"Action received: {action}")
            # Here you would normally apply the action to get a new state
            # For now, we just continue with the same state
            
            clock.tick(60)
        
        pygame.quit()

def create_renderer() -> GameRenderer:
    """Factory function to create a game renderer."""
    return GameRenderer()

def render_state_static(state: State, save_path: Optional[str] = None):
    """Render a state to a static image (useful for debugging/testing)."""
    renderer = GameRenderer()
    renderer.render_state(state)
    
    if save_path:
        pygame.image.save(renderer.screen, save_path)
        print(f"State rendered and saved to {save_path}")
    else:
        # Show for 3 seconds then close
        pygame.time.wait(3000)
    
    pygame.quit()

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
    hour = 3
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
    # Create a sample state
    state = sample_game_state()
    
    if len(sys.argv) > 1 and sys.argv[1] == "static":
        render_state_static(state)
    else:
        renderer = create_renderer()
        renderer.run_interactive(state)
