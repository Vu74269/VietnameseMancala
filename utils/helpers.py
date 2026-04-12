"""Các hàm tiện ích dùng chung."""

from __future__ import annotations

import os

from config import CLOCKWISE


def clear_screen() -> None:
	# Xóa màn hình terminal để vẽ lại bàn cờ cho gọn.
	# os.system("cls" if os.name == "nt" else "clear")  # Tam tat de xem lich su turn.
	pass


def direction_label(direction: int) -> str:
	# Chuyển hướng số sang nhãn dễ đọc.
	return "cw" if direction == CLOCKWISE else "ccw"

