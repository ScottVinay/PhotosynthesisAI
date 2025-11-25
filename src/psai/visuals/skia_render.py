from __future__ import annotations

from typing import Optional, Tuple

import skia  # type: ignore
import numpy as np
import imageio.v3 as iio

import math

from psai.game.objects import State, Cell, PlayerStats


class SkiaRenderer:
	"""
	Render a Photosynthesis State using skia-python.

	This mirrors the layout of MplRenderer: board on the left, info panel on the right.
	"""

	def __init__(self, width: int = 1200, height: int = 800, background: str = "#f0f8ff") -> None:
		if skia is None:
			raise ImportError(
				"skia-python is required. Install with: pip install skia-python"
			)
		self.width = width
		self.height = height

		# Colors
		self.colors = {
			"background": background,  # Alice blue
			"empty_cell": "#f5f5dc",  # Beige
			"board_outline": "#000000",  # Black
			"players": ["#ff6347", "#3cb371", "#1e90ff", "#ffa500"],  # tomato, mediumseagreen, dodgerblue, orange
			"sun": "#ffd700",  # Gold
			"used_colour": "#20202080",  # Semi-transparent grey
			"text": "#000000",
		}

		# Board layout in a normalized "world" coordinate system [-4,4] x [-4,4]
		self.board_world_min = (-4.0, -4.0)
		self.board_world_max = (4.0, 4.0)
		self.board_center = (0.0, 0.0)
		self.ring_radii = [3.0, 2.0, 1.0, 0.0]
		self.cell_radius = 0.5

		# Panel split: 2:1 (board:info)
		self.board_frac = 2.0 / 3.0

		# Fonts
		self.font_title = skia.Font(skia.Typeface('Arial', skia.FontStyle.Bold()), 22)
		self.font_large = skia.Font(skia.Typeface('Arial'), 18)
		self.font_medium = skia.Font(skia.Typeface('Arial'), 14)
		self.font_small = skia.Font(skia.Typeface('Arial'), 12)

	# --------- Utilities ---------
	def _hex_to_color4f(self, hex_color: str) -> skia.Color4f:
		"""Convert #RRGGBB[AA] to skia.Color4f."""
		hex_color = hex_color.lstrip('#')
		if len(hex_color) == 6:
			r = int(hex_color[0:2], 16) / 255.0
			g = int(hex_color[2:4], 16) / 255.0
			b = int(hex_color[4:6], 16) / 255.0
			a = 1.0
		elif len(hex_color) == 8:
			r = int(hex_color[0:2], 16) / 255.0
			g = int(hex_color[2:4], 16) / 255.0
			b = int(hex_color[4:6], 16) / 255.0
			a = int(hex_color[6:8], 16) / 255.0
		else:
			# Fallback to opaque black
			r = g = b = 0.0
			a = 1.0
		return skia.Color4f(r, g, b, a)

	def _paint(self, color_hex: str, style: skia.Paint.Style = skia.Paint.kFill_Style, stroke_width: float = 1.0) -> skia.Paint:
		paint = skia.Paint(Color4f=self._hex_to_color4f(color_hex))
		paint.setStyle(style)
		paint.setStrokeWidth(stroke_width)
		paint.setAntiAlias(True)
		return paint

	def _world_to_board_pixels(self, x: float, y: float) -> Tuple[float, float]:
		"""Map world coords [-4,4]x[-4,4] onto the left board area in pixels."""
		board_w = int(self.width * self.board_frac)
		board_h = self.height

		# Keep aspect ratio square by padding; compute scale from min dimension
		scale = min(board_w, board_h) / (self.board_world_max[0] - self.board_world_min[0])

		# Origin mapping: center of board area
		origin_x = board_w / 2.0
		origin_y = board_h / 2.0

		px = origin_x + x * scale
		py = origin_y - y * scale
		return px, py

	def _world_radius_to_px(self, r: float) -> float:
		board_w = int(self.width * self.board_frac)
		scale = min(board_w, self.height) / (self.board_world_max[0] - self.board_world_min[0])
		return r * scale

	def polar_to_cartesian(self, ring: int, theta: int) -> Tuple[float, float]:
		"""
		Convert polar (ring, theta) coordinates to Cartesian (x, y) coordinates.
		
		Parameters
		----------
		ring : int
			The ring index (0 is outermost, 3 is center).
		theta : int
			The angular position within the ring.
		
		Returns
		-------
		Tuple[float, float]
			The (x, y) coordinates in world space.
		"""
		if ring == 3:  # center
			return self.board_center

		radius = self.ring_radii[ring]
		positions_in_ring = [18, 12, 6, 1][ring]
		# Start from top and go clockwise, matching mpl renderer
		angle = (theta / positions_in_ring) * 2 * math.pi - math.pi / 2

		y = self.board_center[1] + radius * math.sin(-angle)
		x = self.board_center[0] + radius * math.cos(-angle)
		return (x, y)

	# --------- Rendering ---------
	def render_state(self, state: State, save_path: Optional[str] = None, return_image: bool = False):
		"""
		Render the full game state using Skia.
		
		Parameters
		----------
		state : State
			The game state to render.
		save_path : Optional[str], default=None
			If provided, saves the rendered image to this file path.
		return_image : bool, default=False
			If True, returns the rendered skia.Image.
		
		Returns
		-------
		Optional[skia.Image]
			The rendered image if return_image is True, otherwise None.
		"""
		surface = skia.Surface(self.width, self.height)
		canvas = surface.getCanvas()
		canvas.clear(self._hex_to_color4f(self.colors["background"]))

		# Split rects
		board_rect = skia.Rect.MakeXYWH(0, 0, int(self.width * self.board_frac), self.height)
		info_rect = skia.Rect.MakeXYWH(board_rect.width(), 0, self.width - board_rect.width(), self.height)

		# Draw board border (optional subtle outline)
		canvas.drawRect(board_rect, self._paint("#00000020", style=skia.Paint.kStroke_Style, stroke_width=1))

		# Draw cells
		for cell in state.board_state:
			self._draw_cell(canvas, cell)

		# Draw sun
		self._draw_sun(canvas, state.sun_pos)

		# Draw info panel
		self._draw_info_panel(canvas, info_rect, state)

		image = surface.makeImageSnapshot()
		if save_path:
			data = image.encodeToData()  # PNG by default
			if data is not None:
				with open(save_path, 'wb') as f:
					f.write(bytes(data))

		return image if return_image else None


	def save_animation_from_images(
        self,
		images: list[skia.Image],
		save_path: str,
		fps: int = 4,
		loop: int = 0,
	) -> None:
		"""Save a sequence of ``skia.Image`` frames as an animated GIF.

		Parameters
		----------
		images:
			Ordered list of frames returned by :py:meth:`skia.Surface.makeImageSnapshot`.
		save_path:
			Output path. The file extension should typically be ``.gif``.
		fps:
			Frames per second. Controls frame duration (default 4).
		loop:
			Number of extra animation loops. ``0`` means infinite looping.
		"""
		if not images:
			raise ValueError("No frames provided for animation.")

		first = images[0]
		if not isinstance(first, skia.Image):
			raise TypeError("Frames must be skia.Image instances obtained from makeImageSnapshot().")

		width, height = first.width(), first.height()
		frames: list[np.ndarray] = []

		for idx, frame in enumerate(images):
			if not isinstance(frame, skia.Image):
				raise TypeError(f"Frame {idx} is not a skia.Image.")
			if frame.width() != width or frame.height() != height:
				raise ValueError("All frames must share the same dimensions.")

			array = frame.toarray()
			if array.dtype != np.uint8:
				array = np.clip(array, 0, 255).astype(np.uint8)
			frames.append(array)

		if fps <= 0:
			raise ValueError("fps must be > 0")
		frame_duration = 1.0 / fps

		iio.imwrite(
			save_path,
			frames,
			duration=frame_duration,
			loop=loop,
			format_hint='.gif',
		)

	def _draw_cell(self, canvas: 'skia.Canvas', cell: Cell) -> None:
		"""
		Draw a single cell on the canvas.
		
		Parameters
		----------
		canvas : skia.Canvas
			The canvas to draw on.
		cell : Cell
			The cell object to render.
		
		Returns
		-------
		None
		"""
		xw, yw = self.polar_to_cartesian(*cell.loc)
		px, py = self._world_to_board_pixels(xw, yw)
		pr = self._world_radius_to_px(self.cell_radius)

		# Empty cell background
		canvas.drawCircle(px, py, pr, self._paint(self.colors['empty_cell']))
		canvas.drawCircle(px, py, pr, self._paint(self.colors['board_outline'], style=skia.Paint.kStroke_Style, stroke_width=1))

		# Tree if present
		if cell.size is not None and cell.owner is not None:
			size_multipliers = {"seed": 0.1, "small": 0.3, "medium": 0.6, "large": 0.95}
			tree_radius = pr * size_multipliers[cell.size]
			player_color = self.colors['players'][cell.owner]
			canvas.drawCircle(px, py, tree_radius, self._paint(player_color))

			# Used overlay (a small bar across the cell)
			if cell.used:
				bar_h = max(2.0, pr * 0.15)
				bar_w = pr * 2.0
				rect = skia.Rect.MakeXYWH(px - bar_w / 2.0, py - bar_h / 2.0, bar_w, bar_h)
				canvas.drawRect(rect, self._paint(self.colors['used_colour']))

	def _draw_sun(self, canvas: 'skia.Canvas', sun_pos: int) -> None:
		"""
		Draw the sun position indicator on the canvas.
		
		Parameters
		----------
		canvas : skia.Canvas
			The canvas to draw on.
		sun_pos : int
			The sun position (0-5) indicating which direction the sun is shining from.
		
		Returns
		-------
		None
		"""
		sun_radius_world = 3.5
		angle = (sun_pos / 6.0) * 2.0 * math.pi - math.pi / 2.0

		xw = self.board_center[0] + sun_radius_world * math.cos(angle)
		yw = self.board_center[1] + sun_radius_world * math.sin(angle)

		px, py = self._world_to_board_pixels(xw, yw)
		pr = self._world_radius_to_px(0.2)
		canvas.drawCircle(px, py, pr, self._paint(self.colors['sun']))
		canvas.drawCircle(px, py, pr, self._paint('#ffa500', style=skia.Paint.kStroke_Style, stroke_width=2))

		# Rays
		for i in range(8):
			ray_angle = (i / 8.0) * 2.0 * math.pi
			start_world_r = 0.25
			end_world_r = 0.35

			sxw = xw + start_world_r * math.cos(ray_angle)
			syw = yw + start_world_r * math.sin(ray_angle)
			exw = xw + end_world_r * math.cos(ray_angle)
			eyw = yw + end_world_r * math.sin(ray_angle)

			sx, sy = self._world_to_board_pixels(sxw, syw)
			ex, ey = self._world_to_board_pixels(exw, eyw)
			canvas.drawLine(sx, sy, ex, ey, self._paint(self.colors['sun'], style=skia.Paint.kStroke_Style, stroke_width=2))

	def _draw_info_panel(self, canvas: 'skia.Canvas', panel_rect: 'skia.Rect', state: State) -> None:
		"""
		Draw the information panel showing game state and player statistics.
		
		Parameters
		----------
		canvas : skia.Canvas
			The canvas to draw on.
		panel_rect : skia.Rect
			The rectangle defining the info panel area.
		state : State
			The game state containing player information.
		
		Returns
		-------
		None
		"""
		# Panel background (subtle)
		canvas.drawRect(panel_rect, self._paint('#ffffff'))
		canvas.drawRect(panel_rect, self._paint('#00000020', style=skia.Paint.kStroke_Style, stroke_width=1))

		x0 = panel_rect.left() + 16
		y = panel_rect.top() + 28

		paint_text = self._paint(self.colors['text'])

		def draw_text(text: str, x: float, y: float, font: 'skia.Font', color: Optional[str] = None):
			p = paint_text if color is None else self._paint(color)
			canvas.drawString(text, x, y, font, p)

		# Game info
		draw_text(f"Day: {state.day + 1}", x0, y, self.font_title)
		y += 30
		draw_text(f"Active Player: {state.active_player}", x0, y, self.font_large)
		y += 24
		draw_text(f"Score Cards Taken: {state.n_score_cards_taken}", x0, y, self.font_large)
		y += 28

		draw_text("Player Stats:", x0, y, self.font_title)
		y += 30

		for player_id, stats in state.player_stats.items():
			color = self.colors['players'][player_id]
			active_marker = " (ACTIVE)" if player_id == state.active_player else ""
			draw_text(f"Player {player_id}{active_marker}", x0, y, self.font_large, color=color)
			y += 22

			lines = [
				f"Light: {stats.light}    Score: {stats.score}",
				f"Seeds: {stats.seed_stash}+{stats.seed_ready}",
				f"Small: {stats.small_stash}+{stats.small_ready}",
				f"Medium: {stats.medium_stash}+{stats.medium_ready}",
				f"Large: {stats.large_stash}+{stats.large_ready}",
			]
			for line in lines:
				draw_text(line, x0 + 16, y, self.font_medium)
				y += 18
			y += 8


# --------- Simple demo runner ---------
def _sample_game_state() -> State:
	"""
	Generate a random sample game state for testing visualization.
	
	Creates a game state with randomly assigned cell owners, tree sizes,
	and player statistics for demonstration purposes.
	
	Returns
	-------
	State
		A randomly generated game state.
	"""
	import random
	owners = [None, 0, 1, 2, 3]
	sizes = [None, 'seed', 'small', 'medium', 'large']

	board_state = []
	ring_positions = {0: 18, 1: 12, 2: 6, 3: 1}
	for ring, n_positions in ring_positions.items():
		for theta in range(n_positions):
			owner = random.choice(owners)
			size = random.choice(sizes) if owner is not None else None
			used = random.choice([True, False])
			board_state.append(Cell(loc=(ring, theta), owner=owner, size=size, used=used))

	player_stats = {
		0: PlayerStats(light=5, score=2, seed_stash=1, seed_ready=2, small_stash=3, small_ready=1, medium_stash=0, medium_ready=1, large_stash=2, large_ready=0),
		1: PlayerStats(light=7, score=4, seed_stash=2, seed_ready=1, small_stash=2, small_ready=2, medium_stash=1, medium_ready=0, large_stash=1, large_ready=1),
		2: PlayerStats(light=3, score=6, seed_stash=0, seed_ready=3, small_stash=1, small_ready=3, medium_stash=2, medium_ready=2, large_stash=0, large_ready=2),
		3: PlayerStats(light=10, score=8, seed_stash=4, seed_ready=0, small_stash=0, small_ready=0, medium_stash=4, medium_ready=4, large_stash=4, large_ready=4),
	}

	return State(
		board_state=board_state,
		sun_pos=0,
		hour=0,
		player_stats=player_stats,
		active_player=2,
		day=0,
		n_score_cards_taken=15,
	)


if __name__ == "__main__":  # pragma: no cover - manual demo
	st = _sample_game_state()
	renderer = SkiaRenderer(width=1200, height=800)
	renderer.render_state(st, save_path="skia_render_demo.png")

