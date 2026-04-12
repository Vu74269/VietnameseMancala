"""Giao diện chiến lược AI và strategy mặc định dạng random."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from config import CLOCKWISE, COUNTER_CLOCKWISE


class Strategy(ABC):
	@abstractmethod
	def get_best_move(
		self, board_state: Dict[str, object], player_id: int, valid_moves: List[int]
	) -> Tuple[int, int]:
		"""Trả về (ô chọn, hướng rải)."""


class RandomStrategy(Strategy):
	"""Strategy nền tảng đơn giản nhất: chọn ngẫu nhiên nước đi hợp lệ."""

	def get_best_move(
		self, board_state: Dict[str, object], player_id: int, valid_moves: List[int]
	) -> Tuple[int, int]:
		pit = random.choice(valid_moves)
		direction = random.choice([CLOCKWISE, COUNTER_CLOCKWISE])
		return pit, direction

