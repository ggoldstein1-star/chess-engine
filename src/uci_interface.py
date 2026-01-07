"""UCI (Universal Chess Interface) protocol implementation."""
import chess
from typing import Optional
from src.engine import ChessEngine
import sys
import time


class UCIInterface:
    """Implements UCI protocol for chess engine communication."""
    
    def __init__(self):
        """Initialize UCI interface."""
        self.engine = ChessEngine(depth=6, time_limit=3.0)
        self.board = chess.Board()
        self.is_ready = False
        self.search_stop = False
    
    def run(self):
        """Main UCI loop."""
        while True:
            try:
                line = input().strip()
                if not line:
                    continue
                
                self._handle_command(line)
            
            except EOFError:
                break
            except Exception as e:
                print(f"error: {e}", file=sys.stderr)
    
    def _handle_command(self, command: str):
        """Handle UCI command."""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "uci":
            self._cmd_uci()
        elif cmd == "isready":
            self._cmd_isready()
        elif cmd == "setoption":
            self._cmd_setoption(parts)
        elif cmd == "ucinewgame":
            self._cmd_ucinewgame()
        elif cmd == "position":
            self._cmd_position(parts)
        elif cmd == "go":
            self._cmd_go(parts)
        elif cmd == "stop":
            self._cmd_stop()
        elif cmd == "quit":
            self._cmd_quit()
        else:
            print(f"Unknown command: {cmd}")
    
    def _cmd_uci(self):
        """Handle 'uci' command."""
        print("id name Borken Chess V2")
        print("id author Borken Team")
        print("option name Depth type spin default 6 min 1 max 20")
        print("option name TimeLimit type spin default 3000 min 100 max 10000")
        print("uciok")
    
    def _cmd_isready(self):
        """Handle 'isready' command."""
        self.is_ready = True
        print("readyok")
    
    def _cmd_setoption(self, parts: list):
        """Handle 'setoption' command."""
        if len(parts) >= 5 and parts[1].lower() == "name":
            option_name = parts[2].lower()
            if option_name == "depth" and parts[3].lower() == "value":
                self.engine.depth = int(parts[4])
            elif option_name == "timelimit" and parts[3].lower() == "value":
                self.engine.time_limit = int(parts[4]) / 1000.0
    
    def _cmd_ucinewgame(self):
        """Handle 'ucinewgame' command."""
        self.board = chess.Board()
        self.engine.transposition_table.clear()
    
    def _cmd_position(self, parts: list):
        """Handle 'position' command."""
        if len(parts) < 2:
            return
        
        if parts[1] == "startpos":
            self.board = chess.Board()
            move_start = 3 if len(parts) > 2 and parts[2] == "moves" else len(parts)
        elif parts[1] == "fen":
            fen = " ".join(parts[2:8])
            self.board = chess.Board(fen)
            move_start = 8 if len(parts) > 8 and parts[8] == "moves" else len(parts)
        else:
            return
        
        # Apply moves
        if move_start < len(parts):
            for move_uci in parts[move_start:]:
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in self.board.legal_moves:
                        self.board.push(move)
                except:
                    pass
    
    def _cmd_go(self, parts: list):
        """Handle 'go' command."""
        self.search_stop = False
        
        # Parse time controls
        time_available = self.engine.time_limit
        
        for i, part in enumerate(parts[1:]):
            if part == "wtime" and i + 2 < len(parts):
                if self.board.turn:  # White to move
                    time_available = int(parts[i + 2]) / 1000.0
            elif part == "btime" and i + 2 < len(parts):
                if not self.board.turn:  # Black to move
                    time_available = int(parts[i + 2]) / 1000.0
            elif part == "depth" and i + 2 < len(parts):
                self.engine.depth = int(parts[i + 2])
            elif part == "movetime" and i + 2 < len(parts):
                time_available = int(parts[i + 2]) / 1000.0
        
        # Find best move
        best_move = self.engine.find_best_move(self.board, time_available)
        
        if best_move:
            print(f"bestmove {best_move.uci()}")
        else:
            print("bestmove (none)")
    
    def _cmd_stop(self):
        """Handle 'stop' command."""
        self.search_stop = True
    
    def _cmd_quit(self):
        """Handle 'quit' command."""
        sys.exit(0)


def main():
    """Run UCI interface."""
    interface = UCIInterface()
    interface.run()


if __name__ == "__main__":
    main()
