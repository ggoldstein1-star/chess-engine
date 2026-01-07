# Advanced Configuration and Optimization Guide

## Engine Tuning

### Search Depth Configuration

The search depth directly impacts both strength and speed:

```python
# For blitz (3+2)
engine = ChessEngine(depth=4, time_limit=1.5)

# For rapid (10+0)
engine = ChessEngine(depth=6, time_limit=4.0)

# For bullet (1+0)
engine = ChessEngine(depth=3, time_limit=0.5)
```

Estimated Elo by depth:
- Depth 3: ~1200-1400 Elo (bullet)
- Depth 4: ~1400-1600 Elo (blitz)
- Depth 5: ~1600-1800 Elo (blitz+)
- Depth 6: ~1800-2000 Elo (rapid)
- Depth 7: ~2000-2200 Elo (rapid+)

### Time Management

The engine uses iterative deepening to respect time limits:

```python
# 80% of available time is used for search
time_for_move = time_available * 0.8

# Automatic depth adjustment
# Stops searching when time limit is exceeded
```

For chess.com blitz (3+2):
- White has ~180 seconds per game
- Black has ~180 seconds per game
- Average ~30 moves per game = 6 seconds per move
- Recommend 2-3 second time limit per move

## Position Evaluation

### Material Count

Piece values (in centipawns):
```
Pawn:   100
Knight: 320
Bishop: 330
Rook:   500
Queen:  900
King:   Infinite
```

### Positional Factors

1. **Piece-Square Tables**: Each piece gets bonuses/penalties based on square
2. **King Safety**: Castling rights and king exposure
3. **Pawn Structure**: Advanced pawns, pawn storms
4. **Endgame Detection**: Positions with no queens use endgame king table

### Customizing Evaluation

Edit [src/evaluation.py](src/evaluation.py) to modify:
- Piece values
- Piece-square tables
- King safety coefficients
- Pawn structure bonuses

Example - increase pawn value:
```python
PIECE_VALUES = {
    chess.PAWN: 110,      # Increased from 100
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
}
```

## Search Algorithms

### Alpha-Beta Pruning

The engine uses alpha-beta pruning to reduce nodes searched:

```
Alpha: Lower bound of maximizing player's guaranteed score
Beta: Upper bound of minimizing player's guaranteed score
When Alpha >= Beta, the branch can be pruned
```

Typical cutoff rates:
- Depth 3: 80-85% of positions pruned
- Depth 4: 85-90% of positions pruned
- Depth 5+: 90-95% of positions pruned

### Move Ordering

Moves are sorted by likely strength to maximize pruning:

1. **Captures** (MVV-LVA): Most valuable victim, least valuable attacker
2. **Killer Moves**: Moves that caused cutoffs at this depth in sibling nodes
3. **History Heuristic**: Moves that were good in other positions
4. **Checks**: Forcing moves

Well-ordered moves can improve search speed by 3-5x.

### Transposition Table

Cached position evaluations to avoid re-evaluating:

```python
# Key: FEN string
# Value: (score, depth, flag)
transposition_table = {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": (0, 3, 'exact')
}
```

Hits reduce search time significantly in positions with many transpositions.

## Opening Book Enhancement

### Adding Openings

```python
from src.opening_book import OpeningBook
import chess

book = OpeningBook()

# Add position and move
fen = chess.STARTING_FEN
move = chess.Move.from_uci("e2e4")
book.add_opening(fen, move)

# Save to file
book.save_book("data/opening_book.json")
```

### Popular Openings to Add

```python
# Italian Game
book.add_opening(
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    chess.Move.from_uci("e8f6")  # Nf6
)

# Ruy Lopez
book.add_opening(
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    chess.Move.from_uci("b8c6")  # Nc6
)
```

## Chess.com Integration

### Authentication

The bot uses Chess.com API with basic authentication:

```python
bot = ChessComBot(username, password)
bot.login()
```

### Game Automation

```python
bot.play_games(max_games=10)
```

Time allocation for moves:
```python
our_time = player_info.get('remaining_time', 300)
time_for_move = min(our_time * 0.05, 3.0)  # 5% of remaining, max 3s
```

## UCI Protocol Details

### Supported Commands

| Command | Description |
|---------|-------------|
| `uci` | Identify engine |
| `isready` | Check if ready |
| `setoption` | Set engine options |
| `position` | Set board position |
| `go` | Start search |
| `stop` | Stop search |
| `quit` | Exit |

### Example UCI Session

```
> uci
id name Chess Engine Blitz
id author Chess Team
option name Depth type spin default 6 min 1 max 20
option name TimeLimit type spin default 3000 min 100 max 10000
uciok

> position startpos moves e2e4 e7e5
> go wtime 30000 btime 30000
bestmove g1f3
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run engine...
move = engine.find_best_move(board, 2.0)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(20)
```

### Common Bottlenecks

1. **Move Generation**: Use `board.legal_moves` (efficient in python-chess)
2. **Evaluation**: Cache with transposition table
3. **Alpha-Beta**: Good move ordering is critical
4. **Time Checking**: Only check time every 2048 nodes

### Optimization Tips

1. Use `board.copy()` for position backups (faster than undo/redo)
2. Cache legal moves to avoid regenerating
3. Increase transposition table for longer games
4. Use killer heuristic for dramatic pruning improvements
5. Implement iterative deepening to use time efficiently

## Debugging

### Engine Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Now log during search
logger.debug(f"Searching depth {depth} with alpha={alpha}, beta={beta}")
```

### Analyzing Games

```python
from src.engine import ChessEngine
import chess

engine = ChessEngine(depth=5, time_limit=5.0)  # Deep analysis

# Load game
game = chess.pgn.read_game(open('game.pgn'))
board = game.board()

# Analyze each move
for move_number, move in enumerate(game.mainline_moves()):
    engine_move = engine.find_best_move(board, 5.0)
    is_best = (move == engine_move)
    print(f"Move {move_number}: {move.uci()} - {'BEST' if is_best else 'BLUNDER'}")
    board.push(move)
```

## Benchmarking

Run benchmarks to measure performance:

```python
import time
from src.engine import ChessEngine
import chess

engine = ChessEngine(depth=4, time_limit=2.0)
board = chess.Board()

# Warm-up
for _ in range(3):
    engine.find_best_move(board, 1.0)

# Benchmark
times = []
for i in range(5):
    start = time.time()
    move = engine.find_best_move(board, 1.0)
    elapsed = time.time() - start
    times.append(elapsed)
    print(f"Run {i+1}: {elapsed:.2f}s, Nodes: {engine.nodes_searched:,}")

avg = sum(times) / len(times)
print(f"Average: {avg:.2f}s")
```

## Further Improvements

### Not Yet Implemented

1. **Iterative Deepening with Time Control**: Currently uses simple iterative deepening
2. **Quiescence Search**: Avoid horizon effect in tactical positions
3. **Endgame Tablebases**: Perfect play in endgames
4. **Multi-threading**: Parallel search with shared transposition table
5. **Neural Networks**: Use NNUE for faster evaluation
6. **PVS (Principal Variation Search)**: Better pruning than standard alpha-beta
7. **Null Move Pruning**: Aggressive pruning when not in check
8. **Aspiration Windows**: Narrow alpha-beta window for faster search

### Coming Soon

- [ ] Quiescence search for tactical positions
- [ ] More comprehensive opening book
- [ ] Multi-threaded search
- [ ] Better time management
- [ ] Support for Chess.com live analysis
