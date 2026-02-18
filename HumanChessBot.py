import chess
import random
import ChessBotBase
import math

class Bot(ChessBotBase.Bot):
    def evaluate(self, board):
        
        if board.is_checkmate():
            # Faster mate is better, slower mate is worse
            return 1e9
        
        score = 0
        pawn_val, knight_val, bishop_val, rook_val, queen_val = 10, 30, 35, 55, 100
        defend_mod = 0.05
        attacked_mod = 0.05
        attack_mod = -0.03

        total_pieces = chess.popcount(board.occupied)

        endgame_bonus = 1 + max(total_pieces / 16 - 1, 0)
        beginning_bonus = 2 - min(total_pieces / 16, 1)
        middlegame_bonus = 2 - min(2 * abs(total_pieces / 16 - 1), 1)
        
        # ---------------- MATERIAL -----------------
        my_material = (
            len(board.pieces(chess.PAWN, self.color)) * pawn_val +
            len(board.pieces(chess.KNIGHT, self.color)) * knight_val +
            len(board.pieces(chess.BISHOP, self.color)) * bishop_val +
            len(board.pieces(chess.ROOK, self.color)) * rook_val +
            len(board.pieces(chess.QUEEN, self.color)) * queen_val
        )
        
        opponent_material = (
            len(board.pieces(chess.PAWN, not self.color)) * pawn_val +
            len(board.pieces(chess.KNIGHT, not self.color)) * knight_val +
            len(board.pieces(chess.BISHOP, not self.color)) * bishop_val +
            len(board.pieces(chess.ROOK, not self.color)) * rook_val +
            len(board.pieces(chess.QUEEN, not self.color)) * queen_val
        )

        # ---------------- ATTACKERS/DEFENDERS -----------------

        king_squares = list(board.pieces(chess.KING, self.color))
        queen_squares = list(board.pieces(chess.QUEEN, self.color))
        rook_squares = list(board.pieces(chess.ROOK, self.color))
        bishop_squares = list(board.pieces(chess.BISHOP, self.color))
        knight_squares = list(board.pieces(chess.KNIGHT, self.color))
        pawn_squares = list(board.pieces(chess.PAWN, self.color))

        # Combine all lists of squares
        piece_pos = king_squares + queen_squares + rook_squares + bishop_squares + knight_squares + pawn_squares

        defended_score = 0
        attacked_score = 0

        for target_square in pawn_squares:
            defended_score += len(board.attackers(self.color, target_square)) * pawn_val * defend_mod
            attacked_score += len(board.attackers(not self.color, target_square)) * pawn_val * attacked_mod

        for target_square in knight_squares:
            defended_score += len(board.attackers(self.color, target_square)) * knight_val * defend_mod
            attacked_score += len(board.attackers(not self.color, target_square)) * knight_val * attacked_mod

        for target_square in bishop_squares:
            defended_score += len(board.attackers(self.color, target_square)) * bishop_val * defend_mod
            attacked_score += len(board.attackers(not self.color, target_square)) * bishop_val * attacked_mod

        for target_square in rook_squares:
            defended_score += len(board.attackers(self.color, target_square)) * rook_val * defend_mod
            attacked_score += len(board.attackers(not self.color, target_square)) * rook_val * attacked_mod

        for target_square in queen_squares:
            defended_score += len(board.attackers(self.color, target_square)) * queen_val * defend_mod
            attacked_score += len(board.attackers(not self.color, target_square)) * queen_val * attacked_mod

        # ---------------- ATTACKING -----------------

        opp_king_squares = list(board.pieces(chess.KING, not self.color))
        opp_queen_squares = list(board.pieces(chess.QUEEN, not self.color))
        opp_rook_squares = list(board.pieces(chess.ROOK, not self.color))
        opp_bishop_squares = list(board.pieces(chess.BISHOP, not self.color))
        opp_knight_squares = list(board.pieces(chess.KNIGHT, not self.color))
        opp_pawn_squares = list(board.pieces(chess.PAWN, not self.color))

        # Combine all lists of squares
        opp_piece_pos = opp_king_squares + opp_queen_squares + opp_rook_squares + opp_bishop_squares + opp_knight_squares + opp_pawn_squares

        attacker_score = 0

        for target_square in pawn_squares:
            attacker_score += len(board.attackers(not self.color, target_square)) * pawn_val * attack_mod

        for target_square in knight_squares:
            attacker_score += len(board.attackers(not self.color, target_square)) * knight_val * attack_mod

        for target_square in bishop_squares:
            attacker_score += len(board.attackers(not self.color, target_square)) * bishop_val * attack_mod

        for target_square in rook_squares:
            attacker_score += len(board.attackers(not self.color, target_square)) * rook_val * attack_mod

        for target_square in queen_squares:
            attacker_score += len(board.attackers(not self.color, target_square)) * queen_val * attack_mod

        material_score = (my_material - opponent_material) * endgame_bonus * beginning_bonus

        score = (material_score + defended_score - attacked_score + attacker_score) - (total_pieces * middlegame_bonus)

        if board.is_stalemate() or board.is_insufficient_material():
            return -score
        
        return score

