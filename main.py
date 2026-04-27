"""Điểm vào chính của game Ô ăn quan (pygame)."""

from __future__ import annotations

from game.ui.pygame_runner import run_pygame_game


def main() -> None:
	print("=== O An Quan ===")
	run_pygame_game("pvp")


if __name__ == "__main__":
	main()