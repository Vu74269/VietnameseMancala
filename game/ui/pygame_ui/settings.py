"""Cấu hình giao diện pygame cho Ô ăn quan."""

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "O An Quan - Pygame"

BG_TOP = (245, 232, 207)
BG_BOTTOM = (216, 195, 160)
BOARD_COLOR = (170, 125, 85)
BOARD_BORDER = (110, 73, 45)
PIT_COLOR = (238, 220, 184)
PIT_HIGHLIGHT = (255, 241, 198)
PIT_SELECTED = (231, 122, 78)
TEXT_PRIMARY = (40, 30, 20)
TEXT_MUTED = (86, 70, 54)
WHITE = (250, 250, 250)
BLACK = (0, 0, 0)
BUTTON_BG = (56, 97, 139)
BUTTON_BG_HOVER = (73, 123, 173)
BUTTON_TEXT = (244, 248, 252)
INPUT_BG = (255, 248, 236)
INPUT_BORDER = (148, 114, 79)
INPUT_BORDER_ACTIVE = (196, 136, 68)

SMALL_PIT_RADIUS = 52
QUAN_PIT_RADIUS = 82

# Measured pit centers from assets/images/board.png.
PIT_CENTERS = {
	0: (216, 377),
	1: (375, 465),
	2: (507, 465),
	3: (634, 465),
	4: (759, 465),
	5: (889, 465),
	6: (1062, 377),
	7: (889, 300),
	8: (759, 300),
	9: (634, 300),
	10: (507, 300),
	11: (375, 300),
}

# Board rectangle used to place board.png.
BOARD_RECT = (90, 120, 1100, 520)
