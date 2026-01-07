"""Chess board representation and move handling."""
import chess
from typing import List, Tuple, Optional


class ChessBoard:
    """Wrapper around python-chess board with additional utilities."""
    
    def __init__(self, fen: str = chess.STARTING_FEN):
        """Initialize board with optional FEN string."""
        self.board = chess.Board(fen)
        self.move_stack = []
    
    def make_move(self, move: chess.Move) -> bool:
        """Make a move on the board."""
        if move in self.board.legal_moves:
            self.board.push(move)
            self.move_stack.append(move)
            return True
        return False
    
    def make_move_san(self, san_move: str) -> bool:
        """Make a move from SAN notation."""
        try:
            move = self.board.parse_san(san_move)
            return self.make_move(move)
        except (ValueError, chess.InvalidMoveError):
            return False
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get list of legal moves."""
        return list(self.board.legal_moves)
    
    def get_fen(self) -> str:
        """Get current board FEN."""
        return self.board.fen()
    
    def is_checkmate(self) -> bool:
        """Check if position is checkmate."""
        return self.board.is_checkmate()
    
    def is_stalemate(self) -> bool:
        """Check if position is stalemate."""
        return self.board.is_stalemate()
    
    def is_check(self) -> bool:
        """Check if current side is in check."""
        return self.board.is_check()
    
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self.board.is_game_over()
    
    def turn(self) -> bool:
        """Return True if white to move, False if black."""
        return self.board.turn
    
    def copy(self) -> 'ChessBoard':
        """Create a copy of the board."""
        new_board = ChessBoard()
        new_board.board = self.board.copy()
        new_board.move_stack = self.move_stack.copy()
        return new_board
    
    def undo_move(self) -> Optional[chess.Move]:
        """Undo the last move."""
        if self.board.move_stack:
            move = self.board.pop()
            if self.move_stack:
                self.move_stack.pop()
            return move
        return None
    
    def get_move_san(self, move: chess.Move) -> str:
        """Get SAN notation for a move."""
        return self.board.san(move)
