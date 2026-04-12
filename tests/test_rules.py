"""Basic tests for O An Quan rules."""

from __future__ import annotations

import unittest

from game.board import Board
from game import rules


class RulesTestCase(unittest.TestCase):
	def test_initial_board_setup(self) -> None:
		board = Board.create_initial()
		self.assertEqual(sum(board.seeds[idx] for idx in [1, 2, 3, 4, 5]), 25)
		self.assertEqual(sum(board.seeds[idx] for idx in [7, 8, 9, 10, 11]), 25)
		self.assertTrue(board.has_quan(0))
		self.assertTrue(board.has_quan(6))

	def test_move_must_be_from_player_side(self) -> None:
		board = Board.create_initial()
		self.assertTrue(rules.is_valid_move(board, 0, 1))
		self.assertFalse(rules.is_valid_move(board, 0, 8))

	def test_cannot_capture_non_mature_quan(self) -> None:
		board = Board.create_initial()
		board.seeds = [
			0,  # 0 left quan
			0,
			0,
			0,
			1,  # 4 start pit
			0,
			4,  # 6 right quan has only 4 seeds (non-mature)
			0,
			0,
			0,
			0,
			0,
		]
		board.quan_alive = [True, True]

		captured = rules.execute_turn(board, player_id=0, pit_index=4, direction=1)
		self.assertEqual(captured, 0)
		self.assertTrue(board.has_quan(6))

	def test_refill_and_borrow_when_side_empty(self) -> None:
		board = Board.create_initial()
		for pit in [1, 2, 3, 4, 5]:
			board.seeds[pit] = 0
		captured = [3, 0]
		borrowed = [0, 0]

		borrowed_now = rules.ensure_side_has_seeds(board, 0, captured, borrowed)
		self.assertEqual(borrowed_now, 2)
		self.assertEqual(captured[0], 0)
		self.assertEqual(borrowed[0], 2)
		self.assertEqual(sum(board.seeds[p] for p in [1, 2, 3, 4, 5]), 5)


if __name__ == "__main__":
	unittest.main()

