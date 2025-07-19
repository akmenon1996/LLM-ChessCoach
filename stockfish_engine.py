import chess
import chess.engine
import os

# Set STOCKFISH_PATH from environment or default path
STOCKFISH_PATH = os.getenv('STOCKFISH_PATH', 'stockfish')

def evaluate_game(pgn_path, depth=15):
    """Return a list of evaluations for each move in the game."""
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    evaluations = []
    with open(pgn_path) as f:
        game = chess.pgn.read_game(f)
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        score = info['score'].pov(board.turn)
        evaluations.append({
            'move': board.san(move),
            'score': score.score(mate_score=100000) if not score.is_mate() else score
        })
    engine.quit()
    return evaluations
