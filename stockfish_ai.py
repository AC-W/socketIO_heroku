import chess
import chess.pgn
import chess.engine

class StockFish_AI:
    def __init__(self):
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish_15_x64_avx2.exe")

    def make_move(self,board):
        info = self.engine.analyse(board, chess.engine.Limit(time=0.1))
        best_move = info.get('pv')[0]
        return best_move