"""Mô hình bàn cờ Ô ăn quan.

Bàn cờ được biểu diễn như một vòng tròn 12 ô theo thứ tự 0 -> 11.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from config import (
	CLOCKWISE,
	COUNTER_CLOCKWISE,
	INITIAL_QUAN_PIT_SEEDS,
	INITIAL_SMALL_PIT_SEEDS,
	LEFT_QUAN_INDEX,
	PLAYER_0_SIDE,
	PLAYER_1_SIDE,
	QUAN_INDICES,
	RIGHT_QUAN_INDEX,
	TOTAL_PITS,
)


@dataclass
class Board:
	"""Trạng thái bàn cờ có thể thay đổi trong suốt ván chơi."""

	seeds: List[int]
	quan_alive: List[bool]

	@classmethod
	def create_initial(cls) -> "Board":
		# Khởi tạo 50 quân dân: mỗi ô dân 5 quân, hai ô quan bắt đầu trống.
		seeds = [0] * TOTAL_PITS
		for idx in PLAYER_0_SIDE + PLAYER_1_SIDE:
			seeds[idx] = INITIAL_SMALL_PIT_SEEDS
		seeds[LEFT_QUAN_INDEX] = INITIAL_QUAN_PIT_SEEDS
		seeds[RIGHT_QUAN_INDEX] = INITIAL_QUAN_PIT_SEEDS

		# Mảng đánh dấu 2 ô quan còn sống hay đã bị ăn.
		return cls(seeds=seeds, quan_alive=[True, True])

	def copy(self) -> "Board":
		return Board(seeds=self.seeds.copy(), quan_alive=self.quan_alive.copy())

	def get_state(self) -> Dict[str, object]:
		return {
			"seeds": self.seeds.copy(),
			"quan_alive": self.quan_alive.copy(),
			"player_0_side": PLAYER_0_SIDE.copy(),
			"player_1_side": PLAYER_1_SIDE.copy(),
			"quan_indices": list(QUAN_INDICES),
		}

	@staticmethod
	def is_quan_pit(index: int) -> bool:
		return index in QUAN_INDICES

	@staticmethod
	def next_index(index: int, direction: int) -> int:
		# Quy ước hiện tại:
		# - CLOCKWISE  = -1: đi theo chiều kim đồng hồ (giảm chỉ số).
		# - COUNTER_CLOCKWISE = 1: đi ngược chiều kim đồng hồ (tăng chỉ số).
		if direction not in (CLOCKWISE, COUNTER_CLOCKWISE):
			raise ValueError("Huong di khong hop le.")
		return (index + direction) % TOTAL_PITS

	@staticmethod
	def side_indices(player_id: int) -> List[int]:
		return PLAYER_0_SIDE if player_id == 0 else PLAYER_1_SIDE

	def get_valid_moves(self, player_id: int) -> List[int]:
		# Chỉ được chọn các ô thuộc bên mình và đang có quân.
		return [pit for pit in self.side_indices(player_id) if self.seeds[pit] > 0]

	def has_quan(self, index: int) -> bool:
		if index == LEFT_QUAN_INDEX:
			return self.quan_alive[0]
		if index == RIGHT_QUAN_INDEX:
			return self.quan_alive[1]
		return False

	def remove_quan(self, index: int) -> None:
		if index == LEFT_QUAN_INDEX:
			self.quan_alive[0] = False
		elif index == RIGHT_QUAN_INDEX:
			self.quan_alive[1] = False

	def pit_owner(self, index: int) -> Optional[int]:
		if index in PLAYER_0_SIDE:
			return 0
		if index in PLAYER_1_SIDE:
			return 1
		return None

	def is_side_empty(self, player_id: int) -> bool:
		return all(self.seeds[pit] == 0 for pit in self.side_indices(player_id))

	def clear_pit(self, index: int) -> int:
		stones = self.seeds[index]
		self.seeds[index] = 0
		return stones

