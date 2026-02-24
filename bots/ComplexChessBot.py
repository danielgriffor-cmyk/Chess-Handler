import chess
import random
import base.ChessBotBase as ChessBotBase
import math

class Bot(ChessBotBase.Bot):
    def name(self):
        return "Complex Chess Bot"

    def evaluate(self, board):

        if board.is_checkmate():
            return -math.inf if board.turn == self.color else math.inf
        
        score = 0
        pawn_val, knight_val, bishop_val, rook_val, queen_val = 10, 30, 35, 55, 100
        
        defend_mod = 0.015
        attacked_mod = 0.015
        attack_mod = 0.01

        distance_from_center_mod = 0.2
        opp_king_dist_mod = 1

        distance_of_kings_mod = 0.6

        pawn_distance_mod = 0.6

        king_walk_mod = 1

        coverage_mod = 0.1

        total_pieces = chess.popcount(board.occupied)

        beginning_bonus = 2 - min(total_pieces / 16, 1)
        middlegame_bonus = 2 - min(2 * abs(total_pieces / 16 - 1), 1)
        endgame_bonus = 1 + max(total_pieces / 16 - 1, 0)
        
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

        for target_square in opp_pawn_squares:
            attacker_score += len(board.attackers(self.color, target_square)) * pawn_val * attack_mod

        for target_square in opp_knight_squares:
            attacker_score += len(board.attackers(self.color, target_square)) * knight_val * attack_mod

        for target_square in opp_bishop_squares:
            attacker_score += len(board.attackers(self.color, target_square)) * bishop_val * attack_mod

        for target_square in opp_rook_squares:
            attacker_score += len(board.attackers(self.color, target_square)) * rook_val * attack_mod

        for target_square in opp_queen_squares:
            attacker_score += len(board.attackers(self.color, target_square)) * queen_val * attack_mod

        # -------------- CENTRAL CONTROL ------------------

        distance_score = 0

        for pos in piece_pos:
            dist = chess.square_distance(pos, 36)
            dist += chess.square_distance(pos, 37)
            dist += chess.square_distance(pos, 44)
            dist += chess.square_distance(pos, 45)
            distance_score += dist * distance_from_center_mod * beginning_bonus * middlegame_bonus

        # ------------------ KING WALKING -------------------

        king_walk_score = 0

        if self.color == chess.WHITE:
            king_walk_score += chess.square_rank(king_squares[0])
        else:
            king_walk_score += 8 - chess.square_rank(king_squares[0])

        # ----------------- CHECKMATING --------------------

        opp_king_dist = chess.square_distance(opp_king_squares[0], 36)
        opp_king_dist += chess.square_distance(opp_king_squares[0], 37)
        opp_king_dist += chess.square_distance(opp_king_squares[0], 44)
        opp_king_dist += chess.square_distance(opp_king_squares[0], 45)

        king_dists = chess.square_distance(opp_king_squares[0], king_squares[0])

        # ---------------- PAWN STRUCTURE ------------------

        pawn_distance = 0

        for pawn in pawn_squares:
            if self.color == chess.WHITE:
                pawn_distance += chess.square_rank(pawn)
            else:
                pawn_distance += 8 - chess.square_rank(pawn)

        # ------------------ MOVEMENT ---------------------

        attack_squares = set()

        for sq, piece in board.piece_map().items():
            if piece.color == self.color:
                attack_squares |= set(board.attacks(sq))

        coverage_score = len(attack_squares) * coverage_mod * middlegame_bonus * beginning_bonus

        pawn_distance_score = pawn_distance * pawn_distance_mod * beginning_bonus

        opp_king_score = opp_king_dist * opp_king_dist_mod * max(0, endgame_bonus - 1.7)
        
        king_dists_score = king_dists * distance_of_kings_mod * max(0, endgame_bonus - 1.7)

        king_walk_score *= king_walk_mod * ((endgame_bonus ** 2) - (beginning_bonus ** 2) - 1)

        material_score = (my_material - opponent_material) / middlegame_bonus

        score = (material_score + defended_score - attacked_score + attacker_score)
        
        score += (total_pieces * (middlegame_bonus - 1)) - distance_score

        score += opp_king_score - king_dists_score + coverage_score + pawn_distance_score

        if board.is_stalemate() or board.is_insufficient_material():
            return -score / 8

        return score

