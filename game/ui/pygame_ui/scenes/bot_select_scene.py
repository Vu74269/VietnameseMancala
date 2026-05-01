"""Scene to pick bot mode (Random or Greedy) before RPS and game start."""

from __future__ import annotations

from typing import Tuple

import pygame

from config import PLAYER_NAMES
from game.ui.pygame_ui.assets import AssetManager
from game.ui.pygame_ui.scenes.base_scene import BaseScene
from game.ui.pygame_ui.widgets import Button, TextInput
from game.ui.pygame_ui import settings


class BotSelectScene(BaseScene):
	def __init__(
		self,
		app: "PygameApp",
		assets: AssetManager,
		mode: str,
		p1_name: str,
		p2_name: str,
	) -> None:
		self.app = app
		self.assets = assets
		self.mode = mode
		self.p1_name = p1_name or PLAYER_NAMES[0]
		self.p2_name = p2_name or ("Bot" if mode == "pvb" else PLAYER_NAMES[1])

		self.title_font = pygame.font.SysFont("georgia", 56, bold=True)
		self.body_font = pygame.font.SysFont("cambria", 28, bold=True)
		self.small_font = pygame.font.SysFont("segoeui", 18)

		# buttons
		self.btn_random = Button(pygame.Rect(340, 260, 400, 60), "Random", self.body_font, settings.BUTTON_BG, settings.BUTTON_BG_HOVER, settings.BUTTON_TEXT, settings.WHITE)
		self.btn_greedy = Button(pygame.Rect(340, 340, 400, 60), "Greedy", self.body_font, settings.BUTTON_BG, settings.BUTTON_BG_HOVER, settings.BUTTON_TEXT, settings.WHITE)
		self.btn_back = Button(pygame.Rect(360, 560, 220, 48), "Back", self.body_font, settings.BUTTON_BG, settings.BUTTON_BG_HOVER, settings.BUTTON_TEXT, settings.WHITE)
		self.btn_start = Button(pygame.Rect(700, 560, 220, 48), "Next", self.body_font, settings.BUTTON_BG, settings.BUTTON_BG_HOVER, settings.BUTTON_TEXT, settings.WHITE)

		self.bot_type = "random"
		self.message = "Choose bot AI mode: Random or Greedy"

	def handle_event(self, event: pygame.event.Event) -> None:
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			if self.btn_random.is_clicked(event):
				self.bot_type = "random"
				self.message = "Bot mode: Random"
				return
			if self.btn_greedy.is_clicked(event):
				self.bot_type = "greedy"
				self.message = "Bot mode: Greedy"
				return
			if self.btn_back.is_clicked(event):
				from game.ui.pygame_ui.scenes.menu_scene import MenuScene
				self.app.set_scene(MenuScene(self.app, self.assets))
				return
			if self.btn_start.is_clicked(event):
				from game.ui.pygame_ui.scenes.rps_scene import RpsScene
				self.app.set_scene(RpsScene(self.app, self.assets, self.mode, self.p1_name, self.p2_name, self.bot_type))
				return

	def update(self, dt: float) -> None:
		_ = dt

	def draw(self, surface: pygame.Surface) -> None:
		# background
		bg = self.assets.load_image("background", size=(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
		if bg is not None:
			surface.blit(bg, (0, 0))
		else:
			for y in range(settings.WINDOW_HEIGHT):
				ratio = y / settings.WINDOW_HEIGHT
				r = int(settings.BG_TOP[0] * (1 - ratio) + settings.BG_BOTTOM[0] * ratio)
				g = int(settings.BG_TOP[1] * (1 - ratio) + settings.BG_BOTTOM[1] * ratio)
				b = int(settings.BG_TOP[2] * (1 - ratio) + settings.BG_BOTTOM[2] * ratio)
				pygame.draw.line(surface, (r, g, b), (0, y), (settings.WINDOW_WIDTH, y))

		title = self.title_font.render("Select Bot AI", True, settings.TEXT_PRIMARY)
		surface.blit(title, title.get_rect(center=(settings.WINDOW_WIDTH // 2, 140)))

		# draw buttons
		self.btn_random.draw(surface)
		self.btn_greedy.draw(surface)
		self.btn_back.draw(surface)
		self.btn_start.draw(surface)

		# selected indicator
		sel_text = self.small_font.render(f"Selected: {self.bot_type}", True, settings.TEXT_MUTED)
		surface.blit(sel_text, sel_text.get_rect(center=(settings.WINDOW_WIDTH // 2, 440)))

		if self.message:
			msg = self.small_font.render(self.message, True, settings.TEXT_PRIMARY)
			surface.blit(msg, msg.get_rect(center=(settings.WINDOW_WIDTH // 2, 480)))
