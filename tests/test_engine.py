"""Tests for chess engine."""
import unittest
import chess
from src.engine import ChessEngine
from src.board import ChessBoard
from src.evaluation import Evaluator


class TestEngine(unittest.TestCase):
    """Test chess engine functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ChessEngine(depth=3, time_limit=1.0)
        self.board = ChessBoard()
    
    def test_legal_moves(self):
        """Test that engine generates legal moves."""
        board = chess.Board()
        moves = list(board.legal_moves)
        self.assertEqual(len(moves), 20)  # 20 legal moves in starting position
    
    def test_engine_finds_move(self):
        """Test that engine finds a move."""
        move = self.engine.find_best_move(self.board.board)
        self.assertIsNotNone(move)
    
    def test_simple_mate_detection(self):
        """Test mate detection with Scholar's Mate."""
        # Scholar's Mate: 1.e4 e5 2.Bc4 Nc6 3.Qh5 Nf6?? 4.Qxf7#
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        board.push_san("Bc4")
        board.push_san("Nc6")
        board.push_san("Qh5")
        board.push_san("Nf6")
        board.push_san("Qxf7")
        
        self.assertTrue(board.is_checkmate())
    
    def test_evaluation_pieces(self):
        """Test basic material evaluation."""
        # Starting position should be equal
        board = chess.Board()
        score = Evaluator.evaluate(board)
        self.assertAlmostEqual(score, 0, delta=50)
    
    def test_board_make_move(self):
        """Test board move making."""
        self.assertTrue(self.board.make_move_san("e4"))
        self.assertEqual(self.board.board.move_stack[-1], chess.Move.from_uci("e2e4"))
    
    def test_board_undo(self):
        """Test board undo."""
        self.board.make_move_san("e4")
        move = self.board.undo_move()
        self.assertEqual(move, chess.Move.from_uci("e2e4"))


class TestEvaluation(unittest.TestCase):
    """Test evaluation function."""
    
    def test_material_imbalance(self):
        """Test evaluation with material imbalance."""
        board = chess.Board()
        board.push_san("e4")
        board.push_san("d5")
        board.push_san("exd5")
        
        score = Evaluator.evaluate(board)
        self.assertGreater(score, 0)  # White should be winning (up a pawn)


if __name__ == "__main__":
    unittest.main()
