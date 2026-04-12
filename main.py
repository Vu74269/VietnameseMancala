"""Điểm vào chính của game Ô ăn quan bản console."""

from __future__ import annotations

from game.engine import GameEngine
from game.ui.console_ui import ConsoleUI


def main() -> None:
	# Chỉ khởi động UI console và engine, chưa có GUI.
	print("=== O An Quan (Console) ===")
	mode = ConsoleUI.choose_mode()
	engine = GameEngine(mode=mode)
	engine.play()


if __name__ == "__main__":
	main()

