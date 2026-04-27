"""Lightweight widgets for pygame UI."""

from __future__ import annotations

from typing import Optional, Tuple
import pygame


class Button:
	def __init__(
		self,
		rect: pygame.Rect,
		label: str,
		font: pygame.font.Font,
		bg: Tuple[int, int, int],
		bg_hover: Tuple[int, int, int],
		text_color: Tuple[int, int, int],
		border_color: Optional[Tuple[int, int, int]] = None,
	) -> None:
		self.rect = rect
		self.label = label
		self.font = font
		self.bg = bg
		self.bg_hover = bg_hover
		self.text_color = text_color
		self.border_color = border_color

	def draw(self, surface: pygame.Surface) -> None:
		# Draw simple 3D-like button: shadow, main face, top highlight.
		mouse_pos = pygame.mouse.get_pos()
		is_hover = self.rect.collidepoint(mouse_pos)
		bg = self.bg_hover if is_hover else self.bg

		# shadow
		shadow_rect = self.rect.move(4, 4)
		pygame.draw.rect(surface, (20, 20, 20), shadow_rect, border_radius=12)

		# main face
		pygame.draw.rect(surface, bg, self.rect, border_radius=12)

		# top highlight (lighter strip)
		highlight = (min(255, bg[0] + 20), min(255, bg[1] + 20), min(255, bg[2] + 20))
		high_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.width - 6, max(6, self.rect.height // 6))
		pygame.draw.rect(surface, highlight, high_rect, border_radius=8)

		if self.border_color is not None:
			pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=12)
		text = self.font.render(self.label, True, self.text_color)
		surface.blit(text, text.get_rect(center=self.rect.center))

	def is_clicked(self, event: pygame.event.Event) -> bool:
		return (
			event.type == pygame.MOUSEBUTTONDOWN
			and event.button == 1
			and self.rect.collidepoint(event.pos)
		)


class TextInput:
	def __init__(
		self,
		rect: pygame.Rect,
		font: pygame.font.Font,
		placeholder: str,
		max_length: int = 16,
	) -> None:
		self.rect = rect
		self.font = font
		self.placeholder = placeholder
		self.max_length = max_length
		self.text = ""
		self.active = False

	def set_text(self, value: str) -> None:
		self.text = value[: self.max_length]

	def handle_event(self, event: pygame.event.Event) -> None:
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			self.active = self.rect.collidepoint(event.pos)
			return

		if event.type != pygame.KEYDOWN or not self.active:
			return

		if event.key == pygame.K_BACKSPACE:
			self.text = self.text[:-1]
			return

		if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
			return

		if event.unicode and len(self.text) < self.max_length:
			self.text += event.unicode

	def draw(
		self,
		surface: pygame.Surface,
		bg: Tuple[int, int, int],
		border: Tuple[int, int, int],
		border_active: Tuple[int, int, int],
		text_color: Tuple[int, int, int],
		placeholder_color: Tuple[int, int, int],
	) -> None:
		pygame.draw.rect(surface, bg, self.rect, border_radius=8)
		active_border = border_active if self.active else border
		pygame.draw.rect(surface, active_border, self.rect, 2, border_radius=8)
		value = self.text if self.text else self.placeholder
		color = text_color if self.text else placeholder_color
		text = self.font.render(value, True, color)
		text_rect = text.get_rect(midleft=(self.rect.x + 12, self.rect.centery))
		surface.blit(text, text_rect)
