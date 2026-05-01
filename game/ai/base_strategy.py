"""Giao diện chiến lược AI và strategy mặc định dạng random."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from config import CLOCKWISE, COUNTER_CLOCKWISE
from game.board import Board
from game import rules

class Strategy(ABC):
	@abstractmethod
	def get_best_move(
		self, board_state: Dict[str, object], player_id: int, valid_moves: List[int]
	) -> Tuple[int, int]:
		"""Trả về (ô chọn, hướng rải)."""

class RandomStrategy(Strategy):
	def get_best_move(
		self, board_state: Dict[str, object], player_id: int, valid_moves: List[int]
	) -> Tuple[int, int]:
		pit = random.choice(valid_moves)
		direction = random.choice([CLOCKWISE, COUNTER_CLOCKWISE])
		return pit, direction

def evaluate(
    board: Board,
    player_id: int,
    captured_by_player: List[int],
    borrowed_by_player: List[int],
) -> float:
    M_p = int(captured_by_player[player_id]) - int(borrowed_by_player[player_id])
    M_opp = int(captured_by_player[1 - player_id]) - int(borrowed_by_player[1 - player_id])

    S_p = sum(int(board.seeds[i]) for i in Board.side_indices(player_id))
    S_opp = sum(int(board.seeds[i]) for i in Board.side_indices(1 - player_id))

    V_p = sum(1 for i in Board.side_indices(player_id) if int(board.seeds[i]) > 0)
    V_opp = sum(1 for i in Board.side_indices(1 - player_id) if int(board.seeds[i]) > 0)

    return 0.7 * (M_p - M_opp) + 0.1 * (S_p - S_opp) + 0.2 * (V_p - V_opp)

class GreedyStrategy(Strategy):
    def get_best_move(
        self, board_state: Dict[str, object], player_id: int, valid_moves: List[int]
    ) -> Tuple[int, int]:
        if not valid_moves:
            return RandomStrategy().get_best_move(board_state, player_id, valid_moves)

        base_board = Board(
            seeds=list(board_state["seeds"]),
            quan_alive=list(board_state["quan_alive"]),
        )
        base_captured: List[int] = list(board_state.get("captured_by_player", [0, 0]))
        base_borrowed: List[int] = list(board_state.get("borrowed_by_player", [0, 0]))

        best_score = float("-inf")
        best_move: Tuple[int, int] = (valid_moves[0], CLOCKWISE)
        best_captured = -1

        for pit in valid_moves:
            for direction in (CLOCKWISE, COUNTER_CLOCKWISE):
                b = base_board.copy()
                capt_sim = base_captured.copy()
                borrow_sim = base_borrowed.copy()
                try:
                    captured = rules.execute_turn(b, player_id, pit, direction)
                except Exception:
                    continue
                capt_sim[player_id] += captured
                score = evaluate(b, player_id, capt_sim, borrow_sim)
                if score > best_score or (score == best_score and captured > best_captured):
                    best_score = score
                    best_move = (pit, direction)
                    best_captured = captured
        return best_move
