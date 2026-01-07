"""Chess engine with minimax and alpha-beta pruning."""
import chess
from typing import Tuple, Optional, Dict
from src.evaluation import Evaluator
from src.opening_book import OpeningBook
import time


class ChessEngine:
    """Advanced chess engine with alpha-beta pruning optimized for blitz."""
    
    def __init__(self, depth: int = 4, time_limit: float = 2.0):
        """
        Initialize the chess engine.
        
        Args:
            depth: Search depth in plies
            time_limit: Time limit for move calculation in seconds
        """
        self.depth = depth
        self.time_limit = time_limit
        self.nodes_searched = 0
        self.opening_book = OpeningBook()
        self.transposition_table: Dict[str, Tuple[int, int, int]] = {}  # FEN -> (score, depth, flag)
        self.killer_moves: Dict[int, list] = {}  # Depth -> [move1, move2]
        self.history: Dict[Tuple, int] = {}  # (from_square, to_square) -> score
    
    def find_best_move(self, board: chess.Board, time_available: float = None) -> Optional[chess.Move]:
        """
        Find the best move for the current position.
        
        Args:
            board: Current chess board state
            time_available: Time available for move in seconds
            
        Returns:
            Best move or None if no legal moves
        """
        # Try opening book first
        book_move = self.opening_book.get_move(board.fen())
        if book_move:
            return book_move
        
        if time_available:
            self.time_limit = time_available * 0.8  # Use 80% of available time
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        self.nodes_searched = 0
        start_time = time.time()
        
        best_move = None
        best_score = float('-inf')
        
        # Iterative deepening to respect time limit
        for current_depth in range(1, self.depth + 1):
            elapsed = time.time() - start_time
            if elapsed > self.time_limit:
                break
            
            for move in self._sort_moves(board, legal_moves):
                board.push(move)
                score = -self._alphabeta(
                    board, 
                    current_depth - 1, 
                    float('-inf'), 
                    float('inf'),
                    start_time
                )
                board.pop()
                
                if score > best_score:
                    best_score = score
                    best_move = move
                
                # Check time limit
                if time.time() - start_time > self.time_limit:
                    return best_move
        
        return best_move if best_move else legal_moves[0]
    
    def _alphabeta(
        self, 
        board: chess.Board, 
        depth: int, 
        alpha: float, 
        beta: float,
        start_time: float
    ) -> int:
        """
        Alpha-beta pruning algorithm.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            start_time: Start time for time management
            
        Returns:
            Score of position in centipawns
        """
        # Check time limit
        self.nodes_searched += 1
        if self.nodes_searched % 2048 == 0:
            if time.time() - start_time > self.time_limit:
                return Evaluator.evaluate(board)
        
        # Transposition table lookup
        fen = board.fen()
        if fen in self.transposition_table:
            trans_score, trans_depth, flag = self.transposition_table[fen]
            if trans_depth >= depth:
                return trans_score
        
        # Terminal nodes
        if depth == 0 or board.is_game_over():
            return Evaluator.evaluate(board)
        
        # Generate and sort moves
        legal_moves = list(board.legal_moves)
        legal_moves = self._sort_moves(board, legal_moves)
        
        if not legal_moves:
            if board.is_checkmate():
                return -100000
            return 0  # Stalemate
        
        max_score = float('-inf')
        
        for move in legal_moves:
            board.push(move)
            score = -self._alphabeta(board, depth - 1, -beta, -alpha, start_time)
            board.pop()
            
            max_score = max(max_score, score)
            alpha = max(alpha, score)
            
            if alpha >= beta:
                # Update killer moves
                if move not in self.killer_moves.get(depth, []):
                    if depth not in self.killer_moves:
                        self.killer_moves[depth] = []
                    self.killer_moves[depth].insert(0, move)
                    if len(self.killer_moves[depth]) > 2:
                        self.killer_moves[depth].pop()
                break  # Beta cutoff
        
        # Store in transposition table
        self.transposition_table[fen] = (max_score, depth, 'exact')
        
        return max_score
    
    def _sort_moves(self, board: chess.Board, moves: list) -> list:
        """
        Sort moves by estimated strength (for move ordering optimization).
        
        Args:
            board: Current board state
            moves: List of moves to sort
            
        Returns:
            Sorted list of moves
        """
        move_scores = []
        
        for move in moves:
            score = 0
            
            # Captures first (using MVV-LVA)
            if board.is_capture(move):
                victim_piece = board.piece_at(move.to_square)
                if victim_piece:
                    victim_value = PIECE_VALUES.get(victim_piece.piece_type, 0)
                    attacker_piece = board.piece_at(move.from_square)
                    attacker_value = PIECE_VALUES.get(attacker_piece.piece_type, 0) if attacker_piece else 0
                    score += 10000 + victim_value - attacker_value
            
            # Killer moves
            depth_key = self.depth - len(board.move_stack)
            for i, killer in enumerate(self.killer_moves.get(depth_key, [])):
                if move == killer:
                    score += 9000 - i * 100
            
            # History heuristic
            history_key = (move.from_square, move.to_square)
            score += self.history.get(history_key, 0)
            
            # Checks
            if board.gives_check(move):
                score += 1000
            
            move_scores.append((score, move))
        
        # Sort by score (descending)
        move_scores.sort(key=lambda x: x[0], reverse=True)
        return [move for _, move in move_scores]


# Import piece values for move ordering
from src.evaluation import PIECE_VALUES
