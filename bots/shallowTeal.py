import math
import random
import chess
from base.ChessBotBase import Bot

pawn_val, knight_val, bishop_val, rook_val, queen_val = 10, 30, 35, 55, 100 # starts at 421

class Bot(Bot):
    def name(self):
        return "Shallow Teal"
    
    def getPieceValue(self, piece):

        if piece == chess.PAWN:
            return pawn_val
        elif piece == chess.KNIGHT:
            return knight_val
        elif piece == chess.BISHOP:
            return bishop_val
        elif piece == chess.ROOK:
            return rook_val
        elif piece == chess.QUEEN:
            return queen_val
        elif piece == chess.KING:
            return math.inf
        else:
            return 0

    def evaluate(self, board: chess.Board):
        score = 0

        stalemate_threshold = -30
        center_control_multiplier = 20
        king_safety_multiplier = 40
        attack_multiplier = 1

        my_material = (
            len(board.pieces(chess.PAWN, self.color)) * pawn_val +
            len(board.pieces(chess.KNIGHT, self.color)) * knight_val +
            len(board.pieces(chess.BISHOP, self.color)) * bishop_val +
            len(board.pieces(chess.ROOK, self.color)) * rook_val +
            len(board.pieces(chess.QUEEN, self.color)) * queen_val
        ) + 1
        
        opponent_material = (
            len(board.pieces(chess.PAWN, not self.color)) * pawn_val +
            len(board.pieces(chess.KNIGHT, not self.color)) * knight_val +
            len(board.pieces(chess.BISHOP, not self.color)) * bishop_val +
            len(board.pieces(chess.ROOK, not self.color)) * rook_val +
            len(board.pieces(chess.QUEEN, not self.color)) * queen_val
        ) + 1

        board.turn = not board.turn
        score += 0.15 if board.is_check() else 0
        board.turn = not board.turn

        score += (my_material / opponent_material) * 100
        
        center_control = 0

        center_control += center_control_multiplier * len(board.attackers(self.color, chess.E5))
        center_control += center_control_multiplier * len(board.attackers(self.color, chess.D4))
        center_control += center_control_multiplier * len(board.attackers(self.color, chess.D5))
        center_control += center_control_multiplier * len(board.attackers(self.color, chess.E4))
        
        center_control -= center_control_multiplier * len(board.attackers(not self.color, chess.E5))
        center_control -= center_control_multiplier * len(board.attackers(not self.color, chess.D4))
        center_control -= center_control_multiplier * len(board.attackers(not self.color, chess.D5))
        center_control -= center_control_multiplier * len(board.attackers(not self.color, chess.E4))

        king_safety = 0

        if my_material >= 230:
            if self.color == chess.WHITE:
                king_safety -= king_safety_multiplier * chess.square_rank(board.king(self.color))
            else:
                king_safety -= king_safety_multiplier * (7 - chess.square_rank(board.king(self.color)))

        score += king_safety

        

        for piece_type in chess.PIECE_TYPES:
            for trade_square in board.pieces(piece_type, self.color):
                attackers_value = []
                defenders_value = []
                attackers = 0
                defenders = 0
                for attacker in board.attackers(not self.color, trade_square):
                    attackers += 1
                    attackers_value.append(self.getPieceValue(board.piece_at(attacker)))
                for defender in board.attackers(self.color, trade_square):
                    defenders += 1
                    defenders_value.append(self.getPieceValue(board.piece_at(defender)))
                trade_length = min(defenders + 1, attackers)
                attackers_value.sort()
                defenders_value.sort()
                attackers_value = attackers_value[:(trade_length - 1)]
                defenders_value = defenders_value[:(trade_length - 1)]
                attackers_value = sum(attackers_value) * attack_multiplier
                defenders_value = sum(defenders_value) * attack_multiplier
                score += (attackers_value - defenders_value)



        if board.is_checkmate():
            return -math.inf if board.turn == self.color else math.inf
        elif board.is_repetition(3):
            return math.inf if score < stalemate_threshold else -math.inf
            
        return score