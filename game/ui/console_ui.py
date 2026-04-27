"""Giao diện console cho game Ô ăn quan."""

from __future__ import annotations

from typing import Dict, List

from config import CLOCKWISE
from game.board import Board
#from utils.helpers import clear_screen


class ConsoleUI:
	@staticmethod
	def choose_ui_backend() -> str:
		while True:
			choice = input("Choose UI: 1) Console  2) Pygame : ").strip()
			if choice == "1":
				return "console"
			if choice == "2":
				return "pygame"
			print("Invalid choice. Enter 1 or 2.")

	@staticmethod
	def choose_mode() -> str:
		# Chọn chế độ chơi trước khi khởi tạo engine.
		while True:
			mode = input("Choose mode: 1) PvP  2) PvB : ").strip()
			if mode == "1":
				return "pvp"
			if mode == "2":
				return "pvb"
			print("Invalid mode. Enter 1 or 2.")

	@staticmethod
	def ask_player_name(default_name: str) -> str:
		# Cho phép nhập tên riêng hoặc bấm Enter để giữ mặc định.
		name = input(f"Name for {default_name} (Enter to keep): ").strip()
		return name if name else default_name

	@staticmethod
	def ask_rps(name: str) -> str:
		# Nhập kết quả oẳn tù xì bằng text để xác định lượt đi đầu.
		while True:
			pick = input(f"{name} pick rock/paper/scissors: ").strip().lower()
			if pick in ("rock", "paper", "scissors"):
				return pick
			print("Invalid choice.")

	@staticmethod
	def show_rps_result(name_0: str, pick_0: str, name_1: str, pick_1: str) -> None:
		print(f"RPS: {name_0}={pick_0} vs {name_1}={pick_1}")

	@staticmethod
	def render_board(
		board: Board,
		current_player_name: str,
		captured_by_player: List[int],
		borrowed_by_player: List[int],
	) -> None:
		# Xóa màn hình để hiển thị trạng thái bàn cờ gọn gàng hơn.
		# clear_screen()  # Tam tat de giu lai man hinh cua turn truoc.

		# Hiển thị theo đúng vòng 0 -> 11, với hàng trên là phía 11..7.
		top = "  ".join(f"[{idx}:{board.seeds[idx]:2d}]" for idx in [11, 10, 9, 8, 7])
		bottom = "  ".join(f"[{idx}:{board.seeds[idx]:2d}]" for idx in [1, 2, 3, 4, 5])

		left_quan = (
			f"Q0 seeds={board.seeds[0]} {'alive' if board.has_quan(0) else 'captured'}"
		)
		right_quan = (
			f"Q1 seeds={board.seeds[6]} {'alive' if board.has_quan(6) else 'captured'}"
		)

		print("========== O AN QUAN ==========")
		print(f"Turn: {current_player_name}")
		print()
		print(f"          {top}")
		print(f"{left_quan:26s}            {right_quan}")
		print(f"          {bottom}")
		print()
		print(
			f"Captured: P1={captured_by_player[0]}  P2={captured_by_player[1]}"
			f" | Borrowed: P1={borrowed_by_player[0]}  P2={borrowed_by_player[1]}"
		)
		print("Pit labels are the index before ':' in [index:seeds].")
		print("Direction rule: cw = kim dong ho (11->10->9...)")
		print("                ccw = nguoc kim dong ho (11->0->1...)")

	@staticmethod
	def show_resupply(name: str, borrowed: int) -> None:
		# Thông báo khi người chơi phải rải lại quân vì bên mình đã trống hết.
		if borrowed > 0:
			print(f"{name} had empty side and borrowed {borrowed} seeds to refill.")
		else:
			print(f"{name} had empty side and refilled from captured seeds.")

	@staticmethod
	def show_move_summary(name: str, pit: int, direction: int, captured: int) -> None:
		# Tóm tắt nước đi vừa thực hiện để người chơi dễ debug.
		direction_text = "cw" if direction == CLOCKWISE else "ccw"
		print(
			f"{name} moved pit {pit} direction {direction_text}. Captured this turn: {captured}."
		)

	@staticmethod
	def show_final(
		scores: Dict[int, int],
		captured_by_player: List[int],
		borrowed_by_player: List[int],
		names: List[str],
	) -> None:
		# In kết quả cuối cùng sau khi đã trừ phần quân vay.
		print("\n========== FINAL RESULT ==========")
		print(
			f"{names[0]} raw={captured_by_player[0]}, borrowed={borrowed_by_player[0]}, final={scores[0]}"
		)
		print(
			f"{names[1]} raw={captured_by_player[1]}, borrowed={borrowed_by_player[1]}, final={scores[1]}"
		)

		if scores[0] > scores[1]:
			print(f"Winner: {names[0]}")
		elif scores[1] > scores[0]:
			print(f"Winner: {names[1]}")
		else:
			print("Result: Draw")

