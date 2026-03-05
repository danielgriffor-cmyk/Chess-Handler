from base.ChessBotBase import Bot as BotBase
import chess

class Bot(BotBase):
    def name(self):
        return "Kamikaze Gambiter Bot"
    
    def image(self):
        return "icons/KamikazeGambiterBotIcon.png"

    def evaluate(self, board):
        """
        Kamikaze Gambiter strategy:
        Prefer positions where opponent has more material (we sacrificed ours).
        Avoid checkmate and try to develop then sacrifice pieces.
        """
        opponent = not self.color

        # Basic piece values
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
        }

        # --- Safety: avoid getting mated ---
        if board.turn == self.color and board.is_checkmate():
            return -1_000_000
        if board.turn == self.color and board.is_check():
            return -10_000

        # Count material for both sides
        our_material = sum(len(board.pieces(pt, self.color)) * v for pt, v in piece_values.items())
        opp_material = sum(len(board.pieces(pt, opponent)) * v for pt, v in piece_values.items())

        # Reward pieces we've already lost (permanent credit for sacrifices)
        starting_counts = {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}
        material_lost = 0
        for pt, start in starting_counts.items():
            curr = len(board.pieces(pt, self.color))
            lost = max(0, start - curr)
            material_lost += lost * piece_values[pt]

        score = material_lost * 50000  # permanent reward for captures we've made

        # Also favor positions where opponent has more material right now
        score += (opp_material - our_material) * 2000

        # Bonus for hanging pieces (attacked and not protected)
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece is not None and piece.color == self.color:
                val = piece_values.get(piece.piece_type, 0)
                attacked = board.is_attacked_by(opponent, sq)
                protected = board.is_attacked_by(self.color, sq)
                if attacked and not protected:
                    score += val * 5000

                # Penalty for pieces still on starting rank (force development)
                rank = chess.square_rank(sq)
                if (self.color == chess.WHITE and (rank == 0 or (rank == 1 and piece.piece_type == chess.PAWN))) or \
                   (self.color == chess.BLACK and (rank == 7 or (rank == 6 and piece.piece_type == chess.PAWN))):
                    score -= val * 2000

        return int(score)