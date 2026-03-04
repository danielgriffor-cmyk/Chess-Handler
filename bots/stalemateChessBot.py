from base.ChessBotBase import Bot
import chess

class Bot(Bot):
    def name(self):
        return "Stalemate Bot"

    def evaluate(self, board):
        if board.is_stalemate():
            return 100
        return 0
