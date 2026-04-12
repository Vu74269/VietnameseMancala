"""Người chơi nhập tay qua terminal."""

from __future__ import annotations

from typing import Dict, List, Tuple

from config import CLOCKWISE, COUNTER_CLOCKWISE
from game.players.base_player import BasePlayer


class HumanPlayer(BasePlayer):
	def choose_move(
		self, board_state: Dict[str, object], valid_moves: List[int]
	) -> Tuple[int, int]:
		# Nhập theo dạng: <ô> <cw|ccw>
		# Quy ước: cw = giảm chỉ số (ví dụ 11->10), ccw = tăng chỉ số (ví dụ 11->0).
		while True:
			try:
				raw = input(
					f"{self.name} choose pit {valid_moves} then direction (cw/ccw), example '11 cw' or '11 ccw': "
				).strip()
				pit_text, direction_text = raw.split()
				pit = int(pit_text)

				if pit not in valid_moves:
					print("Invalid pit. Pick one pit in your side that has seeds.")
					continue

				direction_text = direction_text.lower()
				if direction_text == "cw":
					direction = CLOCKWISE
				elif direction_text == "ccw":
					direction = COUNTER_CLOCKWISE
				else:
					print("Direction must be 'cw' or 'ccw'.")
					continue

				return pit, direction
			except ValueError:
				print("Invalid input format. Use: <pit> <cw|ccw>")

