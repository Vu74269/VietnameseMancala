"""Bộ chạy pygame dùng GameEngine headless."""

from __future__ import annotations

def run_pygame_game(mode: str) -> None:
	try:
		from game.ui.pygame_ui import PygameApp
	except ModuleNotFoundError as exc:
		raise RuntimeError(
			"Pygame is not installed. Run: pip install -r requirements.txt"
		) from exc

	_ = mode
	app = PygameApp()
	app.run()
