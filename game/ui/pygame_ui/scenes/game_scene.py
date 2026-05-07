"""Scene chơi chính cho giao diện pygame."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import pygame

from config import CLOCKWISE, COUNTER_CLOCKWISE
from game.board import Board
from game.engine import GameEngine, FinalResult, TurnContext
from game.players.bot_player import BotPlayer
from game.ui.pygame_ui.assets import AssetManager
from game.ui.pygame_ui.scenes.base_scene import BaseScene
from game.ui.pygame_ui.scenes.menu_scene import MenuScene
from game.ui.pygame_ui import settings


class GameScene(BaseScene):
	BOT_AVATAR_MAP = {
		"random": "bot1",
		"greedy": "bot2",
		"minimax": "bot3",
	}

	def __init__(
		self,
		app: "PygameApp",
		engine: GameEngine,
		assets: AssetManager,
		last_rps: Tuple[str, str] | None = None,
		bot_type: str = "random",
	) -> None:
		self.app = app
		self.engine = engine
		self.assets = assets

		self.title_font = pygame.font.SysFont("tahoma", 40, bold=True)
		self.head_font = pygame.font.SysFont("tahoma", 28, bold=True)
		self.name_font = pygame.font.SysFont("tahoma", 20, bold=True)
		self.body_font = pygame.font.SysFont("segoeui", 22)
		self.small_font = pygame.font.SysFont("segoeui", 18)

		self.pit_centers = self._build_pit_centers()
		# Circular buttons for CW/CCW arrows (positions swapped: right arrow on the right)
		self.cw_button = pygame.Rect(1016, 636, 68, 68)
		self.ccw_button = pygame.Rect(930, 636, 68, 68)

		# Back button
		self.btn_back = pygame.Rect(28, 646, 120, 46)

		self.turn_context: Optional[TurnContext] = None
		self.final_result: Optional[FinalResult] = None
		self.selected_pit: Optional[int] = None
		self.last_rps: Tuple[str, str] = last_rps or ("rock", "paper")
		self.message = "Hãy chọn ô hợp lệ rồi bấm nút mũi tên để rải quân."
		self.bot_type = bot_type if bot_type in self.BOT_AVATAR_MAP else "random"
		self.bot_avatar_name = self.BOT_AVATAR_MAP[self.bot_type]
		self.bot_border_color = {
			"random": (58, 126, 72),
			"greedy": (54, 103, 166),
			"minimax": (170, 62, 62),
		}[self.bot_type]

		# animation / display overlay state
		self.anim_active = False
		self.anim_frames: list[Board] = []
		self.anim_frame_idx = 0
		self.anim_timer = 0.0
		self.anim_interval = 0.35
		self.display_board: Board = self.engine.board.copy()

		# bot selection display state
		self.bot_selected_pit: Optional[int] = None
		self.bot_selected_direction: Optional[int] = None
		self.bot_select_timer = 0.0
		self.bot_select_delay = 0.35

		# confirm-exit modal
		self.confirm_exit = False
		self.confirm_yes = pygame.Rect(520, 420, 120, 48)
		self.confirm_no = pygame.Rect(660, 420, 120, 48)
		self.final_back_button = pygame.Rect(565, 485, 150, 44)

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
		border_color: Tuple[int, int, int] | None = None,
	) -> None:
		border = border_color or settings.BOARD_BORDER
		pygame.draw.circle(surface, settings.WHITE, center, radius)
		pygame.draw.circle(surface, border, center, radius, 4)
		avatar = self.assets.load_image(image_name, size=(radius * 2 - 12, radius * 2 - 12))
		if avatar is not None:
			rect = avatar.get_rect(center=center)
			surface.blit(avatar, rect)
			return

		fallback = self.small_font.render(image_name[:1].upper(), True, settings.TEXT_PRIMARY)
		surface.blit(fallback, fallback.get_rect(center=center))

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
			self.message = f"{context.player_name} không có ô hợp lệ. Bỏ lượt."
			self.engine.skip_turn()
			return

		if context.side_was_empty:
			if context.borrowed > 0:
				self.message = (
					f"{context.player_name} có bên trống và đã mượn "
					f"{context.borrowed} quân để bù lại."
				)
			else:
				self.message = f"{context.player_name} được bù lại từ quân đã ăn."

		self.turn_context = context

	def _is_human_turn(self) -> bool:
		return not isinstance(self.engine.get_active_player(), BotPlayer)

	def _try_apply_human_move(self, direction: int) -> None:
		if self.turn_context is None:
			return
		if self.selected_pit is None:
			self.message = "Hãy chọn một ô trước."
			return
		if self.selected_pit not in self.turn_context.valid_moves:
			self.message = "Ô đã chọn không hợp lệ ở lượt này."
			return
		self._apply_move(self.selected_pit, direction)

	def _build_animation_frames(self, pit: int, direction: int) -> list[Board]:
		"""Build board snapshots that exactly mirror the engine move flow."""
		from game.board import Board

		board = self.engine.board.copy()
		frames: list[Board] = []

		def can_capture_target(target_idx: int) -> bool:
			if board.is_quan_pit(target_idx) and board.has_quan(target_idx):
				return board.seeds[target_idx] >= 5
			return board.seeds[target_idx] > 0

		def capture_target(target_idx: int) -> None:
			board.seeds[target_idx] = 0
			if board.is_quan_pit(target_idx) and board.has_quan(target_idx):
				board.remove_quan(target_idx)

		hand = board.clear_pit(pit)
		current_idx = pit

		while True:
			while hand > 0:
				current_idx = Board.next_index(current_idx, direction)
				board.seeds[current_idx] += 1
				hand -= 1
				frames.append(board.copy())

			next_idx = Board.next_index(current_idx, direction)

			if board.is_quan_pit(next_idx) and board.has_quan(next_idx):
				break

			if board.seeds[next_idx] > 0:
				hand = board.clear_pit(next_idx)
				frames.append(board.copy())
				current_idx = next_idx
				continue

			target_idx = Board.next_index(next_idx, direction)
			if can_capture_target(target_idx):
				while can_capture_target(target_idx):
					capture_target(target_idx)
					frames.append(board.copy())

					empty_idx = Board.next_index(target_idx, direction)
					next_target_idx = Board.next_index(empty_idx, direction)

					if board.seeds[empty_idx] != 0 or board.has_quan(empty_idx):
						break
					if not can_capture_target(next_target_idx):
						break
					target_idx = next_target_idx

			break

		if not frames:
			frames.append(board.copy())
		return frames

	def _apply_move(self, pit: int, direction: int) -> None:
		# prepare animation steps from current board
		self.display_board = self.engine.board.copy()
		self.display_board.clear_pit(pit)
		self.anim_frames = self._build_animation_frames(pit, direction)
		self.anim_frame_idx = 0
		self.anim_timer = 0.0
		self.anim_active = True

		# perform logical move immediately so engine state updates
		move = self.engine.execute_move(pit, direction)
		direction_label = "xuôi chiều" if direction == CLOCKWISE else "ngược chiều"
		self.message = (
			f"{move.player_name} đi ô {move.pit} theo hướng {direction_label}. "
			f"Đã ăn: {move.captured}."
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
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if self.final_back_button.collidepoint(event.pos):
					self.app.set_scene(MenuScene(self.app, self.assets))
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
			if self.anim_timer >= self.anim_interval and self.anim_frame_idx < len(self.anim_frames):
				self.display_board = self.anim_frames[self.anim_frame_idx].copy()
				self.anim_frame_idx += 1
				self.anim_timer = 0.0
			if self.anim_frame_idx >= len(self.anim_frames):
				self.anim_active = False
			return

		# bot selection display (show red circle on selected pit for 0.35s before moving)
		if self.bot_selected_pit is not None:
			self.bot_select_timer += dt
			if self.bot_select_timer >= self.bot_select_delay:
				direction = self.bot_selected_direction
				if direction is None:
					self.bot_selected_pit = None
					self.bot_select_timer = 0.0
					return
				# now apply the move
				self._apply_move(self.bot_selected_pit, direction)
				self.bot_selected_pit = None
				self.bot_selected_direction = None
				self.bot_select_timer = 0.0
			return

		if self.final_result is not None:
			return

		self._prepare_turn_if_needed()
		if self.turn_context is None:
			return

		active = self.engine.get_active_player()
		if isinstance(active, BotPlayer):
			# give the strategy access to captured/borrowed totals
			board_state = self.engine.board.get_state()
			board_state["captured_by_player"] = self.engine.captured_by_player.copy()
			board_state["borrowed_by_player"] = self.engine.borrowed_by_player.copy()
			pit, direction = active.choose_move(board_state, self.turn_context.valid_moves)
			# Instead of applying move immediately, set bot selection state
			self.bot_selected_pit = pit
			self.bot_selected_direction = direction
			self.bot_select_timer = 0.0
			self.message = f"Bot đã chọn ô {pit}."

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

	def _pick_pit_image_name(self, board: Board, idx: int, seed_count: int) -> Optional[str]:
		is_quan_pit = idx in (0, 6)
		if is_quan_pit:
			has_quan = board.has_quan(idx)
			if seed_count <= 0 and not has_quan:
				return None
			seed_key = max(0, min(seed_count, 15))
			quan_key = 1 if has_quan else 0
			return f"{quan_key}_pit_quan_{seed_key}_pit_small"

		if seed_count <= 0:
			return None
		seed_key = max(1, min(seed_count, 15))
		return f"{seed_key}_pit_small"

	def _draw_pit(self, surface: pygame.Surface, idx: int, is_valid: bool) -> None:
		center = self.pit_centers[idx]
		is_quan_pit = idx in (0, 6)
		radius = settings.QUAN_PIT_RADIUS if is_quan_pit else settings.SMALL_PIT_RADIUS
		board = self.display_board if self.anim_active else self.engine.board
		seed_count = board.seeds[idx]
		pit_image_name = self._pick_pit_image_name(board, idx, seed_count)

		pit_img = None
		if pit_image_name is not None:
			pit_img = self.assets.load_image(pit_image_name, size=(radius * 2, radius * 2))
			# Fallback to the old base pit image if a specific sprite is missing.
			if pit_img is None:
				fallback_name = "pit_quan" if is_quan_pit else "pit_small"
				pit_img = self.assets.load_image(fallback_name, size=(radius * 2, radius * 2))

		if pit_img is not None:
			rect = pit_img.get_rect(center=center)
			surface.blit(pit_img, rect)
		elif pit_image_name is not None:
			fill_color = settings.PIT_HIGHLIGHT if is_valid else settings.PIT_COLOR
			pygame.draw.circle(surface, fill_color, center, radius)
			pygame.draw.circle(surface, settings.BOARD_BORDER, center, radius, 3)

		# Draw red circle for player selection
		if self.selected_pit == idx:
			pygame.draw.circle(surface, settings.PIT_SELECTED, center, radius + 4, 4)

		# Draw red circle for bot selection
		if self.bot_selected_pit == idx:
			pygame.draw.circle(surface, settings.PIT_SELECTED, center, radius + 4, 4)

		# only show seed count (no pit index)
		text = self.body_font.render(str(seed_count), True, settings.WHITE)
		text_rect = text.get_rect(center=center)
		shadow = self.body_font.render(str(seed_count), True, (12, 12, 12))
		surface.blit(
			shadow,
			shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2)),
		)
		surface.blit(text, text_rect)

		if is_quan_pit and board.has_quan(idx):
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
		"""Draw a simple left/right arrow icon."""
		if clockwise:
			shaft_start = (center[0] - radius + 3, center[1])
			shaft_end = (center[0] + radius - 4, center[1])
			head_tip = (center[0] + radius, center[1])
			head_left = (center[0] + radius - 7, center[1] - 6)
			head_right = (center[0] + radius - 7, center[1] + 6)
		else:
			shaft_start = (center[0] + radius - 3, center[1])
			shaft_end = (center[0] - radius + 4, center[1])
			head_tip = (center[0] - radius, center[1])
			head_left = (center[0] - radius + 7, center[1] - 6)
			head_right = (center[0] - radius + 7, center[1] + 6)

		pygame.draw.line(surface, settings.WHITE, shaft_start, shaft_end, 4)
		pygame.draw.polygon(surface, settings.WHITE, [head_tip, head_left, head_right])

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
		back_text = self.small_font.render("Quay lại", True, settings.WHITE)
		surface.blit(back_text, back_text.get_rect(center=self.btn_back.center))

	def _draw_hud(self, surface: pygame.Surface) -> None:
		names = self.engine.get_player_names()
		capt = self.engine.captured_by_player
		borrow = self.engine.borrowed_by_player
		is_bot_game = isinstance(self.engine.players[1], BotPlayer)
		right_avatar_name = self.bot_avatar_name if is_bot_game else "player_2"
		right_avatar_radius = 48 if is_bot_game else 42
		right_avatar_border = self.bot_border_color if is_bot_game else (110, 73, 45)

		panel_rect = pygame.Rect(120, 18, 1040, 160)
		panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
		panel.fill((74, 51, 30, 176))
		surface.blit(panel, panel_rect.topleft)
		pygame.draw.rect(surface, (246, 236, 210), panel_rect, 2, border_radius=18)

		score_text = self.head_font.render(f"{capt[0]} - {capt[1]}", True, settings.WHITE)
		borrow_text = self.small_font.render(
			f"Mượn: {borrow[0]} - {borrow[1]}",
			True,
			settings.TEXT_MUTED,
		)

		surface.blit(score_text, score_text.get_rect(center=(panel_rect.centerx, panel_rect.centery - 10)))
		surface.blit(borrow_text, borrow_text.get_rect(center=(panel_rect.centerx, panel_rect.centery + 28)))

		left_avatar_center = (panel_rect.centerx - 220, panel_rect.centery - 4)
		right_avatar_center = (panel_rect.centerx + 220, panel_rect.centery - 4)
		self._draw_avatar(surface, "player_1", left_avatar_center, radius=42, border_color=(110, 73, 45))
		self._draw_avatar(surface, right_avatar_name, right_avatar_center, radius=right_avatar_radius, border_color=right_avatar_border)

		left_name = self.name_font.render(names[0], True, settings.WHITE)
		right_name = self.name_font.render(names[1], True, settings.WHITE)
		surface.blit(left_name, left_name.get_rect(midtop=(left_avatar_center[0], left_avatar_center[1] + 42)))
		surface.blit(right_name, right_name.get_rect(midtop=(right_avatar_center[0], right_avatar_center[1] + 42)))

		# Bottom status panel kept clear from buttons
		bottom_panel = pygame.Surface((740, 72), pygame.SRCALPHA)
		bottom_panel.fill((20, 18, 16, 156))
		surface.blit(bottom_panel, (164, 632))
		pygame.draw.rect(surface, (248, 236, 208), pygame.Rect(164, 632, 740, 72), 1, border_radius=10)

		message = self.small_font.render(self.message[:92], True, settings.WHITE)
		surface.blit(message, (180, 648))

		hint = self.small_font.render(
			"Esc: bỏ chọn ô | Quay lại: về menu | Mũi tên: rải theo chiều",
			True,
			settings.TEXT_MUTED,
		)
		surface.blit(hint, (180, 674))

	def _draw_final_overlay(self, surface: pygame.Surface) -> None:
		if self.final_result is None:
			return

		overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 130))
		surface.blit(overlay, (0, 0))

		panel = pygame.Rect(330, 210, 620, 330)
		pygame.draw.rect(surface, (255, 248, 230), panel, border_radius=20)
		pygame.draw.rect(surface, settings.BOARD_BORDER, panel, 3, border_radius=20)

		scores = self.final_result.scores
		names = self.final_result.names
		result_title = self.head_font.render("Final Result", True, (0, 0, 0))
		surface.blit(result_title, (panel.x + 230, panel.y + 24))

		line_1 = self.body_font.render(
			f"{names[0]}: {scores[0]} points",
			True,
			(0, 0, 0),
		)
		line_2 = self.body_font.render(
			f"{names[1]}: {scores[1]} points",
			True,
			(0, 0, 0),
		)
		surface.blit(line_1, (panel.x + 120, panel.y + 110))
		surface.blit(line_2, (panel.x + 120, panel.y + 150))

		if scores[0] > scores[1]:
			winner_text = f"Winner: {names[0]}"
		elif scores[1] > scores[0]:
			winner_text = f"Winner: {names[1]}"
		else:
			winner_text = "Draw"

		winner = self.head_font.render(winner_text, True, (220, 70, 40))
		surface.blit(winner, winner.get_rect(center=(panel.centerx, panel.y + 240)))

		mouse_pos = pygame.mouse.get_pos()
		btn_bg = (154, 98, 63) if self.final_back_button.collidepoint(mouse_pos) else (140, 90, 60)
		btn_shadow = self.final_back_button.move(3, 3)
		pygame.draw.rect(surface, (18, 18, 18), btn_shadow, border_radius=10)
		pygame.draw.rect(surface, btn_bg, self.final_back_button, border_radius=10)
		pygame.draw.rect(surface, settings.WHITE, self.final_back_button, 2, border_radius=10)
		btn_text = self.small_font.render("Về menu", True, settings.WHITE)
		surface.blit(btn_text, btn_text.get_rect(center=self.final_back_button.center))

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
			q = self.head_font.render("Về menu?", True, (0, 0, 0))
			surface.blit(q, q.get_rect(center=(panel.centerx, panel.y + 28)))
			desc = self.body_font.render("Bạn có chắc muốn thoát ván hiện tại không?", True, (0, 0, 0))
			surface.blit(desc, desc.get_rect(center=(panel.centerx, panel.y + 84)))
			# yes/no buttons
			pygame.draw.rect(surface, (88, 140, 72), self.confirm_yes, border_radius=8)
			pygame.draw.rect(surface, (180, 60, 60), self.confirm_no, border_radius=8)
			y = self.small_font.render("Yes", True, settings.WHITE)
			n = self.small_font.render("No", True, settings.WHITE)
			surface.blit(y, y.get_rect(center=self.confirm_yes.center))
			surface.blit(n, n.get_rect(center=self.confirm_no.center))

		# Only show victory when animation completes
		if not self.anim_active:
			self._draw_final_overlay(surface)
