# API Documentation

## ChessEngine

The main chess engine class for finding best moves.

### Initialization

```python
from src.engine import ChessEngine
import chess

# Create engine
engine = ChessEngine(depth=5, time_limit=2.0)
```

**Parameters:**
- `depth` (int): Search depth in half-moves/plies. Default: 4
- `time_limit` (float): Time limit in seconds per move. Default: 2.0

### Methods

#### `find_best_move(board, time_available=None) -> Optional[Move]`

Find the best move for the current position.

```python
board = chess.Board()
move = engine.find_best_move(board, time_available=2.0)

if move:
    print(f"Best move: {move.uci()}")
else:
    print("No legal moves")
```

**Parameters:**
- `board` (chess.Board): Current board position
- `time_available` (float, optional): Override time limit for this move

**Returns:**
- `chess.Move` or None: Best move found, or None if no legal moves

**Attributes After Search:**
- `nodes_searched` (int): Total nodes evaluated
- `transposition_table` (dict): Cached positions for reuse

## Evaluator

Position evaluation and scoring.

### Static Methods

#### `evaluate(board) -> int`

Evaluate a position from white's perspective.

```python
from src.evaluation import Evaluator
import chess

board = chess.Board()
score = Evaluator.evaluate(board)

print(f"Score: {score} centipawns")
print(f"White advantage: {score/100:.2f} pawns")
```

**Returns:**
- int: Score in centipawns (1/100th of a pawn)
  - Positive: White advantage
  - Negative: Black advantage
  - ±100000: Checkmate

#### `is_endgame(board) -> bool`

Check if position is in endgame.

```python
if Evaluator.is_endgame(board):
    print("Using endgame evaluation")
```

**Returns:**
- bool: True if no queens and ≤1 rook total

## ChessBoard

Chess board wrapper with utility methods.

### Initialization

```python
from src.board import ChessBoard

# New game
board = ChessBoard()

# From FEN
board = ChessBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
```

### Methods

#### `make_move(move) -> bool`

Make a move on the board.

```python
import chess

move = chess.Move(chess.E2, chess.E4)
if board.make_move(move):
    print("Move made")
else:
    print("Illegal move")
```

#### `make_move_san(san_move) -> bool`

Make a move from standard algebraic notation.

```python
if board.make_move_san("e4"):
    print("Moved e4")
else:
    print("Invalid move")
```

#### `get_legal_moves() -> List[Move]`

Get all legal moves.

```python
moves = board.get_legal_moves()
for move in moves:
    print(move.uci())
```

#### `get_fen() -> str`

Get board position in FEN notation.

```python
fen = board.get_fen()
print(f"Position: {fen}")
```

#### `get_move_san(move) -> str`

Convert move to standard algebraic notation.

```python
san = board.get_move_san(move)
print(f"Move: {san}")  # e.g., "e4", "Nf3", "Ke2"
```

#### `undo_move() -> Optional[Move]`

Undo the last move.

```python
move = board.undo_move()
if move:
    print(f"Undid move: {move.uci()}")
```

#### `copy() -> ChessBoard`

Create a copy of the board.

```python
board2 = board.copy()
board2.make_move_san("e4")
# board1 is unchanged
```

#### `is_checkmate() -> bool`

Check if position is checkmate.

```python
if board.is_checkmate():
    print("Game over - checkmate!")
```

#### `is_stalemate() -> bool`

Check if position is stalemate.

```python
if board.is_stalemate():
    print("Game over - stalemate!")
```

#### `is_check() -> bool`

Check if current side is in check.

```python
if board.is_check():
    print("King is in check!")
```

#### `is_game_over() -> bool`

Check if game is over (checkmate, stalemate, etc).

```python
if board.is_game_over():
    print("Game ended")
```

#### `turn() -> bool`

Get whose turn it is.

```python
if board.turn():
    print("White to move")
else:
    print("Black to move")
```

## OpeningBook

Opening book management.

### Initialization

```python
from src.opening_book import OpeningBook

book = OpeningBook()

# Load from file
book.load_book("data/opening_book.json")
```

### Methods

#### `get_move(fen) -> Optional[Move]`

Get suggested move from opening book.

```python
move = book.get_move(board.get_fen())
if move:
    print(f"Book move: {move.uci()}")
```

#### `add_opening(fen, move)`

Add a move to the opening book.

```python
import chess

fen = chess.STARTING_FEN
move = chess.Move.from_uci("e2e4")
book.add_opening(fen, move)
```

#### `save_book(filepath)`

Save opening book to file.

```python
book.save_book("data/my_opening_book.json")
```

#### `load_book(filepath)`

Load opening book from file.

```python
book.load_book("data/opening_book.json")
```

## ChessComBot

Chess.com bot for automated play.

### Initialization

```python
from src.chesscom_bot import ChessComBot
from src.engine import ChessEngine

engine = ChessEngine(depth=5, time_limit=2.0)
bot = ChessComBot("username", "password", engine)
```

### Methods

#### `login() -> bool`

Login to Chess.com.

```python
if bot.login():
    print("Logged in successfully")
else:
    print("Login failed")
```

#### `get_ongoing_games() -> List[Dict]`

Get list of ongoing games.

```python
games = bot.get_ongoing_games()
for game in games:
    print(f"Game {game['game_id']}: {game['time_class']}")
```

#### `get_game_state(game_id) -> Optional[Dict]`

Get current state of a game.

```python
state = bot.get_game_state("12345")
print(f"FEN: {state['fen']}")
print(f"Status: {state['game_status']}")
```

#### `make_move(game_id, move) -> bool`

Make a move in a game.

```python
import chess

move = chess.Move.from_uci("e2e4")
if bot.make_move("12345", move):
    print("Move made")
else:
    print("Move failed")
```

#### `get_best_move(fen, time_available) -> Optional[Move]`

Get best move for a position.

```python
move = bot.get_best_move(state['fen'], 2.0)
```

#### `play_game(game_id, max_moves=100)`

Play a single game.

```python
bot.play_game("12345")
```

#### `play_games(max_games=5)`

Play multiple games.

```python
bot.play_games(max_games=10)
```

## UCIInterface

UCI protocol interface for chess GUIs.

### Initialization

```python
from src.uci_interface import UCIInterface

interface = UCIInterface()
interface.run()
```

### Supported Commands

| Command | Example | Description |
|---------|---------|-------------|
| `uci` | `uci` | Identify engine |
| `isready` | `isready` | Check readiness |
| `setoption` | `setoption name Depth value 6` | Set option |
| `position` | `position startpos moves e2e4 e7e5` | Set position |
| `go` | `go wtime 30000 btime 30000` | Start search |
| `stop` | `stop` | Stop search |
| `quit` | `quit` | Exit |

### Example Session

```
> uci
id name Chess Engine Blitz
id author Chess Team
uciok

> setoption name Depth value 5
> position startpos
> go wtime 300000 btime 300000 movetime 2000
bestmove e2e4

> quit
```

## Module Imports

### Main Modules

```python
from src.engine import ChessEngine
from src.evaluation import Evaluator
from src.board import ChessBoard
from src.opening_book import OpeningBook
from src.chesscom_bot import ChessComBot
from src.uci_interface import UCIInterface
```

### Constants

```python
from src.evaluation import PIECE_VALUES, PAWN_PST, KNIGHT_PST
```

## Complete Example

```python
from src.engine import ChessEngine
from src.board import ChessBoard
from src.evaluation import Evaluator
import chess

# Create engine and board
engine = ChessEngine(depth=4, time_limit=2.0)
board = ChessBoard()

# Play a game
while not board.is_game_over():
    # Get legal moves
    if not board.get_legal_moves():
        break
    
    # Find best move
    best_move = engine.find_best_move(board.board)
    if best_move:
        board.make_move(best_move)
        print(f"Move: {board.get_move_san(best_move)}")
        
        # Evaluate position
        score = Evaluator.evaluate(board.board)
        print(f"Position: {score/100:.2f} pawns")
    else:
        break

print(f"Final FEN: {board.get_fen()}")
```

## Error Handling

All public methods return `None` or `False` on error. Check returns:

```python
move = engine.find_best_move(board)
if move is None:
    print("Error: No move found")

if not board.make_move(move):
    print("Error: Illegal move")

if not bot.login():
    print("Error: Login failed")
```
