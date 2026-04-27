"""Scene base cho pygame app."""

from __future__ import annotations

import pygame


class BaseScene:
	def handle_event(self, event: pygame.event.Event) -> None:
		pass

	def update(self, dt: float) -> None:
		pass

	def draw(self, surface: pygame.Surface) -> None:
		pass
