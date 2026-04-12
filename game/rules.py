"""Các hàm xử lý luật chơi Ô ăn quan."""

from __future__ import annotations

from typing import Dict, List

from config import CLOCKWISE, COUNTER_CLOCKWISE, MIN_SEEDS_TO_CAPTURE_QUAN, QUAN_VALUE
from game.board import Board


def is_valid_move(board: Board, player_id: int, pit_index: int) -> bool:
	"""Nước đi hợp lệ khi ô đó thuộc bên người chơi và còn ít nhất 1 quân."""
	return pit_index in board.side_indices(player_id) and board.seeds[pit_index] > 0


def _can_capture_target(board: Board, target_idx: int) -> bool:
	# Quan chỉ được ăn khi có đủ 5 quân trở lên.
	if board.is_quan_pit(target_idx) and board.has_quan(target_idx):
		return board.seeds[target_idx] >= MIN_SEEDS_TO_CAPTURE_QUAN
	return board.seeds[target_idx] > 0


def _capture_target(board: Board, target_idx: int) -> int:
	# Ăn toàn bộ quân trong ô mục tiêu; nếu là quan đủ điều kiện thì cộng thêm giá trị quan.
	captured = board.seeds[target_idx]
	board.seeds[target_idx] = 0

	if board.is_quan_pit(target_idx) and board.has_quan(target_idx):
		board.remove_quan(target_idx)
		captured += QUAN_VALUE

	return captured


def _capture_chain(board: Board, first_target_idx: int, direction: int) -> int:
	"""Xử lý chuỗi ăn TH2/TH5/TH6.

	Mẫu sau quân rải cuối cùng sẽ là:
	trống -> ô ăn được -> trống -> ô ăn được -> ...
	"""
	total_captured = 0
	target_idx = first_target_idx

	while _can_capture_target(board, target_idx):
		total_captured += _capture_target(board, target_idx)

		empty_idx = board.next_index(target_idx, direction)
		next_target_idx = board.next_index(empty_idx, direction)

		# Chuỗi chỉ tiếp tục nếu đúng mẫu trống -> có thể ăn.
		if board.seeds[empty_idx] != 0 or board.has_quan(empty_idx):
			break
		if not _can_capture_target(board, next_target_idx):
			break
		target_idx = next_target_idx

	return total_captured


def execute_turn(board: Board, player_id: int, pit_index: int, direction: int) -> int:
	"""Thực thi toàn bộ một lượt đi và trả về số quân người chơi vừa ăn được."""
	if not is_valid_move(board, player_id, pit_index):
		raise ValueError("Invalid move.")
	if direction not in (CLOCKWISE, COUNTER_CLOCKWISE):
		raise ValueError(
			"Direction must be CLOCKWISE(-1) or COUNTER_CLOCKWISE(1) in current mapping."
		)

	captured_total = 0

	# Bốc toàn bộ quân ở ô được chọn.
	hand = board.clear_pit(pit_index)
	current_idx = pit_index

	while True:
		# Rải từng quân một theo hướng đã chọn.
		# Ví dụ: ở ô 11, nếu đi cw thì lần lượt sang 10, 9, 8...
		while hand > 0:
			current_idx = board.next_index(current_idx, direction)
			board.seeds[current_idx] += 1
			hand -= 1

		next_idx = board.next_index(current_idx, direction)

		# TH4: ô tiếp theo là ô quan còn sống thì mất lượt.
		if board.is_quan_pit(next_idx) and board.has_quan(next_idx):
			break

		# TH1: ô tiếp theo có quân -> bốc lên và rải tiếp.
		if board.seeds[next_idx] > 0:
			hand = board.clear_pit(next_idx)
			current_idx = next_idx
			continue

		# Ô kế tiếp trống, kiểm tra ô sau nữa để xét các luật ăn.
		target_idx = board.next_index(next_idx, direction)

		# TH2/TH5/TH6: nếu ô mục tiêu ăn được thì bắt đầu chuỗi ăn.
		if _can_capture_target(board, target_idx):
			captured_total += _capture_chain(board, target_idx, direction)

		# TH3 hoặc sau khi ăn xong thì kết thúc lượt.
		break

	return captured_total


def ensure_side_has_seeds(
	board: Board,
	player_id: int,
	captured_by_player: List[int],
	borrowed_by_player: List[int],
) -> int:
	"""Rải lại 1 quân vào mỗi ô bên mình khi cả 5 ô đều trống.

	Trả về số quân đã phải vay từ đối thủ.
	"""
	if not board.is_side_empty(player_id):
		return 0

	required = len(board.side_indices(player_id))
	from_owned = min(captured_by_player[player_id], required)
	captured_by_player[player_id] -= from_owned

	borrowed = required - from_owned
	if borrowed > 0:
		borrowed_by_player[player_id] += borrowed

	for pit in board.side_indices(player_id):
		board.seeds[pit] += 1

	return borrowed


def check_game_over(board: Board) -> bool:
	"""Kết thúc game khi cả hai ô quan đã bị ăn và không còn quân nào trong đó."""
	for idx in (0, 6):
		if board.has_quan(idx):
			return False
		if board.seeds[idx] > 0:
			return False
	return True


def collect_remaining_side_seeds(board: Board, captured_by_player: List[int]) -> None:
	"""Cuối game, mỗi người lấy hết quân còn lại trên 5 ô thuộc quyền mình."""
	for player_id in (0, 1):
		for pit in board.side_indices(player_id):
			captured_by_player[player_id] += board.seeds[pit]
			board.seeds[pit] = 0


def calculate_score(
	captured_by_player: List[int], borrowed_by_player: List[int]
) -> Dict[int, int]:
	"""Tính điểm cuối cùng, có trừ phần quân đã vay và cộng phần được trả."""
	score_0 = captured_by_player[0] - borrowed_by_player[0] + borrowed_by_player[1]
	score_1 = captured_by_player[1] - borrowed_by_player[1] + borrowed_by_player[0]
	return {0: score_0, 1: score_1}

