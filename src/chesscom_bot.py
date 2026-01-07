"""Chess.com bot integration for automated play."""
import requests
import json
import time
from typing import Optional, Dict
from src.engine import ChessEngine
from src.board import ChessBoard
import chess
import logging

logger = logging.getLogger(__name__)


class ChessComBot:
    """Bot for playing on Chess.com."""
    
    def __init__(self, username: str, password: str, engine: ChessEngine = None):
        """
        Initialize Chess.com bot.
        
        Args:
            username: Chess.com username
            password: Chess.com password
            engine: ChessEngine instance
        """
        self.username = username
        self.password = password
        self.engine = engine or ChessEngine(depth=5, time_limit=2.0)
        self.session = requests.Session()
        self.is_logged_in = False
        self.game_in_progress = False
        self.current_game_id = None
    
    def login(self) -> bool:
        """
        Login to Chess.com.
        
        Returns:
            True if login successful
        """
        try:
            # Chess.com API authentication
            auth = (self.username, self.password)
            response = self.session.get(
                "https://www.chess.com/api/user",
                auth=auth
            )
            
            if response.status_code == 200:
                self.is_logged_in = True
                logger.info(f"Successfully logged in as {self.username}")
                return True
            else:
                logger.error(f"Login failed with status code {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def get_ongoing_games(self) -> list:
        """
        Get list of ongoing games.
        
        Returns:
            List of game data
        """
        if not self.is_logged_in:
            return []
        
        try:
            response = self.session.get(
                f"https://www.chess.com/api/user/{self.username}/games"
            )
            
            if response.status_code == 200:
                data = response.json()
                # Filter for ongoing games
                ongoing = [g for g in data.get('games', []) if g.get('game_status') == 'playing']
                return ongoing
            return []
        except Exception as e:
            logger.error(f"Error fetching games: {e}")
            return []
    
    def get_game_state(self, game_id: str) -> Optional[Dict]:
        """
        Get current state of a game.
        
        Args:
            game_id: Chess.com game ID
            
        Returns:
            Game state data or None
        """
        try:
            response = self.session.get(
                f"https://www.chess.com/api/game/{game_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error fetching game state: {e}")
            return None
    
    def make_move(self, game_id: str, move: chess.Move) -> bool:
        """
        Make a move in a game.
        
        Args:
            game_id: Chess.com game ID
            move: Move to make
            
        Returns:
            True if move successful
        """
        try:
            move_uci = move.uci()
            response = self.session.post(
                f"https://www.chess.com/api/game/{game_id}/move",
                json={"move": move_uci}
            )
            
            if response.status_code == 200:
                logger.info(f"Move {move_uci} made in game {game_id}")
                return True
            else:
                logger.error(f"Failed to make move: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error making move: {e}")
            return False
    
    def get_best_move(self, fen: str, time_available: float) -> Optional[chess.Move]:
        """
        Get the best move for a position.
        
        Args:
            fen: Position FEN
            time_available: Time available for calculation
            
        Returns:
            Best move
        """
        board = chess.Board(fen)
        return self.engine.find_best_move(board, time_available)
    
    def play_game(self, game_id: str, max_moves: int = 100):
        """
        Play a single game.
        
        Args:
            game_id: Chess.com game ID
            max_moves: Maximum moves to play before giving up
        """
        self.current_game_id = game_id
        self.game_in_progress = True
        
        moves_played = 0
        
        while moves_played < max_moves and self.game_in_progress:
            try:
                game_state = self.get_game_state(game_id)
                if not game_state:
                    break
                
                # Check if game is still active
                if game_state.get('game_status') != 'playing':
                    logger.info(f"Game {game_id} ended")
                    self.game_in_progress = False
                    break
                
                # Check if it's our turn
                fen = game_state.get('fen')
                board = chess.Board(fen)
                
                # Get time available
                player_info = game_state.get('players', {})
                our_color = 'white' if game_state.get('user_color') == 'w' else 'black'
                our_time = player_info.get(our_color, {}).get('remaining_time', 300)
                
                # Calculate time for move (blitz: ~2 seconds, bullet: ~0.5 seconds)
                time_for_move = min(our_time * 0.05, 3.0)  # Use 5% of remaining time, max 3 seconds
                
                # Get best move
                best_move = self.get_best_move(fen, time_for_move)
                
                if best_move:
                    if self.make_move(game_id, best_move):
                        moves_played += 1
                    else:
                        logger.error("Failed to make move")
                        break
                else:
                    logger.error("No legal move found")
                    break
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            except Exception as e:
                logger.error(f"Error during gameplay: {e}")
                break
        
        self.game_in_progress = False
        logger.info(f"Finished playing game {game_id} ({moves_played} moves)")
    
    def play_games(self, max_games: int = 5):
        """
        Play multiple games.
        
        Args:
            max_games: Maximum games to play
        """
        if not self.is_logged_in:
            if not self.login():
                logger.error("Cannot play games - not logged in")
                return
        
        games_played = 0
        
        while games_played < max_games:
            games = self.get_ongoing_games()
            
            if not games:
                logger.info("No ongoing games found")
                time.sleep(5)
                continue
            
            for game in games:
                game_id = game.get('game_id')
                time_class = game.get('time_class', 'blitz')
                
                logger.info(f"Starting game {game_id} ({time_class})")
                self.play_game(game_id)
                
                games_played += 1
                if games_played >= max_games:
                    break
                
                # Rest between games
                time.sleep(2)
        
        logger.info(f"Completed {games_played} games")
