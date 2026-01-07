"""Wrapper to use an external UCI engine (e.g., Stockfish) via python-chess.

Provides two helpers:
- `ExternalEngine`: simple per-move invocation (keeps compatibility)
- `PersistentExternalEngine`: keeps a UCI engine process alive for lower latency
"""
import atexit
from typing import Optional

import chess
import chess.engine


class ExternalEngine:
    """Simple wrapper around a UCI engine binary.

    The wrapper opens the engine for each move (safe) — kept for backwards
    compatibility. For better performance across many moves use
    `PersistentExternalEngine`.
    """

    def __init__(self, path: Optional[str] = None):
        # Default to `stockfish` on PATH if no path provided
        self.path = path or "stockfish"

    def find_best_move(self, board: chess.Board, time_available: float = 1.0) -> Optional[chess.Move]:
        """Ask the UCI engine for the best move given `board` and time."""
        try:
            with chess.engine.SimpleEngine.popen_uci(self.path) as eng:
                limit = chess.engine.Limit(time=time_available)
                result = eng.play(board, limit)
                return result.move
        except Exception:
            return None


class PersistentExternalEngine:
    """Keep an external UCI engine process alive for repeated queries.

    Usage:
        eng = PersistentExternalEngine('/usr/bin/stockfish')
        move = eng.find_best_move(board, 0.5)
        eng.close()
    """

    def __init__(self, path: Optional[str] = None, auto_register_close: bool = True):
        self.path = path or "stockfish"
        self._engine: Optional[chess.engine.SimpleEngine] = None
        self._start_engine()
        if auto_register_close:
            atexit.register(self.close)

    def _start_engine(self) -> None:
        # Try provided path first, then try to locate common stockfish binaries
        import shutil

        candidates = []
        if self.path:
            candidates.append(self.path)
        # prefer which result
        which_path = shutil.which("stockfish")
        if which_path:
            candidates.append(which_path)
        # Debian/Ubuntu common path
        candidates.extend(["/usr/games/stockfish", "/usr/bin/stockfish", "/usr/local/bin/stockfish"])

        for p in candidates:
            try:
                self._engine = chess.engine.SimpleEngine.popen_uci(p)
                return
            except Exception:
                self._engine = None
        # nothing succeeded
        self._engine = None

    def find_best_move(self, board: chess.Board, time_available: float = 0.6) -> Optional[chess.Move]:
        if self._engine is None:
            self._start_engine()
            if self._engine is None:
                return None

        try:
            limit = chess.engine.Limit(time=time_available)
            result = self._engine.play(board, limit)
            return result.move
        except Exception:
            return None

    def close(self) -> None:
        try:
            if self._engine is not None:
                self._engine.quit()
        finally:
            self._engine = None

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
