"""Menu scene for pygame UI."""

from __future__ import annotations

from typing import Tuple

import pygame

from config import PLAYER_NAMES
from game.engine import GameEngine
from game.ui.pygame_ui.assets import AssetManager
from game.ui.pygame_ui.scenes.base_scene import BaseScene
from game.ui.pygame_ui.scenes.rps_scene import RpsScene
from game.ui.pygame_ui.widgets import Button, TextInput
from game.ui.pygame_ui import settings


class MenuScene(BaseScene):
	def __init__(self, app: "PygameApp", assets: AssetManager) -> None:
		self.app = app
		self.assets = assets

		self.title_font = pygame.font.SysFont("georgia", 56, bold=True)
		self.head_font = pygame.font.SysFont("cambria", 28, bold=True)
		self.body_font = pygame.font.SysFont("segoeui", 22)
		self.small_font = pygame.font.SysFont("segoeui", 18)

		self.mode = "pvp"
		self.step = "menu"

		# Main menu buttons - directly start game
		self.btn_pvp = Button(
			pygame.Rect(440, 280, 400, 60),
			"Chơi với Bạn bè",
			self.head_font,
			settings.BUTTON_BG,
			settings.BUTTON_BG_HOVER,
			settings.BUTTON_TEXT,
			settings.WHITE,
		)
		self.btn_pvb = Button(
			pygame.Rect(440, 360, 400, 60),
			"Chơi với Máy",
			self.head_font,
			settings.BUTTON_BG,
			settings.BUTTON_BG_HOVER,
			settings.BUTTON_TEXT,
			settings.WHITE,
		)
		self.btn_quit = Button(
			pygame.Rect(440, 440, 400, 60),
			"Thoát",
			self.head_font,
			(160, 70, 60),
			(190, 84, 74),
			settings.WHITE,
			settings.WHITE,
		)

		self.btn_back = Button(
			pygame.Rect(360, 560, 220, 48),
			"Back",
			self.body_font,
			settings.BUTTON_BG,
			settings.BUTTON_BG_HOVER,
			settings.BUTTON_TEXT,
			settings.WHITE,
		)
		self.btn_start = Button(
			pygame.Rect(700, 560, 220, 48),
			"Start",
			self.body_font,
			settings.BUTTON_BG,
			settings.BUTTON_BG_HOVER,
			settings.BUTTON_TEXT,
			settings.WHITE,
		)

		self.input_p1 = TextInput(
			pygame.Rect(420, 330, 440, 46),
			self.body_font,
			"Player 1",
		)
		self.input_p2 = TextInput(
			pygame.Rect(420, 400, 440, 46),
			self.body_font,
			"Player 2",
		)

		self._apply_default_names()

	def _apply_default_names(self) -> None:
		self.input_p1.set_text(PLAYER_NAMES[0])
		self.input_p2.set_text(PLAYER_NAMES[1])

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
		title = self.title_font.render(text, True, settings.TEXT_PRIMARY)
		surface.blit(title, title.get_rect(center=(settings.WINDOW_WIDTH // 2, 140)))

	def _draw_menu(self, surface: pygame.Surface) -> None:
		# Bright centered title with soft glow so it does not sink into the background.
		title_center = (settings.WINDOW_WIDTH // 2, 180)
		glow = self.title_font.render("O ĂN QUAN", True, (55, 40, 20))
		for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)]:
			surface.blit(glow, glow.get_rect(center=(title_center[0] + dx, title_center[1] + dy)))

		title = self.title_font.render("O ĂN QUAN", True, (255, 248, 232))
		surface.blit(title, title.get_rect(center=title_center))

		self.btn_pvp.draw(surface)
		self.btn_pvb.draw(surface)
		self.btn_quit.draw(surface)

	def _draw_name_entry(self, surface: pygame.Surface) -> None:
		title = "Player Names" if self.mode == "pvp" else "Player and Bot"
		self._draw_title(surface, title)

		label_1 = self.small_font.render("Player 1", True, settings.TEXT_MUTED)
		surface.blit(label_1, (420, 305))
		self.input_p1.draw(
			surface,
			settings.INPUT_BG,
			settings.INPUT_BORDER,
			settings.INPUT_BORDER_ACTIVE,
			settings.TEXT_PRIMARY,
			settings.TEXT_MUTED,
		)

		label_2 = self.small_font.render(
			"Player 2" if self.mode == "pvp" else "Bot",
			True,
			settings.TEXT_MUTED,
		)
		surface.blit(label_2, (420, 375))
		self.input_p2.draw(
			surface,
			settings.INPUT_BG,
			settings.INPUT_BORDER,
			settings.INPUT_BORDER_ACTIVE,
			settings.TEXT_PRIMARY,
			settings.TEXT_MUTED,
		)

		self.btn_back.draw(surface)
		self.btn_start.draw(surface)

	def _apply_mode(self, mode: str) -> None:
		self.mode = mode
		if mode == "pvp":
			self.input_p2.set_text(PLAYER_NAMES[1])
		else:
			self.input_p2.set_text("Bot")

	def _start_game(self) -> None:
		p1_name = self.input_p1.text.strip() or PLAYER_NAMES[0]
		p2_name = self.input_p2.text.strip() or ("Bot" if self.mode == "pvb" else PLAYER_NAMES[1])
		# If PvB, first go to BotSelectScene to choose bot AI mode
		if self.mode == "pvb":
			from game.ui.pygame_ui.scenes.bot_select_scene import BotSelectScene
			self.app.set_scene(BotSelectScene(self.app, self.assets, self.mode, p1_name, p2_name))
			return

		self.app.set_scene(
			RpsScene(self.app, self.assets, self.mode, p1_name, p2_name)
		)

	def handle_event(self, event: pygame.event.Event) -> None:
		if self.step == "menu":
			if self.btn_pvp.is_clicked(event):
				self.mode = "pvp"
				self._start_game()
				return
			if self.btn_pvb.is_clicked(event):
				self.mode = "pvb"
				self._start_game()
				return
			if self.btn_quit.is_clicked(event):
				self.app.request_quit()
				return

	def update(self, dt: float) -> None:
		_ = dt

	def draw(self, surface: pygame.Surface) -> None:
		self._draw_background(surface)
		if self.step == "menu":
			self._draw_menu(surface)
		else:
			self._draw_name_entry(surface)
