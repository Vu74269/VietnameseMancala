"""Bộ chạy game console dùng GameEngine headless."""

from __future__ import annotations

import random

from game.engine import GameEngine
from game.players.bot_player import BotPlayer
from game.ui.console_ui import ConsoleUI


def _choose_first_player(engine: GameEngine) -> int:
	while True:
		p0_pick = ConsoleUI.ask_rps(engine.players[0].name)

		if isinstance(engine.players[1], BotPlayer):
			p1_pick = random.choice(["rock", "paper", "scissors"])
		else:
			p1_pick = ConsoleUI.ask_rps(engine.players[1].name)

		ConsoleUI.show_rps_result(
			engine.players[0].name,
			p0_pick,
			engine.players[1].name,
			p1_pick,
		)

		winner = GameEngine._rps_winner(p0_pick, p1_pick)
		if winner == -1:
			print("RPS tie, replay.")
			continue

		return winner


def run_console_game(mode: str) -> None:
	engine = GameEngine(mode=mode)

	engine.set_player_name(0, ConsoleUI.ask_player_name(engine.players[0].name))
	if mode == "pvp":
		engine.set_player_name(1, ConsoleUI.ask_player_name(engine.players[1].name))

	first_player = _choose_first_player(engine)
	engine.start(first_player=first_player)

	print(f"{engine.players[engine.current_player].name} goes first.")
	input("Press Enter to start the game...")

	while not engine.is_game_over():
		context = engine.prepare_turn()
		ConsoleUI.render_board(
			engine.board,
			context.player_name,
			engine.captured_by_player,
			engine.borrowed_by_player,
		)

		if not context.valid_moves:
			print(f"{context.player_name} has no valid pits this turn. Turn skipped.")
			engine.skip_turn()
			continue

		if context.side_was_empty:
			ConsoleUI.show_resupply(context.player_name, context.borrowed)

		active = engine.get_active_player()
		pit, direction = active.choose_move(engine.board.get_state(), context.valid_moves)
		move = engine.execute_move(pit, direction)
		ConsoleUI.show_move_summary(
			move.player_name,
			move.pit,
			move.direction,
			move.captured,
		)
		input("Press Enter for next turn...")
		engine.end_turn()

	result = engine.finalize_game()
	ConsoleUI.render_board(
		engine.board,
		"Game End",
		result.captured_by_player,
		result.borrowed_by_player,
	)
	ConsoleUI.show_final(
		result.scores,
		result.captured_by_player,
		result.borrowed_by_player,
		result.names,
	)
