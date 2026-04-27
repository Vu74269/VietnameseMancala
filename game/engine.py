"""Engine lõi điều phối trạng thái game, độc lập với UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from config import PLAYER_NAMES
from game.board import Board
from game import rules
from game.players.base_player import BasePlayer
from game.players.bot_player import BotPlayer
from game.players.human_player import HumanPlayer


@dataclass
class TurnContext:
	player_id: int
	player_name: str
	valid_moves: List[int]
	side_was_empty: bool
	borrowed: int


@dataclass
class MoveResult:
	player_id: int
	player_name: str
	pit: int
	direction: int
	captured: int


@dataclass
class FinalResult:
	scores: Dict[int, int]
	captured_by_player: List[int]
	borrowed_by_player: List[int]
	names: List[str]


class GameEngine:
	def __init__(self, mode: str, players: Optional[List[BasePlayer]] = None) -> None:
		if mode not in ("pvp", "pvb"):
			raise ValueError("Mode must be 'pvp' or 'pvb'.")

		# Trạng thái tổng của một ván chơi.
		self.mode = mode
		self.board = Board.create_initial()
		self.captured_by_player: List[int] = [0, 0]
		self.borrowed_by_player: List[int] = [0, 0]
		self.players: List[BasePlayer] = players or self._create_default_players()
		if len(self.players) != 2:
			raise ValueError("GameEngine requires exactly 2 players.")
		self.current_player = 0
		self._finished = False
		self._final_result: Optional[FinalResult] = None

	def _create_default_players(self) -> List[BasePlayer]:
		if self.mode == "pvp":
			return [
				HumanPlayer(0, PLAYER_NAMES[0]),
				HumanPlayer(1, PLAYER_NAMES[1]),
			]

		return [HumanPlayer(0, PLAYER_NAMES[0]), BotPlayer(1, "Bot")]

	def start(self, first_player: int = 0) -> None:
		if first_player not in (0, 1):
			raise ValueError("first_player must be 0 or 1.")
		self.current_player = first_player

	def get_active_player(self) -> BasePlayer:
		return self.players[self.current_player]

	def get_player_names(self) -> List[str]:
		return [self.players[0].name, self.players[1].name]

	def set_player_name(self, player_id: int, name: str) -> None:
		if player_id not in (0, 1):
			raise ValueError("player_id must be 0 or 1.")
		self.players[player_id].name = name

	def is_game_over(self) -> bool:
		return rules.check_game_over(self.board)

	def prepare_turn(self) -> TurnContext:
		if self._finished:
			raise RuntimeError("Game has already finished.")

		active = self.get_active_player()
		side_was_empty = self.board.is_side_empty(self.current_player)

		borrowed = rules.ensure_side_has_seeds(
			self.board,
			self.current_player,
			self.captured_by_player,
			self.borrowed_by_player,
		)

		valid_moves = self.board.get_valid_moves(self.current_player)
		return TurnContext(
			player_id=self.current_player,
			player_name=active.name,
			valid_moves=valid_moves,
			side_was_empty=side_was_empty,
			borrowed=borrowed,
		)

	def execute_move(self, pit: int, direction: int) -> MoveResult:
		if self._finished:
			raise RuntimeError("Game has already finished.")

		active = self.get_active_player()
		captured = rules.execute_turn(self.board, self.current_player, pit, direction)
		self.captured_by_player[self.current_player] += captured

		return MoveResult(
			player_id=self.current_player,
			player_name=active.name,
			pit=pit,
			direction=direction,
			captured=captured,
		)

	def end_turn(self) -> None:
		self.current_player = 1 - self.current_player

	def skip_turn(self) -> None:
		self.end_turn()

	def finalize_game(self) -> FinalResult:
		if self._final_result is not None:
			return self._final_result

		rules.collect_remaining_side_seeds(self.board, self.captured_by_player)
		scores = rules.calculate_score(self.captured_by_player, self.borrowed_by_player)
		self._final_result = FinalResult(
			scores=scores,
			captured_by_player=self.captured_by_player.copy(),
			borrowed_by_player=self.borrowed_by_player.copy(),
			names=self.get_player_names(),
		)
		self._finished = True
		return self._final_result

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

