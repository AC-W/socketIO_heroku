import chess.engine as en

class StockFish_AI:
    def __init__(self):
        self.engine = en.SimpleEngine.popen_uci("./stockfish_15_x64_avx2")
        
        print(self.engine)
    def make_move(self,board):
        info = self.engine.analyse(board, en.Limit(time=0.1))
        print(info)
        best_move = info.get('pv')[0]
        print(best_move)
        return best_move