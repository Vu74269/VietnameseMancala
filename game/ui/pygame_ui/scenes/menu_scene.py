"""Menu scene for pygame UI."""

from __future__ import annotations

import pygame

from game.ui.pygame_ui.assets import AssetManager
from game.ui.pygame_ui.scenes.base_scene import BaseScene
from game.ui.pygame_ui.widgets import Button
from game.ui.pygame_ui import settings


class MenuScene(BaseScene):
	def __init__(self, app: "PygameApp", assets: AssetManager) -> None:
		self.app = app
		self.assets = assets

		self.title_font = pygame.font.SysFont("tahoma", 56, bold=True)
		self.head_font = pygame.font.SysFont("tahoma", 28, bold=True)
		self.body_font = pygame.font.SysFont("segoeui", 22)
		self.small_font = pygame.font.SysFont("segoeui", 18)

		self.mode = "pvp"

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
			(144, 83, 56),
			(170, 103, 69),
			settings.WHITE,
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
		title = self.title_font.render(text, True, settings.TEXT_PRIMARY)
		surface.blit(title, title.get_rect(center=(settings.WINDOW_WIDTH // 2, 140)))

	def _draw_menu(self, surface: pygame.Surface) -> None:
		# Bright centered title with soft glow so it does not sink into the background.
		title_center = (settings.WINDOW_WIDTH // 2, 180)
		glow = self.title_font.render("O ĂN QUAN", True, (26, 58, 32))
		for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)]:
			surface.blit(glow, glow.get_rect(center=(title_center[0] + dx, title_center[1] + dy)))

		title = self.title_font.render("O ĂN QUAN", True, (249, 250, 243))
		surface.blit(title, title.get_rect(center=title_center))

		self.btn_pvp.draw(surface)
		self.btn_pvb.draw(surface)
		self.btn_quit.draw(surface)




	def handle_event(self, event: pygame.event.Event) -> None:
		if self.btn_pvp.is_clicked(event):
			from game.ui.pygame_ui.scenes.name_input_scene import NameInputScene
			self.app.set_scene(NameInputScene(self.app, self.assets, "pvp"))
			return
		if self.btn_pvb.is_clicked(event):
			from game.ui.pygame_ui.scenes.name_input_scene import NameInputScene
			self.app.set_scene(NameInputScene(self.app, self.assets, "pvb"))
			return
		if self.btn_quit.is_clicked(event):
			self.app.request_quit()
			return

	def update(self, dt: float) -> None:
		_ = dt

	def draw(self, surface: pygame.Surface) -> None:
		self._draw_background(surface)
		self._draw_menu(surface)


