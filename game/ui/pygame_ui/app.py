"""Vòng lặp ứng dụng pygame."""

from __future__ import annotations

import pygame

from game.ui.pygame_ui.assets import AssetManager
from game.ui.pygame_ui.scenes.base_scene import BaseScene
from game.ui.pygame_ui.scenes.menu_scene import MenuScene
from game.ui.pygame_ui import settings


class PygameApp:
	def __init__(self) -> None:
		self.clock: pygame.time.Clock | None = None
		self.screen: pygame.Surface | None = None
		self.assets: AssetManager | None = None
		self.scene: BaseScene | None = None
		self.running = False

	def _init_pygame(self) -> None:
		pygame.init()
		pygame.display.set_caption(settings.WINDOW_TITLE)
		self.screen = pygame.display.set_mode(
			(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
		)
		self.clock = pygame.time.Clock()
		self.assets = AssetManager()
		self.scene = MenuScene(self, self.assets)

	def set_scene(self, scene: BaseScene) -> None:
		self.scene = scene

	def request_quit(self) -> None:
		self.running = False

	def run(self) -> None:
		self._init_pygame()
		assert self.screen is not None
		assert self.clock is not None
		assert self.scene is not None

		self.running = True
		while self.running:
			dt = self.clock.tick(settings.FPS) / 1000.0

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					break
				self.scene.handle_event(event)

			self.scene.update(dt)
			self.scene.draw(self.screen)
			pygame.display.flip()

		pygame.quit()
