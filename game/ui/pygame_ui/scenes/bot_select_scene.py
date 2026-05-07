"""Scene to pick bot mode (Random or Greedy) before RPS and game start."""

from __future__ import annotations

import pygame

from config import PLAYER_NAMES
from game.ui.pygame_ui.assets import AssetManager
from game.ui.pygame_ui.scenes.base_scene import BaseScene
from game.ui.pygame_ui.widgets import Button
from game.ui.pygame_ui import settings


class BotSelectScene(BaseScene):
	BOT_LABELS = {
		"random": "Trẻ con",
		"greedy": "Học trò",
		"minimax": "Trạng nguyên",
	}
	BOT_BUTTON_COLORS = {
		"random": ((58, 126, 72), (78, 158, 92)),
		"greedy": ((54, 103, 166), (76, 131, 205)),
		"minimax": ((170, 62, 62), (205, 86, 86)),
	}

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

		self.title_font = pygame.font.SysFont("tahoma", 56, bold=True)
		self.body_font = pygame.font.SysFont("tahoma", 28, bold=True)
		self.small_font = pygame.font.SysFont("segoeui", 18)

		# buttons
		self.btn_random = Button(pygame.Rect(410, 260, 460, 64), "Trẻ con", self.body_font, *self.BOT_BUTTON_COLORS["random"], settings.BUTTON_TEXT, settings.WHITE)
		self.btn_greedy = Button(pygame.Rect(410, 346, 460, 64), "Học trò", self.body_font, *self.BOT_BUTTON_COLORS["greedy"], settings.BUTTON_TEXT, settings.WHITE)
		self.btn_minimax = Button(pygame.Rect(410, 432, 460, 64), "Trạng nguyên", self.body_font, *self.BOT_BUTTON_COLORS["minimax"], settings.BUTTON_TEXT, settings.WHITE)
		self.btn_back = Button(pygame.Rect(360, 560, 220, 48), "Quay lại", self.body_font, settings.BUTTON_BG, settings.BUTTON_BG_HOVER, settings.BUTTON_TEXT, settings.WHITE)
		self.btn_start = Button(pygame.Rect(700, 560, 220, 48), "Next", self.body_font, settings.BUTTON_BG, settings.BUTTON_BG_HOVER, settings.BUTTON_TEXT, settings.WHITE)

		self.bot_type = "random"
		self.message = "Chọn đối thủ"
		self.selected_bot_name = self.BOT_LABELS[self.bot_type]
		self.selected_bot_label = self.bot_type.capitalize()
		self.title_outline_color = (48, 114, 64)

	def _draw_outlined_title(self, surface: pygame.Surface, text: str, center: tuple[int, int]) -> None:
		for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
			outline = self.title_font.render(text, True, self.title_outline_color)
			surface.blit(outline, outline.get_rect(center=(center[0] + dx, center[1] + dy)))
		title = self.title_font.render(text, True, settings.WHITE)
		surface.blit(title, title.get_rect(center=center))

	def _launch_rps(self) -> None:
		from game.ui.pygame_ui.scenes.rps_scene import RpsScene
		self.app.set_scene(RpsScene(self.app, self.assets, self.mode, self.p1_name, self.selected_bot_name, self.bot_type))

	def _select_bot(self, bot_type: str) -> None:
		self.bot_type = bot_type
		self.selected_bot_name = self.BOT_LABELS[bot_type]
		self.selected_bot_label = bot_type.capitalize()

	def handle_event(self, event: pygame.event.Event) -> None:
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			if self.btn_random.is_clicked(event):
				self._select_bot("random")
				return
			if self.btn_greedy.is_clicked(event):
				self._select_bot("greedy")
				return
			if self.btn_minimax.is_clicked(event):
				self._select_bot("minimax")
				return
			if self.btn_back.is_clicked(event):
				from game.ui.pygame_ui.scenes.menu_scene import MenuScene
				self.app.set_scene(MenuScene(self.app, self.assets))
				return
			if self.btn_start.is_clicked(event):
				self._launch_rps()
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

		self._draw_outlined_title(surface, "Chọn đối thủ", (settings.WINDOW_WIDTH // 2, 140))

		# draw buttons
		self.btn_random.draw(surface)
		self.btn_greedy.draw(surface)
		self.btn_minimax.draw(surface)
		self.btn_back.draw(surface)
		self.btn_start.draw(surface)

		status_x = settings.WINDOW_WIDTH - 380
		status_y = settings.WINDOW_HEIGHT - 104
		status_panel = pygame.Surface((340, 74), pygame.SRCALPHA)
		status_panel.fill((76, 54, 32, 168))
		surface.blit(status_panel, (status_x, status_y))
		pygame.draw.rect(surface, (247, 236, 214), pygame.Rect(status_x, status_y, 340, 74), 2, border_radius=12)
		opponent_text = self.small_font.render(f"Đối thủ: {self.selected_bot_name}", True, settings.WHITE)
		ai_text = self.small_font.render(f"Bot AI {self.selected_bot_label}", True, settings.TEXT_MUTED)
		surface.blit(opponent_text, (status_x + 14, status_y + 12))
		surface.blit(ai_text, (status_x + 14, status_y + 40))
