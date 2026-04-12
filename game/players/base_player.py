"""Interface chung cho mọi loại người chơi."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class BasePlayer(ABC):
	def __init__(self, player_id: int, name: str) -> None:
		# player_id: 0 hoặc 1 để engine biết đang tới lượt ai.
		self.player_id = player_id
		self.name = name

	@abstractmethod
	def choose_move(
		self, board_state: Dict[str, object], valid_moves: List[int]
	) -> Tuple[int, int]:
		"""Trả về (ô chọn, hướng rải)."""

