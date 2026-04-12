"""Người chơi bot."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from game.ai.base_strategy import RandomStrategy, Strategy
from game.players.base_player import BasePlayer


class BotPlayer(BasePlayer):
	def __init__(
		self,
		player_id: int,
		name: str,
		strategy: Optional[Strategy] = None,
	) -> None:
		super().__init__(player_id=player_id, name=name)
		# Bot mặc định dùng strategy đơn giản, sau này AI team có thể thay thế.
		self.strategy = strategy or RandomStrategy()

	def choose_move(
		self, board_state: Dict[str, object], valid_moves: List[int]
	) -> Tuple[int, int]:
		return self.strategy.get_best_move(board_state, self.player_id, valid_moves)

