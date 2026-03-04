import chess
import random
import base.ChessBotBase as ChessBotBase
import math

class Bot(ChessBotBase.Bot):
    def name(self):
        return "Complex Chess Bot"

    def openning(self, board):
        fen = str(board.fen().split(" ")[0])
        move = None
        if self.turn > 1:
            return None
        if fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": #empty
            move = ["e2e4", "d2d4", "c2c4", "g1f3", "b1c3"][random.randint(0, 4)]
        elif fen == "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": #e4
            move = "e7e5"
        elif fen == "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR": #e3
            move = "e7e5"
        elif fen == "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": #d4
            move = "d7d5"
        elif fen == "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R": #Nf3
            move = "c7c5"
        elif fen == "rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR": #Nc3
            move = "d7d5"
        elif fen == "rnbqkbnr/pppppppp/8/8/8/3P4/PPP1PPPP/RNBQKBNR": #d3
            move = "e7e5"
        elif fen == "rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR": #f4
            move = "g8f6"
        elif fen == "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR": #c4
            move = "e7e5"
        elif fen == "rnbqkbnr/pppppppp/8/8/8/1P6/P1PPPPPP/RNBQKBNR": #b3
            move = "e7e5"
        elif self.turn == 1:
            move = "e7e5"
        if move == None:
            return None
        return chess.Move.from_uci(move)
            

    def evaluate(self, board):

        if board.is_checkmate():
            return -math.inf if board.turn == self.color else math.inf
        
        score = 0

        # ------------------- MODIFIERS ------------------

        pawn_val, knight_val, bishop_val, rook_val, queen_val = 1, 3, 3.5, 5.5, 10

        defend_mod = 0.0075
        attacked_mod = 0.0075
        attack_mod = 0.005
        
        king_walk_mod = 0.02
        opp_king_dist_mod = 0.03
        distance_of_kings_mod = 0.06

        pawn_distance_mod = 0.01

        distance_from_center_mod = -0.0002
        center_control_mod = 0.002
        opp_center_control_mod = 0.0015

        coverage_mod = 0.04

        # ----------------- GAME PROGRESSION BONUSES -----------------

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

        material_score = (my_material - opponent_material) / middlegame_bonus + (my_material / opponent_material)

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
            dist = chess.square_distance(pos, chess.E4)
            dist += chess.square_distance(pos, chess.E5)
            dist += chess.square_distance(pos, chess.D4)
            dist += chess.square_distance(pos, chess.D5)
            distance_score += dist * distance_from_center_mod * beginning_bonus * middlegame_bonus

        central_control = len(board.attackers(self.color, chess.E4)) * center_control_mod
        central_control += len(board.attackers(self.color, chess.E5)) * center_control_mod
        central_control += len(board.attackers(self.color, chess.D4)) * center_control_mod
        central_control += len(board.attackers(self.color, chess.D5)) * center_control_mod

        central_control -= len(board.attackers(not self.color, chess.E4)) * opp_center_control_mod
        central_control -= len(board.attackers(not self.color, chess.E5)) * opp_center_control_mod
        central_control -= len(board.attackers(not self.color, chess.D4)) * opp_center_control_mod
        central_control -= len(board.attackers(not self.color, chess.D5)) * opp_center_control_mod

        central_control *= beginning_bonus

        # ------------------ KING WALKING -------------------

        king_walk_score = 0

        if self.color == chess.WHITE:
            king_walk_score += chess.square_rank(king_squares[0])
        else:
            king_walk_score += 8 - chess.square_rank(king_squares[0])

        king_walk_score *= king_walk_mod * ((endgame_bonus ** 2) - (beginning_bonus ** 2) - 1)
        

        # ----------------- CHECKMATING --------------------

        opp_king_dist = chess.square_distance(opp_king_squares[0], 36)
        opp_king_dist += chess.square_distance(opp_king_squares[0], 37)
        opp_king_dist += chess.square_distance(opp_king_squares[0], 44)
        opp_king_dist += chess.square_distance(opp_king_squares[0], 45)

        king_dists = chess.square_distance(opp_king_squares[0], king_squares[0])
        
        opp_king_score = opp_king_dist * opp_king_dist_mod * max(0, endgame_bonus - 1.7)

        king_dists_score = king_dists * distance_of_kings_mod * max(0, endgame_bonus - 1.7)

        # ---------------- PAWN STRUCTURE ------------------

        pawn_distance = 0

        for pawn in pawn_squares:
            if self.color == chess.WHITE:
                pawn_distance += chess.square_rank(pawn)
            else:
                pawn_distance += 8 - chess.square_rank(pawn)

        pawn_distance_score = pawn_distance * pawn_distance_mod * beginning_bonus

        # -------------------- MOVEMENT ------------------------

        attack_squares = set()

        for sq, piece in board.piece_map().items():
            if piece.color == self.color:
                attack_squares |= set(board.attacks(sq))

        coverage_score = len(attack_squares) * coverage_mod * middlegame_bonus * beginning_bonus

        # ----------------------- SCORING ------------------------

        score = (material_score + defended_score - attacked_score + attacker_score)
        
        score += (total_pieces * (middlegame_bonus - 1)) - distance_score

        score += opp_king_score - king_dists_score + coverage_score + pawn_distance_score

        score += central_control

        if board.is_stalemate() or board.is_insufficient_material():
            return -score / 8

        return score

