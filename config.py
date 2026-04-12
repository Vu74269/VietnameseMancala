"""Cấu hình chung cho game Ô ăn quan bản console."""

NUM_PLAYERS = 2
NUM_SMALL_PITS_PER_SIDE = 5
TOTAL_PITS = 12

# Sơ đồ bàn cờ theo vòng tròn chiều kim đồng hồ:
# 0 = quan trái, 1..5 = 5 ô bên người chơi 0, 6 = quan phải, 7..11 = 5 ô bên người chơi 1.
# Player 1 được khai báo ngược lại để khi nhìn theo chiều kim đồng hồ từ 0 -> 11
# thì hai phía của bàn cờ khớp với cách đánh số.
# Quy ước hướng trong project này (theo yêu cầu hiện tại):
# - cw  = giảm chỉ số: 11 -> 10 -> 9 -> ... -> 0 -> 11
# - ccw = tăng chỉ số: 11 -> 0  -> 1 -> ... -> 10 -> 11
LEFT_QUAN_INDEX = 0
RIGHT_QUAN_INDEX = 6
QUAN_INDICES = (LEFT_QUAN_INDEX, RIGHT_QUAN_INDEX)

PLAYER_0_SIDE = [1, 2, 3, 4, 5]
PLAYER_1_SIDE = [11, 10, 9, 8, 7]

INITIAL_SMALL_PIT_SEEDS = 5
INITIAL_QUAN_PIT_SEEDS = 0

QUAN_VALUE = 10
MIN_SEEDS_TO_CAPTURE_QUAN = 5

CLOCKWISE = -1
COUNTER_CLOCKWISE = 1

PLAYER_NAMES = ("Player 1", "Player 2")

DEBUG_MODE = False
