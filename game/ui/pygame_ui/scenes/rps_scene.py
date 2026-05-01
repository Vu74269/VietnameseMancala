"""Rock-paper-scissors scene for pygame UI."""

from __future__ import annotations

import random
from typing import Tuple

import pygame

from config import PLAYER_NAMES
from game.engine import GameEngine
from game.ui.pygame_ui.assets import AssetManager
from game.ui.pygame_ui.scenes.base_scene import BaseScene
from game.ui.pygame_ui import settings


class RpsScene(BaseScene):
	def __init__(
		self,
		app: "PygameApp",
		assets: AssetManager,
		mode: str,
		p1_name: str,
		p2_name: str,
		bot_type: str = "random",
	) -> None:
		self.app = app
		self.assets = assets
		self.mode = mode
		self.p1_name = p1_name or PLAYER_NAMES[0]
		self.p2_name = p2_name or ("Bot" if mode == "pvb" else PLAYER_NAMES[1])
		self.bot_type = bot_type if bot_type in ("random", "greedy") else "random"

		self.title_font = pygame.font.SysFont("georgia", 48, bold=True)
		self.body_font = pygame.font.SysFont("segoeui", 22)
		self.small_font = pygame.font.SysFont("segoeui", 18)

		# Use image icons as clickable buttons (transparent PNGs)
		icon_size = (120, 120)
		self.icon_rock = self.assets.load_image("rps_rock", size=icon_size)
		self.icon_paper = self.assets.load_image("rps_paper", size=icon_size)
		self.icon_scissors = self.assets.load_image("rps_scissors", size=icon_size)

		self.rect_rock = pygame.Rect(340, 420, icon_size[0], icon_size[1])
		self.rect_paper = pygame.Rect(555, 420, icon_size[0], icon_size[1])
		self.rect_scissors = pygame.Rect(770, 420, icon_size[0], icon_size[1])

		self.pick_0 = ""
		self.pick_1 = ""
		self.winner = -1
		self.timer = 0.0
		self.message = ""

		if self.mode == "pvp":
			self._resolve_random_pvp()

	def _resolve_random_pvp(self) -> None:
		while True:
			self.pick_0 = random.choice(["rock", "paper", "scissors"])
			self.pick_1 = random.choice(["rock", "paper", "scissors"])
			self.winner = GameEngine._rps_winner(self.pick_0, self.pick_1)
			if self.winner != -1:
				break
		self.message = (
			f"Random RPS: {self.p1_name}={self.pick_0} vs {self.p2_name}={self.pick_1}"
		)

	def _draw_background(self, surface: pygame.Surface) -> None:
		bg_img = self.assets.load_image("background", size=(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
		if bg_img is not None:
			surface.blit(bg_img, (0, 0))
			return

		for y in range(settings.WINDOW_HEIGHT):
			ratio = y / settings.WINDOW_HEIGHT
			r = int(settings.BG_TOP[0] * (1 - ratio) + settings.BG_BOTTOM[0] * ratio)
			g = int(settings.BG_TOP[1] * (1 - ratio) + settings.BG_BOTTOM[1] * ratio)
			b = int(settings.BG_TOP[2] * (1 - ratio) + settings.BG_BOTTOM[2] * ratio)
			pygame.draw.line(surface, (r, g, b), (0, y), (settings.WINDOW_WIDTH, y))

	def _go_to_game(self) -> None:
		# Lazy import to avoid circular dependency
		from game.ui.pygame_ui.scenes.game_scene import GameScene
		# Build GameEngine with chosen players/strategies
		if self.mode == "pvb":
			from game.players.human_player import HumanPlayer
			from game.players.bot_player import BotPlayer
			from game.ai.base_strategy import GreedyStrategy, RandomStrategy

			p0 = HumanPlayer(0, self.p1_name)
			if self.bot_type == "greedy":
				strategy = GreedyStrategy()
			else:
				strategy = RandomStrategy()
			p1 = BotPlayer(1, self.p2_name, strategy)
			engine = GameEngine(mode=self.mode, players=[p0, p1])
		else:
			from game.players.human_player import HumanPlayer
			engine = GameEngine(mode=self.mode, players=[HumanPlayer(0, self.p1_name), HumanPlayer(1, self.p2_name)])

		engine.start(first_player=self.winner)
		self.app.set_scene(
			GameScene(self.app, engine, self.assets, (self.pick_0, self.pick_1))
		)

	def handle_event(self, event: pygame.event.Event) -> None:
		if self.mode == "pvp":
			return

		# image button clicks
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			pos = event.pos
			if self.rect_rock.collidepoint(pos):
				self.pick_0 = "rock"
				self.pick_1 = random.choice(["rock", "paper", "scissors"])
				self.winner = GameEngine._rps_winner(self.pick_0, self.pick_1)
				self.message = (
					f"{self.p1_name}={self.pick_0} vs {self.p2_name}={self.pick_1}"
				)
				self.timer = 0.0
				return
			if self.rect_paper.collidepoint(pos):
				self.pick_0 = "paper"
				self.pick_1 = random.choice(["rock", "paper", "scissors"])
				self.winner = GameEngine._rps_winner(self.pick_0, self.pick_1)
				self.message = (
					f"{self.p1_name}={self.pick_0} vs {self.p2_name}={self.pick_1}"
				)
				self.timer = 0.0
				return
			if self.rect_scissors.collidepoint(pos):
				self.pick_0 = "scissors"
				self.pick_1 = random.choice(["rock", "paper", "scissors"])
				self.winner = GameEngine._rps_winner(self.pick_0, self.pick_1)
				self.message = (
					f"{self.p1_name}={self.pick_0} vs {self.p2_name}={self.pick_1}"
				)
				self.timer = 0.0

	def update(self, dt: float) -> None:
		self.timer += dt
		if self.mode == "pvp":
			if self.timer > 1.4:
				self._go_to_game()
			return

		if self.pick_0 and self.pick_1 and self.winner != -1 and self.timer > 1.2:
			self._go_to_game()

	def _draw_rps_icon(self, surface: pygame.Surface, pick: str, center: Tuple[int, int]) -> None:
		icon = self.assets.load_image(f"rps_{pick}", size=(120, 120))
		if icon is not None:
			rect = icon.get_rect(center=center)
			surface.blit(icon, rect)
			return

		fallback = self.body_font.render(pick[:1].upper(), True, settings.TEXT_PRIMARY)
		surface.blit(fallback, fallback.get_rect(center=center))

	def draw(self, surface: pygame.Surface) -> None:
		self._draw_background(surface)

		title = self.title_font.render("Rock / Paper / Scissors", True, settings.TEXT_PRIMARY)
		surface.blit(title, title.get_rect(center=(settings.WINDOW_WIDTH // 2, 150)))

		name_line = self.small_font.render(
			f"{self.p1_name} vs {self.p2_name}", True, settings.TEXT_MUTED
		)
		surface.blit(name_line, name_line.get_rect(center=(settings.WINDOW_WIDTH // 2, 190)))

		if self.mode == "pvb":
			mouse_pos = pygame.mouse.get_pos()
			if self.icon_rock is not None and self.icon_paper is not None and self.icon_scissors is not None:
				for img, rect in ((self.icon_rock, self.rect_rock), (self.icon_paper, self.rect_paper), (self.icon_scissors, self.rect_scissors)):
					is_hover = rect.collidepoint(mouse_pos)
					if is_hover:
						t = pygame.transform.smoothscale(img, (int(img.get_width() * 1.06), int(img.get_height() * 1.06)))
						r = t.get_rect(center=rect.center)
						surface.blit(t, r)
						pygame.draw.rect(surface, settings.BUTTON_BG_HOVER, r.inflate(8, 8), 3, border_radius=12)
					else:
						surface.blit(img, rect)
			else:
				# fallback textual layout
				x = 340
				for label in ("Rock", "Paper", "Scissors"):
					rect = pygame.Rect(x, 420, 170, 52)
					pygame.draw.rect(surface, settings.BUTTON_BG, rect, border_radius=12)
					pygame.draw.rect(surface, settings.WHITE, rect, 2, border_radius=12)
					text = self.body_font.render(label, True, settings.BUTTON_TEXT)
					surface.blit(text, text.get_rect(center=rect.center))
					x += 215
			info = self.small_font.render("Choose your move", True, settings.TEXT_MUTED)
			surface.blit(info, info.get_rect(center=(settings.WINDOW_WIDTH // 2, 380)))
		else:
			info = self.small_font.render("Random draw...", True, settings.TEXT_MUTED)
			surface.blit(info, info.get_rect(center=(settings.WINDOW_WIDTH // 2, 380)))

		if self.pick_0 and self.pick_1:
			self._draw_rps_icon(surface, self.pick_0, (520, 290))
			self._draw_rps_icon(surface, self.pick_1, (760, 290))

		if self.message:
			msg = self.small_font.render(self.message, True, settings.TEXT_PRIMARY)
			surface.blit(msg, msg.get_rect(center=(settings.WINDOW_WIDTH // 2, 520)))
