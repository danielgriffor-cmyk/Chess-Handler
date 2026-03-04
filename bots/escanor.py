from base.ChessBotBase import Bot
import chess
import random
import math

class Bot(Bot):
    def name(self):
        return "Escanor, The Lion's Sin of Pride"
    def count_captures_on_moved_piece(self, board):
              move = board.peek()
              moved_to = move.to_square

              moved_to = move.to_square
              ene_color = not self.color
              Attackers = board.attackers(ene_color, moved_to)
              Attackcount = len(Attackers)                
              return float(Attackcount)
    def is_queen_trade(self, board):
        move = board.peek()
        moved_to = move.to_square
        piece = board.piece_at(move.from_square)
        target = board.piece_at(move.to_square)

        # Must be queen capturing queen
        if not piece or not target:
            return False
        if piece.piece_type != chess.QUEEN:
            return False
        if target.piece_type != chess.QUEEN:
            return False

        # Simulate the move to see if opponent can recapture
        temp = board.copy()
        temp.push(move)

        # Opponent recaptures on the same square?
        recaptures = temp.attackers(not self.color, move.to_square)
        return len(recaptures) > 0
    def count_defenses_on_moved_piece(self, board):
              move = board.peek()
              moved_to = move.to_square

              moved_to = move.to_square
              my_color = self.color
              defenders = board.attackers(my_color, moved_to)
              defendcount = len(defenders)                
              return float(defendcount)
    def count_pieces_on_my_side(self, board):
              if self.color == chess.WHITE:
                  my_side = range(0, 32)   # ranks 1–4
              else:
                  my_side = range(32, 64)  # ranks 5–8
              enemy = not self.color
              count = 0.0
              for sq in my_side:
                  piece = board.piece_at(sq)
                  if piece and piece.color == enemy:
                      count += 1.0

              return count
    def count_defended_pieces(self, board):
        my_color = board.turn
        count = 0.0

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == my_color:
                if board.is_attacked_by(my_color, square):
                    count += 1.0

        return count
    def count_my_pieces_on_ENE_side(self, board):
              if self.color == chess.WHITE:
                  ene_side = range(32, 64)   # ranks 1–4
              else:
                  ene_side = range(0, 32)  # ranks 5–8
              me = self.color
              count = 0.0
              for sq in ene_side:
                  piece = board.piece_at(sq)
                  if piece and piece.color == me:
                      count += 1.0

              return count
    def dowereallycareaboutthatpiece(self, board):
            my_color = self.color
            enemy_color = not my_color

            # Locate my queen
            queen_square = None
            for sq in board.pieces(chess.QUEEN, my_color):
                queen_square = sq
                break

            if queen_square is None:
                return 0  # queen already gone

            # If queen is attacked, penalize heavily
            if board.is_attacked_by(enemy_color, queen_square):
                return -300  # negative because it's bad

            return 0
    def dowereallycarethosepieces(self, board):
        my_color = self.color
        enemy_color = not my_color

        # Basic piece values (you can tune these)
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 300,
            chess.BISHOP: 300,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000  # king danger is huge
        }

        total_penalty = 0

        # Loop through all pieces of my color
        for piece_type in piece_values:
            for square in board.pieces(piece_type, my_color):

                # Count attackers on this square
                attackers = len(board.attackers(enemy_color, square))

                if attackers > 0:
                    # Penalty scales with piece value and number of attackers
                    penalty = attackers * piece_values[piece_type] // 4
                    total_penalty -= penalty

        return total_penalty
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
        # Checkmate / stalemate
        if board.is_checkmate():
            return -math.inf if board.turn == self.color else math.inf

        if board.is_stalemate():
            return -math.inf * 2

        cycle = (self.turn // 12) % 2
        pride_mode = (cycle == 0)

        score = 0

        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 1200,
        }

        material_self = 0
        material_opp = 0

        for pt in piece_values:
            material_self += len(board.pieces(pt, self.color)) * piece_values[pt]
            material_opp += len(board.pieces(pt, not self.color)) * piece_values[pt]

        material_score = material_self - material_opp

        
        # Queen trade veto if behind
        if material_score < 0 and self.is_queen_trade(board):
            score -= 5000

        pride_multiplier = 1.0 * max(
            1.0,
            self.count_defenses_on_moved_piece(board) + self.count_captures_on_moved_piece(board)
        )

        if pride_mode:
            score += material_score

            mobility_self = len(list(board.legal_moves))
            temp = board.copy()
            temp.turn = not board.turn
            mobility_opp = len(list(temp.legal_moves))

            score += (mobility_self - mobility_opp) * 20 + self.dowereallycareaboutthatpiece(board)
            score += material_score + (self.count_my_pieces_on_ENE_side(board) * 10) * pride_multiplier

        else:
            mobility_self = len(list(board.legal_moves))

            score -= self.count_pieces_on_my_side(board) * 60
            score += self.count_my_pieces_on_ENE_side(board) * 15
            score += self.count_defended_pieces(board) * 40
            score -= self.count_captures_on_moved_piece(board) * 40
            score += (material_score * 1.2)
            score += mobility_self * 10
            score += self.dowereallycarethosepieces(board)

        return score