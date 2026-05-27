## Vietnamese Mancala Game (Console + Pygame GUI)

A Python project with powerful engine for the traditional Vietnamese game O An Quan (Vietnamese Mancala). The project separates `board`, `rules`, `engine`, `player`, and `ui` components to make it easier to extend with AI and a GUI.

## 1. Installation

Requirements:
- Python 3.10+

Create a virtual environment (recommended):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## 2. Run the game (terminal)

```powershell
python main.py
```

## 3. VS Code setup

No special extensions are required to run the GUI, but the following are recommended.

Required:
- Python 3.10+
- `pygame` installed in the virtual environment

Recommended VS Code extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)

If you encounter issues opening a pygame window:
- Run from a terminal with the `.venv` activated.
- Use 64-bit Python.
- Try updating GPU drivers on older machines.

## 4. PNG image assets (optional)

The project supports a fallback: if image files are missing, shapes are drawn instead.

Place image files in: `assets/images/`

## 5. Data structure

### 5.1 Board and pit indices

- Total 12 pits, indices wrap: `0..11`
- Left big pit: `0`
- Right big pit: `6`
- Player 0's 5 pits: `[1, 2, 3, 4, 5]`
- Player 1's 5 pits: `[11, 10, 9, 8, 7]`

### 5.2 Data in `Board`

- `seeds: List[int]`
  - An array of 12 elements; each element is the number of small stones in that pit.
- `quan_alive: List[bool]`
  - `quan_alive[0]`: whether the big piece at pit 0 is still present.
  - `quan_alive[1]`: whether the big piece at pit 6 is still present.

### 5.3 Game state in `GameEngine`

- `self.board: Board`
- `self.captured_by_player: List[int]`
  - Total small stones captured by each player (debt not yet subtracted).
- `self.borrowed_by_player: List[int]`
  - Amount borrowed when a side runs out of stones.
- `self.players: List[BasePlayer]`
  - Contains `HumanPlayer`/`BotPlayer` depending on mode.
- `self.current_player: int`
  - `0` or `1`.

### 5.4 Data passed to AI/player

- `board_state: Dict[str, object]` (from `Board.get_state()`)
  - Contains `seeds`, `quan_alive`, `player_0_side`, `player_1_side`, `quan_indices`.
- `valid_moves: List[int]`
  - List of pit indices that are valid choices for the current turn.

## 6. Detailed functions and methods

### 6.1 `main.py`

- `main() -> None`
  - Prints the game title.
  - Chooses the backend UI (`console` or `pygame`).
  - Chooses mode (`pvp`/`pvb`) and runs the appropriate runner.

### 6.2 `game/board.py` - `class Board`

- `Board.create_initial() -> Board`
  - Initialize the default board: each small pit has 5 stones, big pits have 0, both big pieces present.
- `copy() -> Board`
  - Return a copy for AI/simulation without modifying the original board.
- `get_state() -> Dict[str, object]`
  - Pack current state into a dict.
- `is_quan_pit(index: int) -> bool`
  - Check whether an index is a big piece pit.
- `next_index(index: int, direction: int) -> int`
  - Compute the next pit index according to `cw/ccw`.
  - Raises `ValueError` if direction is invalid.
- `side_indices(player_id: int) -> List[int]`
  - Return the 5 pit indices belonging to the player.
- `get_valid_moves(player_id: int) -> List[int]`
  - Return the pits on the player's side that contain seeds and are selectable.
- `has_quan(index: int) -> bool`
  - Check if a big piece (pit 0 or 6) is still present.
- `remove_quan(index: int) -> None`
  - Mark a big piece pit as removed.
- `pit_owner(index: int) -> Optional[int]`
  - Determine the owner of a pit (0/1), return `None` for big piece pits.
- `is_side_empty(player_id: int) -> bool`
  - Check whether all 5 pits on the player's side are empty.
- `clear_pit(index: int) -> int`
  - Take all stones from a pit and set it to 0.
  - Return the number of stones taken.

### 6.3 `game/rules.py`

- `is_valid_move(board, player_id, pit_index) -> bool`
  - A move is valid when the chosen pit belongs to the player and has stones.
- `_can_capture_target(board, target_idx) -> bool`
  - Check whether the target pit meets capture conditions.
  - If it's a big piece pit, it must have at least 5 small stones to be captured.
- `_capture_target(board, target_idx) -> int`
  - Capture all stones from the target; if a big piece is present add the `QUAN_VALUE`.
- `_capture_chain(board, first_target_idx, direction) -> int`
  - Handle chained captures: empty -> capture -> empty -> capture ...
- `execute_turn(board, player_id, pit_index, direction) -> int`
  - The main function for one turn:
  - Pick up stones from the chosen pit.
  - Sow them according to direction.
  - Handle cases 1..6.
  - Return the total stones captured this turn.
- `ensure_side_has_seeds(board, player_id, captured_by_player, borrowed_by_player) -> int`
  - If all 5 pits on the player's side are empty:
  - Refill each pit from the captured pile (1 stone per pit).
  - If there aren't enough stones, record the debt in `borrowed_by_player`.
  - Return number of stones borrowed.
- `check_game_over(board) -> bool`
  - Game ends when both big pits are gone and there are no small stones left.
- `collect_remaining_side_seeds(board, captured_by_player) -> None`
  - At the end, each side collects all remaining small stones from its 5 pits.
- `calculate_score(captured_by_player, borrowed_by_player) -> Dict[int, int]`
  - Calculate final scores, subtract debts and apply any compensation.

### 6.4 `game/engine.py` - `class GameEngine`

- `__init__(mode: str) -> None`
  - Initialize board, scores, players, and current turn (headless).
  - `mode` accepts `pvp` or `pvb`.
  - Custom player lists can be supplied.
- `_create_default_players() -> List[BasePlayer]`
  - Create players based on mode:
  - `pvp`: 2 humans.
  - `pvb`: 1 human + 1 bot.
- `start(first_player: int = 0) -> None`
  - Set who starts first.
- `prepare_turn() -> TurnContext`
  - Handle refills/borrowing if needed and return the current turn context.
- `execute_move(pit, direction) -> MoveResult`
  - Perform the move and update captured counts.
- `end_turn() -> None`
  - Switch the turn to the other player.
- `skip_turn() -> None`
  - Safely skip a turn when no valid move exists.
- `finalize_game() -> FinalResult`
  - Collect remaining stones and compute final scores.
- `_rps_winner(pick_0: str, pick_1: str) -> int`
  - Determine the Rock-Paper-Scissors winner.
  - Return `0`/`1` for a player win, `-1` for a tie.

### 6.5 `game/players/base_player.py` - `class BasePlayer`

- `__init__(player_id: int, name: str) -> None`
  - Store player id and name.
- `choose_move(board_state, valid_moves) -> Tuple[int, int]` (abstract)
  - Required interface for all players.
  - Return `(pit_index, direction)`.

### 6.6 `game/players/human_player.py` - `class HumanPlayer`

- `choose_move(board_state, valid_moves) -> Tuple[int, int]`
  - Read input from terminal in the form `<pit> <cw|ccw>`.
  - Validate pit and direction.
  - Repeat until valid.

### 6.7 `game/players/bot_player.py` - `class BotPlayer`

- `__init__(player_id, name, strategy=None) -> None`
  - Accept an optional strategy; if missing use `RandomStrategy`.
- `choose_move(board_state, valid_moves) -> Tuple[int, int]`
  - Delegate to `self.strategy.get_best_move(...)`.

### 6.8 `game/ai/base_strategy.py`

- `class Strategy`
  - AI interface:
  - `get_best_move(board_state, player_id, valid_moves) -> Tuple[int, int]`.
- `class RandomStrategy(Strategy)`
  - A simple AI to let the game run immediately.
- `RandomStrategy.get_best_move(...) -> Tuple[int, int]`
  - Choose a random valid pit and a legal direction.

### 6.9 `game/ui/console_ui.py` - `class ConsoleUI`

- `choose_mode() -> str`
  - Pick `pvp`/`pvb` from menu 1/2.
- `ask_player_name(default_name: str) -> str`
  - Enter the player's name, press Enter to keep the default.
- `ask_rps(name: str) -> str`
  - Enter rock/paper/scissors.
- `show_rps_result(name_0, pick_0, name_1, pick_1) -> None`
  - Print RPS result.
- `render_board(board, current_player_name, captured_by_player, borrowed_by_player) -> None`
  - Draw the board as text.
  - Print temporary scores, debt info, and direction.
- `show_resupply(name: str, borrowed: int) -> None`
  - Notify when refilling from captured stones or when borrowing occurs.
- `show_move_summary(name, pit, direction, captured) -> None`
  - Print a summary of the played move.
- `show_final(scores, captured_by_player, borrowed_by_player, names) -> None`
  - Print final results and the winner.

### 6.10 `game/ui/pygame_ui/*`

- `app.py`
  - Manages the pygame loop (events/update/draw).
- `scenes/game_scene.py`
  - Render the board, pits, and score HUD.
  - Handle mouse clicks, direction selection, and turn updates.
- `assets.py`
  - Load PNG sprites from `assets/images` (with fallback if files are missing).

### 6.11 `utils/helpers.py`

- `clear_screen() -> None`
  - Clear the terminal.
  - Currently a no-op (`pass`) to keep a record of previous turns.
- `direction_label(direction: int) -> str`
  - Convert direction integer to `cw`/`ccw` label.

### 6.12 `tests/test_rules.py` - `class RulesTestCase`

- `test_initial_board_setup()`
  - Test the initial board state.
- `test_move_must_be_from_player_side()`
  - Test that chosen pit belongs to the player.
- `test_cannot_capture_non_mature_quan()`
  - Test that a big piece cannot be captured unless it has >= 5 small stones.
- `test_refill_and_borrow_when_side_empty()`
  - Test the refill and borrow logic when a side runs out.

## 7. Rules mapped to code

- Initial setup:
  - 12 pits: 2 big pits + 10 small pits.
  - 50 small stones: each small pit starts with 5 stones.
  - 2 big pieces (each worth 10 points), placed in the two big pits.
- First player is chosen by RPS (rock/paper/scissors).
- Each turn:
  - Pick up all stones from one of your pits.
  - Sow them one by one in `cw` or `ccw`.
  - Handle cases 1..6 as implemented in `game/rules.py`.
- Big piece capture:
  - A big piece can only be captured if that pit has at least 5 small stones.
- Running out of stones on your side:
  - Automatically refill each of your 5 pits with 1 stone from captured stones.
  - If there are fewer than 5 stones available, borrow from the opponent (record debt to be settled at game end).
- Game end:
  - Both big pits have been removed and there are no small stones left.
  - Remaining stones belong to the side that owns them.
  - Final scoring subtracts any borrowed stones.

## 8. AI extension

Planned improvement: calculate a better evaluation function for a stronger AI.

