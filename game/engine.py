"""Engine điều phối người chơi, luật, và giao diện console."""

from __future__ import annotations

import random
from typing import List

from config import PLAYER_NAMES
from game.board import Board
from game.players.base_player import BasePlayer
from game.players.bot_player import BotPlayer
from game.players.human_player import HumanPlayer
from game import rules
from game.ui.console_ui import ConsoleUI


class GameEngine:
	def __init__(self, mode: str) -> None:
		if mode not in ("pvp", "pvb"):
			raise ValueError("Mode must be 'pvp' or 'pvb'.")

		# Trạng thái tổng của một ván chơi.
		self.mode = mode
		self.board = Board.create_initial()
		self.captured_by_player: List[int] = [0, 0]
		self.borrowed_by_player: List[int] = [0, 0]
		self.players: List[BasePlayer] = self._create_players()
		self.current_player = 0

	def _create_players(self) -> List[BasePlayer]:
		if self.mode == "pvp":
			p1_name = ConsoleUI.ask_player_name(PLAYER_NAMES[0])
			p2_name = ConsoleUI.ask_player_name(PLAYER_NAMES[1])
			return [HumanPlayer(0, p1_name), HumanPlayer(1, p2_name)]

		p1_name = ConsoleUI.ask_player_name(PLAYER_NAMES[0])
		return [HumanPlayer(0, p1_name), BotPlayer(1, "Bot")]

	@staticmethod
	def _rps_winner(pick_0: str, pick_1: str) -> int:
		if pick_0 == pick_1:
			return -1
		win_pairs = {
			("rock", "scissors"),
			("scissors", "paper"),
			("paper", "rock"),
		}
		return 0 if (pick_0, pick_1) in win_pairs else 1

	def choose_first_player(self) -> int:
		while True:
			# Oẳn tù xì để xác định người đi trước.
			p0_pick = ConsoleUI.ask_rps(self.players[0].name)

			if isinstance(self.players[1], BotPlayer):
				p1_pick = random.choice(["rock", "paper", "scissors"])
			else:
				p1_pick = ConsoleUI.ask_rps(self.players[1].name)

			ConsoleUI.show_rps_result(
				self.players[0].name,
				p0_pick,
				self.players[1].name,
				p1_pick,
			)

			winner = self._rps_winner(p0_pick, p1_pick)
			if winner == -1:
				print("RPS tie, replay.")
				continue

			return winner

	def play(self) -> None:
		# Chọn người đi trước bằng RPS rồi bắt đầu vòng lặp chính.
		self.current_player = self.choose_first_player()
		print(f"{self.players[self.current_player].name} goes first.")
		input("Press Enter to start the game...")

		while not rules.check_game_over(self.board):
			active = self.players[self.current_player]
			# Kiểm tra trước khi rải: nếu cả 5 ô bên mình trống thì phải bơm lại quân.
			was_empty_side = self.board.is_side_empty(self.current_player)

			borrowed = rules.ensure_side_has_seeds(
				self.board,
				self.current_player,
				self.captured_by_player,
				self.borrowed_by_player,
			)

			ConsoleUI.render_board(
				self.board,
				active.name,
				self.captured_by_player,
				self.borrowed_by_player,
			)

			if self.board.is_side_empty(self.current_player):
				# Chỉ là chốt an toàn nếu strategy bên ngoài trả về trạng thái không hợp lệ.
				print(f"{active.name} has no valid pits this turn. Turn skipped.")
				self.current_player = 1 - self.current_player
				continue

			if was_empty_side:
				ConsoleUI.show_resupply(active.name, borrowed)

			valid_moves = self.board.get_valid_moves(self.current_player)
			pit, direction = active.choose_move(self.board.get_state(), valid_moves)
			captured = rules.execute_turn(self.board, self.current_player, pit, direction)
			self.captured_by_player[self.current_player] += captured

			ConsoleUI.show_move_summary(active.name, pit, direction, captured)
			input("Press Enter for next turn...")

			self.current_player = 1 - self.current_player

		rules.collect_remaining_side_seeds(self.board, self.captured_by_player)
		scores = rules.calculate_score(self.captured_by_player, self.borrowed_by_player)
		names = [self.players[0].name, self.players[1].name]
		ConsoleUI.render_board(
			self.board,
			"Game End",
			self.captured_by_player,
			self.borrowed_by_player,
		)
		ConsoleUI.show_final(
			scores,
			self.captured_by_player,
			self.borrowed_by_player,
			names,
		)

