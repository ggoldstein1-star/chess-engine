#!/usr/bin/env python3
"""Main entry point for chess engine."""
import argparse
import sys
import logging
from typing import Optional

from src.engine import ChessEngine
from src.board import ChessBoard
from src.uci_interface import UCIInterface
from src.chesscom_bot import ChessComBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def play_against_engine(use_external: bool = False, engine_path: Optional[str] = None):
    """Play a full game against the engine."""
    import chess

    if use_external:
        # Use persistent engine for lower latency across moves
        from src.external_engine import PersistentExternalEngine

        engine = PersistentExternalEngine(engine_path)
    else:
        engine = ChessEngine(depth=5, time_limit=2.5)

    board = ChessBoard()

    # Choose color
    print("\n" + "=" * 50)
    print("PLAY AGAINST THE CHESS ENGINE")
    print("=" * 50)
    print("\nChoose your color:")
    print("  1 - White (you play first)")
    print("  2 - Black (engine plays first)")

    while True:
        choice = input("\nEnter 1 or 2: ").strip()
        if choice in ["1", "2"]:
            user_white = choice == "1"
            break
        print("Invalid choice. Enter 1 or 2.")

    print("\n" + "=" * 50)
    print(f"You are playing as {'White' if user_white else 'Black'}")
    print("Enter moves in algebraic notation (e.g., e4, Nf3, O-O)")
    print("Type 'quit' to exit\n")

    move_count = 0

    try:
        while not board.is_game_over():
            # Show board and position
            print(board.board)
            print(f"Move {move_count // 2 + 1}. ", end="")

            is_white = board.turn()
            is_user_turn = (is_white and user_white) or (not is_white and not user_white)

            if is_user_turn:
                # User's turn
                player_color = "White" if is_white else "Black"
                while True:
                    move_input = input(f"{player_color} to move > ").strip()

                    if move_input.lower() == "quit":
                        print("Game ended by user.")
                        return

                    if board.make_move_san(move_input):
                        move_count += 1
                        break
                    else:
                        print(f"Invalid move '{move_input}'. Try again.")

            else:
                # Engine's turn
                engine_color = "White" if is_white else "Black"
                engine_move = engine.find_best_move(board.board, 0.6)

                if engine_move:
                    san = board.get_move_san(engine_move)
                    board.make_move(engine_move)
                    move_count += 1
                    print(f"{engine_color} plays: {san}")
                    print()
                else:
                    print("Engine has no legal moves.")
                    break

    finally:
        # Game over / cleanup
        print("\n" + "=" * 50)
        print("GAME OVER")
        print("=" * 50)
        print(board.board)

        if board.is_checkmate():
            print("Checkmate!")
            winner = "Black" if board.board.turn else "White"
            print(f"{winner} wins!")
        elif board.is_stalemate():
            print("Stalemate - Draw!")
        else:
            print("Game ended.")

        print(f"\nFinal FEN: {board.get_fen()}\n")

        # If engine is a persistent external engine, ensure it's closed
        try:
            close_fn = getattr(engine, "close", None)
            if callable(close_fn):
                close_fn()
        except Exception:
            pass


def cli_mode(use_external: bool = False, engine_path: Optional[str] = None):
    """Interactive CLI mode for testing engine."""
    if use_external:
        from src.external_engine import PersistentExternalEngine

        engine = PersistentExternalEngine(engine_path)
    else:
        engine = ChessEngine(depth=5, time_limit=2.0)

    board = ChessBoard()

    print("\n" + "=" * 50)
    print("CHESS ENGINE - CLI MODE")
    print("=" * 50)
    print("\nCommands:")
    print("  play          - Play a full game against the engine")
    print("  move <san>    - Make a move (e.g., move e4)")
    print("  best          - Get best move suggestion")
    print("  eval          - Evaluate current position")
    print("  fen           - Show FEN string")
    print("  undo          - Undo last move")
    print("  new           - Start new position")
    print("  quit          - Exit")
    print()

    try:
        while True:
            print(board.board)
            print(f"FEN: {board.get_fen()}")

            user_input = input(" > ").strip().lower()

            if not user_input:
                continue

            parts = user_input.split()
            cmd = parts[0]

            if cmd == "play":
                play_against_engine(use_external=use_external, engine_path=engine_path)
                board = ChessBoard()

            elif cmd == "quit":
                break

            elif cmd == "new":
                board = ChessBoard()
                print("New game started")

            elif cmd == "move" and len(parts) > 1:
                if board.make_move_san(parts[1]):
                    print(f"✓ Moved: {parts[1]}")
                else:
                    print("✗ Invalid move")

            elif cmd == "fen":
                print(board.get_fen())

            elif cmd == "eval":
                from src.evaluation import Evaluator

                score = Evaluator.evaluate(board.board)
                advantage = "White" if score > 0 else "Black" if score < 0 else "Equal"
                print(f"Position: {advantage}")
                print(f"Score: {score/100:+.2f} pawns")

            elif cmd == "best":
                move = engine.find_best_move(board.board, 0.6)
                if move:
                    print(f"✓ Best move: {board.get_move_san(move)} ({move.uci()})")
                    nodes = getattr(engine, "nodes_searched", None)
                    if nodes is not None:
                        print(f"  Nodes searched: {nodes:,}")
                else:
                    print("No moves available")

            elif cmd == "undo":
                move = board.undo_move()
                if move:
                    print(f"✓ Undid: {board.get_move_san(move)}")
                else:
                    print("No moves to undo")

            else:
                print("Unknown command. Type 'help' for commands.")

            print()

    finally:
        # Close persistent engine if present
        close_fn = getattr(engine, "close", None)
        if callable(close_fn):
            try:
                close_fn()
            except Exception:
                pass


def uci_mode():
    """UCI protocol mode for use with other GUIs."""
    interface = UCIInterface()
    interface.run()


def bot_mode(username: str, password: str, depth: int, max_games: int, use_external: bool = False, engine_path: Optional[str] = None):
    """Play on Chess.com."""
    if use_external:
        from src.external_engine import PersistentExternalEngine

        engine = PersistentExternalEngine(engine_path)
    else:
        engine = ChessEngine(depth=depth, time_limit=2.0)
    bot = ChessComBot(username, password, engine)

    if bot.login():
        bot.play_games(max_games)
    else:
        print("Failed to login to Chess.com")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Chess Engine specialized for blitz chess"
    )

    parser.add_argument("--internal", action="store_true", help="Use internal built-in engine instead of external UCI engine")
    parser.add_argument("--engine-path", default=None, help="Path to UCI engine binary (default: stockfish on PATH)")
    subparsers = parser.add_subparsers(dest="mode", help="Mode of operation")

    # CLI mode (default)
    subparsers.add_parser("cli", help="Interactive CLI mode")

    # UCI mode
    subparsers.add_parser("uci", help="UCI protocol mode")

    # Chess.com bot mode
    bot_parser = subparsers.add_parser("bot", help="Play on Chess.com")
    bot_parser.add_argument("username", help="Chess.com username")
    bot_parser.add_argument("password", help="Chess.com password")
    bot_parser.add_argument("--depth", type=int, default=5, help="Search depth (default: 5)")
    bot_parser.add_argument("--games", type=int, default=5, help="Number of games to play (default: 5)")

    args = parser.parse_args()

    # Default behavior: use external UCI engine (e.g., stockfish).
    use_external = not bool(args.internal)

    if args.mode == "uci":
        uci_mode()
    elif args.mode == "bot":
        bot_mode(args.username, args.password, args.depth, args.games, use_external=use_external, engine_path=args.engine_path)
    else:
        # Default to CLI mode
        cli_mode(use_external=use_external, engine_path=args.engine_path)


if __name__ == "__main__":
    main()
