"""Name input scene for pygame UI."""

from __future__ import annotations

import pygame

from config import PLAYER_NAMES
from game.ui.pygame_ui.assets import AssetManager
from game.ui.pygame_ui.scenes.base_scene import BaseScene
from game.ui.pygame_ui.scenes.rps_scene import RpsScene
from game.ui.pygame_ui.widgets import Button, TextInput
from game.ui.pygame_ui import settings


class NameInputScene(BaseScene):
	def __init__(
		self,
		app: "PygameApp",
		assets: AssetManager,
		mode: str,
	) -> None:
		self.app = app
		self.assets = assets
		self.mode = mode

		self.title_font = pygame.font.SysFont("tahoma", 48, bold=True)
		self.head_font = pygame.font.SysFont("tahoma", 28, bold=True)
		self.label_font = pygame.font.SysFont("tahoma", 22, bold=True)
		self.body_font = pygame.font.SysFont("segoeui", 22)
		self.small_font = pygame.font.SysFont("segoeui", 18)

		# Input for player 1
		self.input_p1 = TextInput(
			pygame.Rect(420, 280, 440, 46),
			self.body_font,
			"Người chơi 1",
		)
		self.input_p1.set_text(PLAYER_NAMES[0])

		# Input for player 2 (only visible in PvP mode)
		self.input_p2 = TextInput(
			pygame.Rect(420, 360, 440, 46),
			self.body_font,
			"Đối thủ" if mode == "pvb" else "Người chơi 2",
		)
		if mode == "pvp":
			self.input_p2.set_text(PLAYER_NAMES[1])

		# Buttons
		self.btn_back = Button(
			pygame.Rect(28, 646, 120, 46),
			"Quay lại",
			self.small_font,
			(140, 90, 60),
			(154, 98, 63),
			settings.WHITE,
			settings.WHITE,
		)
		self.btn_start = Button(
			pygame.Rect(1120, 646, 120, 46),
			"Bắt đầu",
			self.small_font,
			settings.BUTTON_BG,
			settings.BUTTON_BG_HOVER,
			settings.BUTTON_TEXT,
			settings.WHITE,
		)

	def _draw_gradient(self, surface: pygame.Surface) -> None:
		for y in range(settings.WINDOW_HEIGHT):
			ratio = y / settings.WINDOW_HEIGHT
			r = int(settings.BG_TOP[0] * (1 - ratio) + settings.BG_BOTTOM[0] * ratio)
			g = int(settings.BG_TOP[1] * (1 - ratio) + settings.BG_BOTTOM[1] * ratio)
			b = int(settings.BG_TOP[2] * (1 - ratio) + settings.BG_BOTTOM[2] * ratio)
			pygame.draw.line(surface, (r, g, b), (0, y), (settings.WINDOW_WIDTH, y))

	def _draw_background(self, surface: pygame.Surface) -> None:
		bg_img = self.assets.load_image("background", size=(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
		if bg_img is not None:
			surface.blit(bg_img, (0, 0))
		else:
			self._draw_gradient(surface)

	def _draw_title(self, surface: pygame.Surface, text: str) -> None:
		outline_color = (58, 126, 72)
		for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
			outline = self.title_font.render(text, True, outline_color)
			surface.blit(outline, outline.get_rect(center=(settings.WINDOW_WIDTH // 2 + dx, 140 + dy)))
		title = self.title_font.render(text, True, settings.WHITE)
		surface.blit(title, title.get_rect(center=(settings.WINDOW_WIDTH // 2, 140)))

	def _draw_outlined_label(
		self,
		surface: pygame.Surface,
		text: str,
		pos: tuple[int, int],
		color: tuple[int, int, int] = (250, 246, 238),
		outline: tuple[int, int, int] = (36, 26, 18),
	) -> None:
		# Thin outline to keep labels readable on light backgrounds.
		for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
			shadow = self.label_font.render(text, True, outline)
			surface.blit(shadow, (pos[0] + dx, pos[1] + dy))
		label = self.label_font.render(text, True, color)
		surface.blit(label, pos)

	def _start_game(self) -> None:
		p1_name = self.input_p1.text.strip() or PLAYER_NAMES[0]
		p2_name = self.input_p2.text.strip() or ("Bot" if self.mode == "pvb" else PLAYER_NAMES[1])

		# If PvB, go to BotSelectScene to choose bot AI mode
		if self.mode == "pvb":
			from game.ui.pygame_ui.scenes.bot_select_scene import BotSelectScene
			self.app.set_scene(BotSelectScene(self.app, self.assets, self.mode, p1_name, p2_name))
			return

		# If PvP, go directly to RpsScene
		self.app.set_scene(
			RpsScene(self.app, self.assets, self.mode, p1_name, p2_name)
		)

	def handle_event(self, event: pygame.event.Event) -> None:
		self.input_p1.handle_event(event)
		if self.mode == "pvp":
			self.input_p2.handle_event(event)

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			if self.btn_back.is_clicked(event):
				from game.ui.pygame_ui.scenes.menu_scene import MenuScene
				self.app.set_scene(MenuScene(self.app, self.assets))
				return
			if self.btn_start.is_clicked(event):
				self._start_game()
				return

	def update(self, dt: float) -> None:
		_ = dt

	def draw(self, surface: pygame.Surface) -> None:
		self._draw_background(surface)

		title = "Tên người chơi" if self.mode == "pvp" else "Chọn đối thủ"
		self._draw_title(surface, title)

		# Label and input for player 1
		self._draw_outlined_label(surface, "Người chơi 1", (420, 250))
		self.input_p1.draw(
			surface,
			(236, 226, 206),
			settings.INPUT_BORDER,
			settings.INPUT_BORDER_ACTIVE,
			(18, 18, 18),
			(96, 86, 72),
		)

		# Label and input for player 2 are only shown in PvP mode.
		if self.mode == "pvp":
			self._draw_outlined_label(surface, "Người chơi 2", (420, 330))
			self.input_p2.draw(
				surface,
				(236, 226, 206),
				settings.INPUT_BORDER,
				settings.INPUT_BORDER_ACTIVE,
				(18, 18, 18),
				(96, 86, 72),
			)
		else:
			self._draw_outlined_label(surface, "Đối thủ bot", (420, 330))

		# Buttons
		self.btn_back.draw(surface)
		self.btn_start.draw(surface)
