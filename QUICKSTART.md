# Quick Start Guide for Borken Chess V2

## Installation

```bash
pip install -r requirements.txt
```

## Quick Test

Run the test suite to verify everything works:

```bash
python test_quick.py
```

Expected output:
```
============================================================
Borken Chess V2 Test Suite
============================================================

Test 1: Engine Initialization
✓ Engine created with depth=4, time_limit=2.0s

Test 2: Starting Position
✓ Legal moves: 20
✓ Evaluation: 0 centipawns (balanced)

Test 3: Move Finding (3-ply depth)
✓ Best move: e2e4 (e.g., e2-e4)
✓ Time: 0.XX s
✓ Nodes searched: X,XXX
...
```

## Playing Games

### CLI Mode (Interactive)
By default the engine now uses an external UCI engine (e.g., Stockfish) if available. To run interactive CLI:

```bash
python main.py cli
```

To force the built-in internal engine instead, use `--internal`:

```bash
python main.py --internal cli
```

Example session:
```
[Chess board display]
FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

> move e4
Moved: e4

> best
Best move: e5 (e5)
Nodes: 15234

> quit
```

### UCI Mode (for Chess GUIs)
```bash
python main.py uci
```

Then use with:
- Arena Chess GUI
- Lichess Analysis Board
- ChessTempo

### Playing on Chess.com
```bash
# First, set up your credentials
cp .env.example .env
# Edit .env with your Chess.com username and password

# Then run the bot (external engine is used by default)
python main.py bot myusername mypassword --depth 5 --games 10

To use an external engine binary at a specific path:

```bash
python main.py --engine-path /path/to/stockfish cli
```
```

## Performance Tips

1. **For Blitz (3+2)**
   - Use `--depth 4` or `--depth 5`
   - Each move should take ~1-2 seconds

2. **For Rapid (10+0)**
   - Use `--depth 6` or `--depth 7`
   - Can afford 3-5 seconds per move

3. **For Bullet (1+0)**
   - Use `--depth 3`
   - Limit to 0.5 seconds per move

## Key Files

- [main.py](main.py) - Entry point with CLI/UCI/Bot modes
- [src/engine.py](src/engine.py) - Core search algorithm
- [src/evaluation.py](src/evaluation.py) - Position evaluation
- [src/board.py](src/board.py) - Chess board representation

## Engine Features

- **Alpha-Beta Search**: Efficient minimax with pruning
- **Transposition Table**: Caches evaluated positions
- **Move Ordering**: MVV-LVA and killer moves
- **Piece-Square Tables**: Positional bonuses
- **Time Management**: Automatic time allocation for moves

## Customization

### Adjust Search Depth
Edit `ChessEngine(depth=5)` in main.py

### Change Evaluation Weights
Edit coefficients in [src/evaluation.py](src/evaluation.py)

### Add Opening Moves
Edit `_create_book()` in [src/opening_book.py](src/opening_book.py)

## Troubleshooting

**Engine is too slow:**
- Reduce depth: `--depth 3` or `--depth 4`
- Reduce time limit: `--time 1.0`

**Engine makes blunders:**
- Increase depth: `--depth 6` or `--depth 7`
- Add more opening book positions

**Chess.com login fails:**
- Verify username and password in .env
- Check Chess.com API availability
- Ensure network connection

## Next Steps

1. Run `python test_quick.py` to verify setup
2. Try `python main.py cli` for interactive play
3. Experiment with different depths and time limits
4. Read [README.md](README.md) for full documentation
