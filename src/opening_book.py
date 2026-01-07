"""Opening book for standard chess openings."""
import chess
from typing import Optional, Dict
import json
import os


class OpeningBook:
    """Manages opening book moves."""
    
    def __init__(self):
        """Initialize opening book with common moves."""
        self.book = self._create_book()
    
    def _create_book(self) -> Dict[str, list]:
        """Create opening book with common openings."""
        return {
            # Starting position
            chess.STARTING_FEN: [
                chess.Move.from_uci("e2e4"),  # 1.e4
                chess.Move.from_uci("d2d4"),  # 1.d4
                chess.Move.from_uci("c2c4"),  # 1.c4
                chess.Move.from_uci("g1f3"),  # 1.Nf3
            ],
        }
    
    def get_move(self, fen: str) -> Optional[chess.Move]:
        """
        Get a move from the opening book.
        
        Args:
            fen: Position FEN string
            
        Returns:
            Suggested move or None
        """
        if fen in self.book:
            moves = self.book[fen]
            if moves:
                # Return first move (can be randomized for variety)
                return moves[0]
        return None
    
    def add_opening(self, fen: str, move: chess.Move):
        """Add a move to the opening book."""
        if fen not in self.book:
            self.book[fen] = []
        if move not in self.book[fen]:
            self.book[fen].append(move)
    
    def save_book(self, filepath: str):
        """Save opening book to file."""
        # Convert moves to UCI strings for JSON serialization
        serializable_book = {}
        for fen, moves in self.book.items():
            serializable_book[fen] = [move.uci() for move in moves]
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(serializable_book, f, indent=2)
    
    def load_book(self, filepath: str):
        """Load opening book from file."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.book = {}
                for fen, uci_moves in data.items():
                    self.book[fen] = [chess.Move.from_uci(uci) for uci in uci_moves]
