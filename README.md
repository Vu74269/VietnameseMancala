# O An Quan Game (Console + Pygame GUI)

Project Python cho game O An Quan, tach ro phan board/rules/engine/player/ui de de mo rong AI va GUI.

## 1. Cai dat

Yeu cau:
- Python 3.10+

Tao virtual environment (khuyen nghi):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Cai dependencies:

```powershell
pip install -r requirements.txt
```

## 2. Chay game (Terminal)

```powershell
python main.py
```

Sau khi chay:
1. Chon UI: `1` (Console) hoac `2` (Pygame).
1. Chon mode: `1` (PvP) hoac `2` (PvB).
2. Nhap ten nguoi choi.
3. Oan tu ti (rock/paper/scissors) de quyet dinh nguoi di truoc.
4. Moi luot nhap theo dinh dang:

```text
<pit_index> <cw|ccw>
```

Vi du:

```text
11 cw
```

Quy uoc huong hien tai:
- `cw`  = giam chi so (11 -> 10 -> 9 -> ... -> 0 -> 11)
- `ccw` = tang chi so (11 -> 0 -> 1 -> ... -> 10 -> 11)

### Dieu khien trong Pygame

- Click 1 o hop le de chon nuoc di.
- Click nut `CW` hoac `CCW` (hoac bam phim `C`/`X`) de danh.
- Bam `Esc` de bo chon o.

## 3. Cai dat cho VS Code

Ban khong bat buoc cai extension nao de chay GUI.

Can thiet:
- Python 3.10+
- Da cai package `pygame` trong virtual env

Khuyen nghi trong VS Code:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)

Neu gap loi khi mo cua so pygame:
- Chay tu terminal da active `.venv`.
- Dung python 64-bit.
- Thu cap nhat driver GPU neu may qua cu.

## 4. Tai nguyen anh PNG (optional)

Du an ho tro fallback: neu khong co anh thi van ve bang shape.

Dat file vao thu muc: `assets/images/`

Ten file khuyen nghi:
- `board.png`
- `pit_small.png`
- `pit_quan.png`
- `player_human.png`
- `player_bot.png`
- `rps_rock.png`
- `rps_paper.png`
- `rps_scissors.png`

Kich thuoc khuyen nghi (px x px):
- Board background: `2200 x 1040` (tile/scale xuong 1100 x 520)
- O nho: `160 x 160`
- O quan: `256 x 256`
- Avatar nguoi/AI: `512 x 512`
- Icon RPS: `256 x 256`

Luu y:
- Nen dung PNG co alpha trong suot.
- Giu ti le 1:1 cho sprite tron (pit, avatar, RPS).
- Xuat tai nguyen gap doi kich thuoc hien thi de hinh sac net hon.

## 5. Cau truc du lieu

### 5.1 Ban co va chi so o

- Tong 12 o, danh so vong tron: `0..11`
- O quan trai: `0`
- O quan phai: `6`
- 5 o nguoi choi 0: `[1, 2, 3, 4, 5]`
- 5 o nguoi choi 1: `[11, 10, 9, 8, 7]`

### 5.2 Du lieu trong `Board`

- `seeds: List[int]`
	- Mang 12 phan tu, moi phan tu la so quan dan trong tung o.
- `quan_alive: List[bool]`
	- `quan_alive[0]`: quan o o 0 con song hay da bi an.
	- `quan_alive[1]`: quan o o 6 con song hay da bi an.

### 5.3 Du lieu trang thai trong `GameEngine`

- `self.board: Board`
- `self.captured_by_player: List[int]`
	- Tong so quan da an duoc (chua tru vay).
- `self.borrowed_by_player: List[int]`
	- So quan da vay khi bi "het quan ben minh".
- `self.players: List[BasePlayer]`
	- Gom `HumanPlayer`/`BotPlayer` tuy mode.
- `self.current_player: int`
	- `0` hoac `1`.

### 5.4 Du lieu truyen qua AI/player

- `board_state: Dict[str, object]` (tu `Board.get_state()`)
	- `seeds`, `quan_alive`, `player_0_side`, `player_1_side`, `quan_indices`.
- `valid_moves: List[int]`
	- Danh sach cac o hop le co the chon o luot hien tai.

## 6. Chi tiet tat ca ham va method

### 6.1 `main.py`

- `main() -> None`
	- In tieu de game.
	- Chon backend UI (`console` hoac `pygame`).
	- Chon mode (`pvp`/`pvb`) roi goi runner tuong ung.

### 6.2 `game/board.py` - `class Board`

- `Board.create_initial() -> Board`
	- Khoi tao ban co mac dinh: moi o dan 5 quan, o quan 0 quan, 2 quan lon con song.
- `copy() -> Board`
	- Tra ve ban sao de AI/co che mo phong dung ma khong sua board goc.
- `get_state() -> Dict[str, object]`
	- Dong goi trang thai hien tai thanh dict.
- `is_quan_pit(index: int) -> bool`
	- Kiem tra mot index co phai o quan hay khong.
- `next_index(index: int, direction: int) -> int`
	- Tinh o tiep theo theo huong `cw/ccw`.
	- Raise `ValueError` neu huong khong hop le.
- `side_indices(player_id: int) -> List[int]`
	- Tra ve 5 o thuoc quyen player.
- `get_valid_moves(player_id: int) -> List[int]`
	- Tra ve cac o ben player co quan de duoc chon.
- `has_quan(index: int) -> bool`
	- Kiem tra o quan (0/6) co con quan lon hay da bi an.
- `remove_quan(index: int) -> None`
	- Danh dau quan lon o o quan da bi an.
- `pit_owner(index: int) -> Optional[int]`
	- Xac dinh chu o (0/1), tra `None` neu la o quan.
- `is_side_empty(player_id: int) -> bool`
	- Kiem tra ca 5 o ben player co dang trong het khong.
- `clear_pit(index: int) -> int`
	- Lay het quan trong o va dat o do ve 0.
	- Tra ve so quan vua lay.

### 6.3 `game/rules.py`

- `is_valid_move(board, player_id, pit_index) -> bool`
	- Nuoc di hop le khi o duoc chon thuoc ben player va co quan.
- `_can_capture_target(board, target_idx) -> bool`
	- Kiem tra o dich co du dieu kien de an.
	- Neu la o quan thi phai >= 5 quan dan moi duoc an quan.
- `_capture_target(board, target_idx) -> int`
	- An sach quan o dich, neu co quan lon thi cong them gia tri quan (`QUAN_VALUE`).
- `_capture_chain(board, first_target_idx, direction) -> int`
	- Xu ly chuoi an dang: `trong -> an duoc -> trong -> an duoc ...`.
- `execute_turn(board, player_id, pit_index, direction) -> int`
	- Ham quan trong nhat cho 1 luot:
	- Boc quan o duoc chon.
	- Rai theo huong.
	- Xu ly TH1..TH6.
	- Tra ve tong quan vua an trong luot.
- `ensure_side_has_seeds(board, player_id, captured_by_player, borrowed_by_player) -> int`
	- Neu 5 o ben player trong het:
	- Lay tu quan da an de rai lai 5 o (moi o 1 quan).
	- Neu thieu thi ghi no vao `borrowed_by_player`.
	- Tra ve so quan da vay.
- `check_game_over(board) -> bool`
	- Ket thuc khi ca 2 o quan deu khong con quan lon va khong con quan dan.
- `collect_remaining_side_seeds(board, captured_by_player) -> None`
	- Cuoi game, moi ben thu het quan con lai o 5 o cua minh.
- `calculate_score(captured_by_player, borrowed_by_player) -> Dict[int, int]`
	- Tinh diem cuoi co tru no vay va cong phan doi thu phai tra lai.

### 6.4 `game/engine.py` - `class GameEngine`

- `__init__(mode: str) -> None`
	- Khoi tao board, diem, nguoi choi, luot hien tai (headless).
	- `mode` chi nhan `pvp` hoac `pvb`.
	- Co the truyen danh sach player tuy chinh.
- `_create_default_players() -> List[BasePlayer]`
	- Tao danh sach player theo mode:
	- `pvp`: 2 nguoi.
	- `pvb`: 1 nguoi + 1 bot.
- `start(first_player: int = 0) -> None`
	- Dat nguoi di truoc.
- `prepare_turn() -> TurnContext`
	- Xu ly refill/vay neu can va tra ve trang thai luot hien tai.
- `execute_move(pit, direction) -> MoveResult`
	- Thuc thi nuoc di va cap nhat so quan an.
- `end_turn() -> None`
	- Chuyen luot cho nguoi choi con lai.
- `skip_turn() -> None`
	- Bo luot an toan khi khong co nuoc hop le.
- `finalize_game() -> FinalResult`
	- Thu quan cuoi game va tinh diem chung cuoc.
- `_rps_winner(pick_0: str, pick_1: str) -> int`
	- Tinh ket qua oẳn tù xì.
	- Tra `0`/`1` neu co nguoi thang, `-1` neu hoa.

### 6.5 `game/players/base_player.py` - `class BasePlayer`

- `__init__(player_id: int, name: str) -> None`
	- Luu id va ten nguoi choi.
- `choose_move(board_state, valid_moves) -> Tuple[int, int]` (abstract)
	- Interface bat buoc cho tat ca player.
	- Tra ve `(pit_index, direction)`.

### 6.6 `game/players/human_player.py` - `class HumanPlayer`

- `choose_move(board_state, valid_moves) -> Tuple[int, int]`
	- Doc input tu terminal dang `<pit> <cw|ccw>`.
	- Validate pit va huong.
	- Lap lai neu sai dinh dang/khong hop le.

### 6.7 `game/players/bot_player.py` - `class BotPlayer`

- `__init__(player_id, name, strategy=None) -> None`
	- Nhan strategy tuy chon, neu khong co thi dung `RandomStrategy`.
- `choose_move(board_state, valid_moves) -> Tuple[int, int]`
	- Uy quyen cho `self.strategy.get_best_move(...)`.

### 6.8 `game/ai/base_strategy.py`

- `class Strategy`
	- Interface AI:
	- `get_best_move(board_state, player_id, valid_moves) -> Tuple[int, int]`.
- `class RandomStrategy(Strategy)`
	- AI don gian nhat de game chay duoc ngay.
- `RandomStrategy.get_best_move(...) -> Tuple[int, int]`
	- Chon ngau nhien 1 o hop le va 1 huong hop le.

### 6.9 `game/ui/console_ui.py` - `class ConsoleUI`

- `choose_mode() -> str`
	- Chon `pvp`/`pvb` tu menu 1/2.
- `ask_player_name(default_name: str) -> str`
	- Nhap ten nguoi choi, Enter de giu mac dinh.
- `ask_rps(name: str) -> str`
	- Nhap rock/paper/scissors.
- `show_rps_result(name_0, pick_0, name_1, pick_1) -> None`
	- In ket qua oẳn tù xì.
- `render_board(board, current_player_name, captured_by_player, borrowed_by_player) -> None`
	- Ve ban co dang text.
	- In score tam thoi, thong tin vay, va huong di.
- `show_resupply(name: str, borrowed: int) -> None`
	- In thong bao khi refill tu quan da an hoac co vay.
- `show_move_summary(name, pit, direction, captured) -> None`
	- In tom tat nuoc di vua danh.
- `show_final(scores, captured_by_player, borrowed_by_player, names) -> None`
	- In ket qua cuoi va nguoi thang.

### 6.10 `game/ui/pygame_ui/*`

- `app.py`
	- Quan ly vong lap pygame (event/update/draw).
- `scenes/game_scene.py`
	- Render ban co, o, score HUD.
	- Xu ly click chuot/chon huong/cap nhat turn.
- `assets.py`
	- Tai sprite PNG tu `assets/images` (co fallback neu thieu file).

### 6.11 `utils/helpers.py`

- `clear_screen() -> None`
	- Ham xoa terminal.
	- Hien dang tam tat (`pass`) de xem lich su turn.
- `direction_label(direction: int) -> str`
	- Chuyen huong so sang text `cw`/`ccw`.

### 6.12 `tests/test_rules.py` - `class RulesTestCase`

- `test_initial_board_setup()`
	- Test trang thai board ban dau.
- `test_move_must_be_from_player_side()`
	- Test validate o chon co thuoc ben minh khong.
- `test_cannot_capture_non_mature_quan()`
	- Test khong duoc an quan non (< 5 quan).
- `test_refill_and_borrow_when_side_empty()`
	- Test logic refill + vay khi het quan ben minh.

## 7. Luat da duoc map vao code

- Tai nguyen ban dau:
	- 12 o: 2 o quan + 10 o quan nho.
	- 50 quan nho: moi o nho 5 quan.
	- 2 quan lon (moi quan tri gia 10 diem), dat o 2 o quan.
- Chon nguoi di truoc bang RPS (rock/paper/scissors).
- Moi luot:
	- Boc toan bo quan o 1 o ben minh.
	- Rai tung quan theo `cw` hoac `ccw`.
	- Xu ly TH1..TH6 trong `game/rules.py`.
- Quan non:
	- Chi duoc an quan khi o quan do co it nhat 5 quan nho.
- Het quan ben minh:
	- Tu dong rai moi o ben minh 1 quan.
	- Neu khong du 5 quan tu so da an, se vay doi thu (ghi no, cuoi game phai tra).
- Ket thuc:
	- Hai o quan khong con quan nho va quan lon da bi an het.
	- Quan con lai ben nao thuoc ve ben do.
	- Tinh diem co tru no vay.

## 8. Mo rong AI

`BotPlayer` dang goi strategy qua `Strategy.get_best_move(...)`.

Team AI co the:
1. Tao file moi, vi du `game/ai/minimax_strategy.py`.
2. Implement class ke thua `Strategy`.
3. Truyen strategy do vao `BotPlayer` trong `game/engine.py`.

## 9. Chay test

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

