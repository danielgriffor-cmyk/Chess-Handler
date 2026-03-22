from base.ChessBotBase import Bot
import chess
import math

class Bot(Bot):
    def name(self):
        return "3Check Bot"

    def evaluate(self, board: chess.Board):
        score = 0
        if self.self_checks >= 3:
            return math.inf
        if self.op_checks >= 3:
            return -math.inf
        if board.is_checkmate():
            if self.color == board.turn:
                return -math.inf
            else:
                return math.inf
            
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            for square in board.pieces(piece_type, self.color):
                score += len(board.attacks(square))  # number of squares attacked
        
        return score
