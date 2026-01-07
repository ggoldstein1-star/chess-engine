#!/usr/bin/env python3
"""
Example usage of the chess engine in various modes.
"""

from src.engine import ChessEngine
from src.board import ChessBoard
from src.evaluation import Evaluator
from src.opening_book import OpeningBook
import chess


def example_1_basic_search():
    """Example 1: Find the best move in a position."""
    print("=" * 60)
    print("Example 1: Basic Move Search")
    print("=" * 60)
    
    # Create engine
    engine = ChessEngine(depth=4, time_limit=1.0)
    
    # Starting position
    board = chess.Board()
    
    # Find best move
    move = engine.find_best_move(board, time_available=1.0)
    
    print(f"Best move: {move.uci()}")
    print(f"Nodes searched: {engine.nodes_searched:,}")
    print()


def example_2_position_evaluation():
    """Example 2: Evaluate different positions."""
    print("=" * 60)
    print("Example 2: Position Evaluation")
    print("=" * 60)
    
    # Starting position
    board = chess.Board()
    score = Evaluator.evaluate(board)
    print(f"Starting position: {score} cp ({score/100:.2f} pawns)")
    
    # After 1.e4
    board.push_san("e4")
    score = Evaluator.evaluate(board)
    print(f"After 1.e4: {score} cp")
    
    # After 1.e4 c5
    board.push_san("c5")
    score = Evaluator.evaluate(board)
    print(f"After 1.e4 c5 (Sicilian): {score} cp")
    
    # Tactical position - White is up material
    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nxe5")  # White captures pawn
    score = Evaluator.evaluate(board)
    print(f"White up a pawn: {score} cp (should be ~100)")
    print()


def example_3_game_simulation():
    """Example 3: Simulate a game between engine and itself."""
    print("=" * 60)
    print("Example 3: Game Simulation")
    print("=" * 60)
    
    engine = ChessEngine(depth=3, time_limit=0.5)
    board = ChessBoard()
    move_count = 0
    
    while not board.is_game_over() and move_count < 20:
        # Get best move
        move = engine.find_best_move(board.board, time_available=0.5)
        
        if not move:
            break
        
        # Make move
        board.make_move(move)
        move_count += 1
        
        # Print position
        san = board.get_move_san(move)
        print(f"Move {(move_count+1)//2}: {san}")
    
    print(f"Game ended after {move_count} moves")
    print(f"Final FEN: {board.get_fen()}")
    print()


def example_4_opening_book():
    """Example 4: Using the opening book."""
    print("=" * 60)
    print("Example 4: Opening Book")
    print("=" * 60)
    
    book = OpeningBook()
    board = chess.Board()
    
    # Get book move
    move = book.get_move(board.fen())
    print(f"Book move from starting position: {move.uci() if move else 'None'}")
    
    # Add custom opening
    book.add_opening(
        chess.STARTING_FEN,
        chess.Move.from_uci("d2d4")
    )
    
    # Save book
    # book.save_book("data/my_opening_book.json")
    print("Added 1.d4 to opening book")
    print()


def example_5_custom_position():
    """Example 5: Analyze a custom position."""
    print("=" * 60)
    print("Example 5: Custom Position Analysis")
    print("=" * 60)
    
    # Set up a position (Scholar's Mate setup)
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Bc4")
    board.push_san("Nc6")
    board.push_san("Qh5")
    
    print("Position: Scholar's Mate Trap")
    print(board)
    print()
    
    # Analyze what Black should do
    engine = ChessEngine(depth=5, time_limit=2.0)
    best_move = engine.find_best_move(board, time_available=2.0)
    
    if best_move:
        print(f"Black's best move: {board.san(best_move)}")
        print(f"This should be Nf6 (defending)")
    
    # Evaluate if Black plays Nf6??
    board.push_san("Nf6")
    score = Evaluator.evaluate(board)
    print(f"After Nf6: Score = {score} cp (should be very negative - Black losing)")
    print()


def example_6_time_management():
    """Example 6: Engine with different time controls."""
    print("=" * 60)
    print("Example 6: Time Management")
    print("=" * 60)
    
    board = chess.Board()
    
    # Blitz settings
    print("Blitz (3+2):")
    engine_blitz = ChessEngine(depth=4, time_limit=1.5)
    move = engine_blitz.find_best_move(board, time_available=1.5)
    print(f"Move: {move.uci()}, Time: quick\n")
    
    # Rapid settings
    print("Rapid (10+0):")
    engine_rapid = ChessEngine(depth=6, time_limit=4.0)
    move = engine_rapid.find_best_move(board, time_available=4.0)
    print(f"Move: {move.uci()}, Time: thoughtful\n")
    
    # Bullet settings
    print("Bullet (1+0):")
    engine_bullet = ChessEngine(depth=3, time_limit=0.5)
    move = engine_bullet.find_best_move(board, time_available=0.5)
    print(f"Move: {move.uci()}, Time: instant\n")


def example_7_comparing_positions():
    """Example 7: Compare engine evaluation across variations."""
    print("=" * 60)
    print("Example 7: Variation Comparison")
    print("=" * 60)
    
    # Italian Game: Two different responses
    board_main = chess.Board()
    board_main.push_san("e4")
    board_main.push_san("e5")
    board_main.push_san("Nf3")
    board_main.push_san("Nc6")
    board_main.push_san("Bc4")
    
    print("After 1.e4 e5 2.Nf3 Nc6 3.Bc4")
    
    # Main line: d6
    board_d6 = board_main.copy()
    board_d6.push_san("d6")
    score_d6 = Evaluator.evaluate(board_d6)
    print(f"3...d6 (Conservative): {score_d6} cp")
    
    # Aggressive: Nf6
    board_nf6 = board_main.copy()
    board_nf6.push_san("Nf6")
    score_nf6 = Evaluator.evaluate(board_nf6)
    print(f"3...Nf6 (Aggressive): {score_nf6} cp")
    
    # Rare: Nd4
    board_nd4 = board_main.copy()
    board_nd4.push_san("Nd4")
    score_nd4 = Evaluator.evaluate(board_nd4)
    print(f"3...Nd4 (Tactical): {score_nd4} cp")
    
    print(f"\nBest for Black: {'d6' if score_d6 > max(score_nf6, score_nd4) else 'Nf6' if score_nf6 > score_nd4 else 'Nd4'}")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "Chess Engine Examples" + " " * 25 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    examples = [
        ("Basic Move Search", example_1_basic_search),
        ("Position Evaluation", example_2_position_evaluation),
        ("Game Simulation", example_3_game_simulation),
        ("Opening Book", example_4_opening_book),
        ("Custom Position", example_5_custom_position),
        ("Time Management", example_6_time_management),
        ("Variation Comparison", example_7_comparing_positions),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
            input(f"Press Enter to continue to example {i+1}...\n")
        except KeyboardInterrupt:
            print("\n\nExamples interrupted.")
            break
        except Exception as e:
            print(f"Error in {name}: {e}\n")
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
