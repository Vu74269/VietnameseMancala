"""Scene chơi chính cho giao diện pygame."""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

import pygame

from config import CLOCKWISE, COUNTER_CLOCKWISE
from game.engine import GameEngine, FinalResult, TurnContext
from game.players.bot_player import BotPlayer
from game.ui.pygame_ui.assets import AssetManager
from game.ui.pygame_ui.scenes.base_scene import BaseScene
from game.ui.pygame_ui.scenes.menu_scene import MenuScene
from game.ui.pygame_ui import settings


class GameScene(BaseScene):
	def __init__(
		self,
		app: "PygameApp",
		engine: GameEngine,
		assets: AssetManager,
		last_rps: Tuple[str, str] | None = None,
	) -> None:
		self.app = app
		self.engine = engine
		self.assets = assets

		self.title_font = pygame.font.SysFont("georgia", 40, bold=True)
		self.head_font = pygame.font.SysFont("cambria", 28, bold=True)
		self.body_font = pygame.font.SysFont("segoeui", 22)
		self.small_font = pygame.font.SysFont("segoeui", 18)

		self.pit_centers = self._build_pit_centers()
		# Circular buttons for CW/CCW arrows
		self.cw_button = pygame.Rect(930, 636, 68, 68)
		self.ccw_button = pygame.Rect(1016, 636, 68, 68)

		# Back button
		self.btn_back = pygame.Rect(28, 646, 120, 46)

		self.turn_context: Optional[TurnContext] = None
		self.final_result: Optional[FinalResult] = None
		self.selected_pit: Optional[int] = None
		self.last_rps: Tuple[str, str] = last_rps or ("rock", "paper")
		self.message = "Chon o hop le, sau do bam nut mui ten de rai quan."

		# animation / display overlay state
		self.anim_active = False
		self.anim_steps: list[int] = []
		self.anim_step_idx = 0
		self.anim_timer = 0.0
		self.anim_interval = 0.10
		self.board_display_seeds = self.engine.board.seeds.copy()

		# confirm-exit modal
		self.confirm_exit = False
		self.confirm_yes = pygame.Rect(520, 420, 120, 48)
		self.confirm_no = pygame.Rect(660, 420, 120, 48)

	def _build_pit_centers(self) -> Dict[int, Tuple[int, int]]:
		if settings.PIT_CENTERS:
			return dict(settings.PIT_CENTERS)

		top_order = [11, 10, 9, 8, 7]
		bottom_order = [1, 2, 3, 4, 5]

		x_start = 320
		x_gap = 160
		top_y = 225
		bottom_y = 505

		centers: Dict[int, Tuple[int, int]] = {
			0: (140, 365),
			6: (1140, 365),
		}
		for i, idx in enumerate(top_order):
			centers[idx] = (x_start + i * x_gap, top_y)
		for i, idx in enumerate(bottom_order):
			centers[idx] = (x_start + i * x_gap, bottom_y)
		return centers

	def _draw_background(self, surface: pygame.Surface) -> None:
		bg_img = self.assets.load_image(
			"background", size=(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
		)
		if bg_img is not None:
			surface.blit(bg_img, (0, 0))
			return
		self._draw_gradient(surface)
	def _draw_avatar(
		self,
		surface: pygame.Surface,
		image_name: str,
		center: Tuple[int, int],
		radius: int = 34,
	) -> None:
		avatar = self.assets.load_image(image_name, size=(radius * 2, radius * 2))
		if avatar is not None:
			rect = avatar.get_rect(center=center)
			surface.blit(avatar, rect)
			return

		pygame.draw.circle(surface, (225, 210, 178), center, radius)
		pygame.draw.circle(surface, settings.BOARD_BORDER, center, radius, 2)

	def _draw_rps_icon(
		self,
		surface: pygame.Surface,
		pick: str,
		center: Tuple[int, int],
		size: int = 44,
	) -> None:
		icon = self.assets.load_image(f"rps_{pick}", size=(size, size))
		if icon is not None:
			rect = icon.get_rect(center=center)
			surface.blit(icon, rect)
			return

		fallback = self.small_font.render(pick[:1].upper(), True, settings.TEXT_PRIMARY)
		surface.blit(fallback, fallback.get_rect(center=center))

	def _prepare_turn_if_needed(self) -> None:
		if self.final_result is not None or self.turn_context is not None:
			return

		if self.engine.is_game_over():
			self.final_result = self.engine.finalize_game()
			return

		context = self.engine.prepare_turn()
		if not context.valid_moves:
			self.message = f"{context.player_name} has no valid pit. Turn skipped."
			self.engine.skip_turn()
			return

		if context.side_was_empty:
			if context.borrowed > 0:
				self.message = (
					f"{context.player_name} had empty side and borrowed "
					f"{context.borrowed} seeds to refill."
				)
			else:
				self.message = f"{context.player_name} refilled from captured seeds."

		self.turn_context = context

	def _is_human_turn(self) -> bool:
		return not isinstance(self.engine.get_active_player(), BotPlayer)

	def _try_apply_human_move(self, direction: int) -> None:
		if self.turn_context is None:
			return
		if self.selected_pit is None:
			self.message = "Please select a pit first."
			return
		if self.selected_pit not in self.turn_context.valid_moves:
			self.message = "Selected pit is not valid for this turn."
			return
		self._apply_move(self.selected_pit, direction)

	def _simulate_distribution_steps(self, pit: int, direction: int) -> list:
		"""Simulate which pits will receive seeds in order without mutating the real board.
		Returns list of pit indices in the distribution order."""
		from game.board import Board
		# local copy
		seeds = self.engine.board.seeds.copy()
		hand = seeds[pit]
		seeds[pit] = 0
		current_idx = pit
		steps: list[int] = []

		while True:
			while hand > 0:
				current_idx = Board.next_index(current_idx, direction)
				seeds[current_idx] += 1
				hand -= 1
				steps.append(current_idx)

			next_idx = Board.next_index(current_idx, direction)

			# if next is quan alive -> stop
			if self.engine.board.is_quan_pit(next_idx) and self.engine.board.has_quan(next_idx):
				break

			# if next has seeds -> pick them up and continue
			if seeds[next_idx] > 0:
				hand = seeds[next_idx]
				seeds[next_idx] = 0
				current_idx = next_idx
				continue

			# otherwise potential capture or stop
			# we record stops but don't mutate further here
			break

		return steps

	def _apply_move(self, pit: int, direction: int) -> None:
		# prepare animation steps from current board
		self.board_display_seeds = self.engine.board.seeds.copy()
		# visually pick up the stones from source
		self.board_display_seeds[pit] = 0
		self.anim_steps = self._simulate_distribution_steps(pit, direction)
		self.anim_step_idx = 0
		self.anim_timer = 0.0
		self.anim_active = True

		# perform logical move immediately so engine state updates
		move = self.engine.execute_move(pit, direction)
		direction_label = "cw" if direction == CLOCKWISE else "ccw"
		self.message = (
			f"{move.player_name} moved pit {move.pit} {direction_label}. "
			f"Captured: {move.captured}."
		)
		self.engine.end_turn()
		self.turn_context = None
		self.selected_pit = None
		if self.engine.is_game_over():
			self.final_result = self.engine.finalize_game()

	def _pit_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
		for idx, center in self.pit_centers.items():
			radius = settings.QUAN_PIT_RADIUS if idx in (0, 6) else settings.SMALL_PIT_RADIUS
			dx = pos[0] - center[0]
			dy = pos[1] - center[1]
			if (dx * dx + dy * dy) <= (radius * radius):
				return idx
		return None

	def handle_event(self, event: pygame.event.Event) -> None:
		if self.final_result is not None:
			return

		# if confirm modal active, handle yes/no clicks
		if self.confirm_exit and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			if self.confirm_yes.collidepoint(event.pos):
				self.app.set_scene(MenuScene(self.app, self.assets))
				return
			if self.confirm_no.collidepoint(event.pos):
				self.confirm_exit = False
				return

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				self.selected_pit = None
			if event.key == pygame.K_c:
				self._try_apply_human_move(CLOCKWISE)
			if event.key == pygame.K_x:
				self._try_apply_human_move(COUNTER_CLOCKWISE)

		if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
			return

		# back button
		if self.btn_back.collidepoint(event.pos):
			# if game in progress ask confirm
			self.confirm_exit = True
			return

		# ignore clicks during animation
		if self.anim_active:
			return

		if self.turn_context is None or not self._is_human_turn():
			return

		mouse_pos = event.pos
		pit = self._pit_at_position(mouse_pos)
		if pit is not None and pit in self.turn_context.valid_moves:
			self.selected_pit = pit
			self.message = f"Selected pit {pit}. Choose direction CW/CCW."
			return

		if self.cw_button.collidepoint(mouse_pos):
			self._try_apply_human_move(COUNTER_CLOCKWISE)
		elif self.ccw_button.collidepoint(mouse_pos):
			self._try_apply_human_move(CLOCKWISE)

	def update(self, dt: float) -> None:
		# animation advance
		if self.anim_active:
			self.anim_timer += dt
			if self.anim_timer >= self.anim_interval and self.anim_step_idx < len(self.anim_steps):
				# apply next step visually
				target = self.anim_steps[self.anim_step_idx]
				self.board_display_seeds[target] += 1
				self.anim_step_idx += 1
				self.anim_timer = 0.0
				# when finished, sync with real board
			if self.anim_step_idx >= len(self.anim_steps):
				self.anim_active = False
				self.board_display_seeds = self.engine.board.seeds.copy()
			return

		if self.final_result is not None:
			return

		self._prepare_turn_if_needed()
		if self.turn_context is None:
			return

		active = self.engine.get_active_player()
		if isinstance(active, BotPlayer):
			pit, direction = active.choose_move(
				self.engine.board.get_state(), self.turn_context.valid_moves
			)
			self._apply_move(pit, direction)

	def _draw_gradient(self, surface: pygame.Surface) -> None:
		for y in range(settings.WINDOW_HEIGHT):
			ratio = y / settings.WINDOW_HEIGHT
			r = int(settings.BG_TOP[0] * (1 - ratio) + settings.BG_BOTTOM[0] * ratio)
			g = int(settings.BG_TOP[1] * (1 - ratio) + settings.BG_BOTTOM[1] * ratio)
			b = int(settings.BG_TOP[2] * (1 - ratio) + settings.BG_BOTTOM[2] * ratio)
			pygame.draw.line(surface, (r, g, b), (0, y), (settings.WINDOW_WIDTH, y))

	def _draw_board(self, surface: pygame.Surface) -> None:
		board_img = self.assets.load_image("board", size=(1100, 520))
		board_rect = pygame.Rect(*settings.BOARD_RECT)
		if board_img is not None:
			surface.blit(board_img, board_rect)
		else:
			pygame.draw.rect(surface, settings.BOARD_COLOR, board_rect, border_radius=28)
			pygame.draw.rect(
				surface,
				settings.BOARD_BORDER,
				board_rect,
				4,
				border_radius=28,
			)

	def _draw_pit(self, surface: pygame.Surface, idx: int, is_valid: bool) -> None:
		center = self.pit_centers[idx]
		is_quan_pit = idx in (0, 6)
		radius = settings.QUAN_PIT_RADIUS if is_quan_pit else settings.SMALL_PIT_RADIUS

		if is_quan_pit:
			pit_img = self.assets.load_image("pit_quan", size=(radius * 2, radius * 2))
		else:
			pit_img = self.assets.load_image("pit_small", size=(radius * 2, radius * 2))

		if pit_img is not None:
			rect = pit_img.get_rect(center=center)
			surface.blit(pit_img, rect)
		else:
			fill_color = settings.PIT_HIGHLIGHT if is_valid else settings.PIT_COLOR
			pygame.draw.circle(surface, fill_color, center, radius)
			pygame.draw.circle(surface, settings.BOARD_BORDER, center, radius, 3)

		if self.selected_pit == idx:
			pygame.draw.circle(surface, settings.PIT_SELECTED, center, radius + 4, 4)

		# use display seeds when animating, otherwise real board
		seed_count = self.board_display_seeds[idx] if self.anim_active else self.engine.board.seeds[idx]
		# only show seed count (no pit index)
		text = self.body_font.render(str(seed_count), True, settings.WHITE)
		text_rect = text.get_rect(center=center)
		shadow = self.body_font.render(str(seed_count), True, (12, 12, 12))
		surface.blit(
			shadow,
			shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2)),
		)
		surface.blit(text, text_rect)

		if is_quan_pit and self.engine.board.has_quan(idx):
			marker = self.small_font.render("Q", True, (255, 240, 120))
			marker_rect = marker.get_rect(center=(center[0], center[1] - radius + 18))
			surface.blit(marker, marker_rect)

	def _draw_circular_arrow_icon(
		self,
		surface: pygame.Surface,
		center: Tuple[int, int],
		clockwise: bool,
		radius: int = 17,
	) -> None:
		"""Draw a true circular arrow by drawing an arc and an arrow head."""
		if clockwise:
			angles = list(range(230, -40, -18))
		else:
			angles = list(range(-50, 230, 18))

		points = []
		for ang in angles:
			rad = math.radians(ang)
			x = int(center[0] + radius * math.cos(rad))
			y = int(center[1] + radius * math.sin(rad))
			points.append((x, y))

		if len(points) >= 2:
			pygame.draw.lines(surface, settings.WHITE, False, points, 4)
			tip = points[-1]
			prev = points[-2]
			theta = math.atan2(tip[1] - prev[1], tip[0] - prev[0])
			left = (
				int(tip[0] - 9 * math.cos(theta - 0.6)),
				int(tip[1] - 9 * math.sin(theta - 0.6)),
			)
			right = (
				int(tip[0] - 9 * math.cos(theta + 0.6)),
				int(tip[1] - 9 * math.sin(theta + 0.6)),
			)
			pygame.draw.polygon(surface, settings.WHITE, [tip, left, right])

	def _draw_buttons(self, surface: pygame.Surface) -> None:
		mouse_pos = pygame.mouse.get_pos()
		
		# Draw CW button (clockwise arrow)
		cw_center = (self.cw_button.centerx, self.cw_button.centery)
		is_cw_hover = self.cw_button.collidepoint(mouse_pos)
		bg_cw = (52, 168, 84) if is_cw_hover else (39, 148, 72)
		pygame.draw.circle(surface, (18, 18, 18), (cw_center[0] + 4, cw_center[1] + 4), 34)
		pygame.draw.circle(surface, bg_cw, cw_center, 32)
		pygame.draw.circle(surface, (95, 205, 120), (cw_center[0], cw_center[1] - 8), 18)
		pygame.draw.circle(surface, settings.WHITE, cw_center, 32, 2)
		self._draw_circular_arrow_icon(surface, cw_center, clockwise=True)
		
		# Draw CCW button (counter-clockwise arrow)
		ccw_center = (self.ccw_button.centerx, self.ccw_button.centery)
		is_ccw_hover = self.ccw_button.collidepoint(mouse_pos)
		bg_ccw = (52, 168, 84) if is_ccw_hover else (39, 148, 72)
		pygame.draw.circle(surface, (18, 18, 18), (ccw_center[0] + 4, ccw_center[1] + 4), 34)
		pygame.draw.circle(surface, bg_ccw, ccw_center, 32)
		pygame.draw.circle(surface, (95, 205, 120), (ccw_center[0], ccw_center[1] - 8), 18)
		pygame.draw.circle(surface, settings.WHITE, ccw_center, 32, 2)
		self._draw_circular_arrow_icon(surface, ccw_center, clockwise=False)

		# draw back button
		back_bg = (154, 98, 63) if self.btn_back.collidepoint(mouse_pos) else (140, 90, 60)
		shadow = self.btn_back.move(4, 4)
		pygame.draw.rect(surface, (18, 18, 18), shadow, border_radius=12)
		pygame.draw.rect(surface, back_bg, self.btn_back, border_radius=12)
		pygame.draw.rect(surface, settings.WHITE, self.btn_back, 2, border_radius=12)
		back_text = self.small_font.render("Back", True, settings.WHITE)
		surface.blit(back_text, back_text.get_rect(center=self.btn_back.center))

	def _draw_hud(self, surface: pygame.Surface) -> None:
		# Top information panel to avoid text/background clash
		top_panel = pygame.Surface((790, 116), pygame.SRCALPHA)
		top_panel.fill((20, 18, 16, 156))
		surface.blit(top_panel, (20, 16))
		pygame.draw.rect(surface, (248, 236, 208), pygame.Rect(20, 16, 790, 116), 1, border_radius=10)

		title_surf = self.title_font.render("O AN QUAN", True, (255, 244, 224))
		surface.blit(title_surf, (36, 22))

		names = self.engine.get_player_names()
		capt = self.engine.captured_by_player
		borrow = self.engine.borrowed_by_player
		active_name = self.engine.get_active_player().name

		player_line = self.body_font.render(
			f"P1: {names[0]}  |  P2: {names[1]}  |  Turn: {active_name}",
			True,
			(252, 244, 228),
		)
		surface.blit(player_line, (36, 74))

		score_line = self.small_font.render(
			f"Captured: {capt[0]} - {capt[1]}    Borrowed: {borrow[0]} - {borrow[1]}",
			True,
			(245, 231, 205),
		)
		surface.blit(score_line, (36, 102))

		# Bottom status panel kept clear from buttons
		bottom_panel = pygame.Surface((740, 72), pygame.SRCALPHA)
		bottom_panel.fill((20, 18, 16, 156))
		surface.blit(bottom_panel, (164, 632))
		pygame.draw.rect(surface, (248, 236, 208), pygame.Rect(164, 632, 740, 72), 1, border_radius=10)

		message = self.small_font.render(self.message[:92], True, (255, 246, 230))
		surface.blit(message, (180, 648))

		hint = self.small_font.render(
			"Esc: bo chon o | Back: ve menu | Mui ten: rai theo chieu",
			True,
			(235, 222, 194),
		)
		surface.blit(hint, (180, 674))

		# avatar mapping: prefer provided player images
		avatar_0_name = "player_1"
		if isinstance(self.engine.players[1], BotPlayer):
			avatar_1_name = "bot1"
		else:
			avatar_1_name = "player_2"
		self._draw_avatar(surface, avatar_0_name, (1080, 58))
		self._draw_avatar(surface, avatar_1_name, (1170, 58))

		name_0 = self.small_font.render(names[0], True, (255, 246, 230))
		name_1 = self.small_font.render(names[1], True, (255, 246, 230))
		surface.blit(name_0, name_0.get_rect(center=(1080, 102)))
		surface.blit(name_1, name_1.get_rect(center=(1170, 102)))

		self._draw_rps_icon(surface, self.last_rps[0], (1080, 132), size=36)
		self._draw_rps_icon(surface, self.last_rps[1], (1170, 132), size=36)

	def _draw_final_overlay(self, surface: pygame.Surface) -> None:
		if self.final_result is None:
			return

		overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 130))
		surface.blit(overlay, (0, 0))

		panel = pygame.Rect(330, 210, 620, 300)
		pygame.draw.rect(surface, (255, 248, 230), panel, border_radius=20)
		pygame.draw.rect(surface, settings.BOARD_BORDER, panel, 3, border_radius=20)

		scores = self.final_result.scores
		names = self.final_result.names
		result_title = self.head_font.render("Final Result", True, settings.TEXT_PRIMARY)
		surface.blit(result_title, (panel.x + 230, panel.y + 24))

		line_1 = self.body_font.render(
			f"{names[0]}: {scores[0]} points",
			True,
			settings.TEXT_PRIMARY,
		)
		line_2 = self.body_font.render(
			f"{names[1]}: {scores[1]} points",
			True,
			settings.TEXT_PRIMARY,
		)
		surface.blit(line_1, (panel.x + 120, panel.y + 110))
		surface.blit(line_2, (panel.x + 120, panel.y + 150))

		if scores[0] > scores[1]:
			winner_text = f"Winner: {names[0]}"
		elif scores[1] > scores[0]:
			winner_text = f"Winner: {names[1]}"
		else:
			winner_text = "Draw"

		winner = self.head_font.render(winner_text, True, (180, 65, 32))
		surface.blit(winner, (panel.x + 190, panel.y + 215))

	def draw(self, surface: pygame.Surface) -> None:
		self._draw_background(surface)
		self._draw_board(surface)

		valid_moves = set(self.turn_context.valid_moves) if self.turn_context else set()
		for idx in [0, 11, 10, 9, 8, 7, 6, 1, 2, 3, 4, 5]:
			is_valid = self._is_human_turn() and idx in valid_moves
			self._draw_pit(surface, idx, is_valid)

		self._draw_buttons(surface)
		self._draw_hud(surface)
		# confirm exit modal
		if self.confirm_exit:
			overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
			overlay.fill((0, 0, 0, 150))
			surface.blit(overlay, (0, 0))
			panel = pygame.Rect(360, 300, 560, 200)
			pygame.draw.rect(surface, (255, 248, 230), panel, border_radius=12)
			pygame.draw.rect(surface, settings.BOARD_BORDER, panel, 3, border_radius=12)
			q = self.head_font.render("Return to menu?", True, settings.TEXT_PRIMARY)
			surface.blit(q, (panel.x + 160, panel.y + 28))
			desc = self.body_font.render("Are you sure you want to quit the current game?", True, settings.TEXT_PRIMARY)
			surface.blit(desc, (panel.x + 40, panel.y + 84))
			# yes/no buttons
			pygame.draw.rect(surface, (88, 140, 72), self.confirm_yes, border_radius=8)
			pygame.draw.rect(surface, (180, 60, 60), self.confirm_no, border_radius=8)
			y = self.small_font.render("Yes", True, settings.WHITE)
			n = self.small_font.render("No", True, settings.WHITE)
			surface.blit(y, y.get_rect(center=self.confirm_yes.center))
			surface.blit(n, n.get_rect(center=self.confirm_no.center))

		self._draw_final_overlay(surface)
