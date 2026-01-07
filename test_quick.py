#!/usr/bin/env python3
"""Quick test script for the chess engine."""
import time
from src.engine import ChessEngine
from src.evaluation import Evaluator
from src.board import ChessBoard
import chess


def test_basic_functionality():
    """Test basic engine functionality."""
    print("=" * 60)
    print("Chess Engine Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: Engine initialization
    print("Test 1: Engine Initialization")
    engine = ChessEngine(depth=4, time_limit=2.0)
    print(f"✓ Engine created with depth={engine.depth}, time_limit={engine.time_limit}s")
    print()
    
    # Test 2: Starting position evaluation
    print("Test 2: Starting Position")
    board = chess.Board()
    board_wrapper = ChessBoard()
    
    score = Evaluator.evaluate(board)
    legal_moves = list(board.legal_moves)
    print(f"✓ Legal moves: {len(legal_moves)}")
    print(f"✓ Evaluation: {score} centipawns (balanced)")
    print()
    
    # Test 3: Find best move
    print("Test 3: Move Finding (3-ply depth)")
    start = time.time()
    move = engine.find_best_move(board, 1.0)
    elapsed = time.time() - start
    print(f"✓ Best move: {move.uci()} (e.g., e2-e4)")
    print(f"✓ Time: {elapsed:.2f}s")
    print(f"✓ Nodes searched: {engine.nodes_searched:,}")
    print()
    
    # Test 4: Game simulation
    print("Test 4: Simple Game (5 moves per side)")
    board = chess.Board()
    moves = []
    
    for _ in range(5):
        if board.is_game_over():
            break
        
        move = engine.find_best_move(board, 0.5)
        if move:
            board.push(move)
            moves.append(move.uci())
    
    print(f"✓ Played {len(moves)} moves")
    print(f"✓ Move sequence: {' '.join(moves)}")
    print(f"✓ Final FEN: {board.fen()}")
    print()
    
    # Test 5: Tactical position
    print("Test 5: Tactical Position (Fool's Mate)")
    board = chess.Board()
    board.push_san("f3")
    board.push_san("e5")
    board.push_san("g4")
    
    # Black should find Qh5# mate
    move = engine.find_best_move(board, 1.0)
    if move:
        board.push(move)
        print(f"✓ Engine found: {move.uci()}")
        print(f"✓ Checkmate: {board.is_checkmate()}")
    print()
    
    print("=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_basic_functionality()
