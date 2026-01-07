"""Board evaluation and position scoring."""
import chess
from typing import Dict

# Piece values (in centipawns)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,  # King value is infinite
}

# Piece-square tables for better positional evaluation
PAWN_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_PST = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0,
]

QUEEN_PST = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

KING_PST_MID = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20,
]

KING_PST_END = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
]

PST_TABLES = {
    chess.PAWN: PAWN_PST,
    chess.KNIGHT: KNIGHT_PST,
    chess.BISHOP: BISHOP_PST,
    chess.ROOK: ROOK_PST,
    chess.QUEEN: QUEEN_PST,
}


class Evaluator:
    """Evaluates chess positions."""
    
    @staticmethod
    def is_endgame(board: chess.Board) -> bool:
        """Determine if position is in endgame."""
        queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + \
                 len(board.pieces(chess.QUEEN, chess.BLACK))
        rooks = len(board.pieces(chess.ROOK, chess.WHITE)) + \
                len(board.pieces(chess.ROOK, chess.BLACK))
        
        # Endgame if no queens and less than 2 rooks total
        return queens == 0 and rooks <= 1
    
    @staticmethod
    def evaluate(board: chess.Board) -> int:
        """
        Evaluate the position from white's perspective.
        Positive score = white advantage, negative = black advantage.
        Returns score in centipawns.
        """
        if board.is_checkmate():
            # If white to move and checkmate, white lost
            return -100000 if board.turn else 100000
        
        if board.is_stalemate():
            return 0
        
        score = 0
        is_endgame = Evaluator.is_endgame(board)
        
        # Heavy penalty if in check - opponent has tactical advantage
        if board.is_check():
            score -= 200
        
        # Material count
        for piece_type in PIECE_VALUES:
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            score += (white_count - black_count) * PIECE_VALUES[piece_type]
        
        # Piece-square tables
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            
            value = 0
            if piece.piece_type == chess.KING:
                pst = KING_PST_END if is_endgame else KING_PST_MID
            else:
                pst = PST_TABLES.get(piece.piece_type, [0] * 64)
            
            # Flip board perspective for black pieces
            square_idx = square if piece.color == chess.WHITE else 63 - square
            value = pst[square_idx]
            
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
        
        # Bonus for king safety
        score += Evaluator._king_safety(board)
        
        # Bonus for pawn structure
        score += Evaluator._pawn_structure(board)
        
        # Evaluate tactical threats
        score += Evaluator._threats(board)
        
        return score
    
    @staticmethod
    def _king_safety(board: chess.Board) -> int:
        """Evaluate king safety."""
        score = 0
        
        # White king safety
        white_king = board.king(chess.WHITE)
        white_shield = len(board.pieces(chess.PAWN, chess.WHITE))
        
        # Black king safety
        black_king = board.king(chess.BLACK)
        black_shield = len(board.pieces(chess.PAWN, chess.BLACK))
        
        # Bonus for castling rights
        if board.has_kingside_castling_rights(chess.WHITE):
            score += 25
        if board.has_queenside_castling_rights(chess.WHITE):
            score += 20
        if board.has_kingside_castling_rights(chess.BLACK):
            score -= 25
        if board.has_queenside_castling_rights(chess.BLACK):
            score -= 20
        
        return score
    
    @staticmethod
    def _pawn_structure(board: chess.Board) -> int:
        """Evaluate pawn structure."""
        score = 0
        
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        # Bonus for advanced pawns
        for pawn in white_pawns:
            rank = chess.square_rank(pawn)
            score += (rank - 1) * 5
        
        for pawn in black_pawns:
            rank = chess.square_rank(pawn)
            score -= (6 - rank) * 5
        
        return score
    
    @staticmethod
    def _threats(board: chess.Board) -> int:
        """Evaluate threats and tactical opportunities."""
        score = 0
        
        # Bonus for opponent's pieces under attack
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            
            # Count attacking moves on this piece
            attackers = len(board.attackers(not piece.color, square))
            defenders = len(board.attackers(piece.color, square))
            
            piece_value = PIECE_VALUES.get(piece.piece_type, 0)
            
            # If piece is under attack and undefended, penalize opponent
            if attackers > defenders and defenders == 0:
                if piece.color == chess.WHITE:
                    score -= piece_value // 2
                else:
                    score += piece_value // 2
        
        return score
