# your_bot.py
import chess
import random

# Import the base class from the other file
import base.ChessBotBase as BaseBot   # adjust filename/import if needed


class Bot(BaseBot.Bot):
    """
    Your specialized bot that uses the base search logic but with your
    original evaluation function (sped up + slightly tuned).
    """
    def __init__(self, color=chess.WHITE, depth=4):
        # Pass params to base — note: base defaults to BLACK & depth=2
        super().__init__(color=color, depth=depth, qsearch=False, qdepth=4)
        # You can keep qsearch=False since we're not using quiescence

        # Precompute constants for faster eval
        self.center_squares = {chess.D4, chess.E4, chess.D5, chess.E5}
        self.early_king_penalty_squares = {
            chess.D1, chess.E1, chess.D2, chess.E2,
            chess.D7, chess.E7, chess.D8, chess.E8
        }
        self.piece_values = {
            chess.PAWN:   100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK:   500,
            chess.QUEEN:  900,
            chess.KING:   0
        }

    def evaluate(self, board):
        """
        Your original evaluation logic — optimized + stalemate friendly.
        Called via self.main_eval() from the base search.
        """
        if board.is_checkmate():
            return -99999 if board.turn == self.color else 99999

        # Explicit stalemate/draw preference (very important for your goal)
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        piece_map = board.piece_map()           # cache once — big speedup
        total_pieces = len(piece_map)
        fullmove = board.fullmove_number

        score = 0

        for square, piece in piece_map.items():
            ptype = piece.piece_type
            p_val = self.piece_values.get(ptype, 0)

            same_color = (piece.color == self.color)

            # 1. Early Queen Penalty (your original)
            if ptype == chess.QUEEN and fullmove < 10:
                p_val -= 70

            # 2. Development Bonus
            if ptype in (chess.KNIGHT, chess.BISHOP):
                rank = chess.square_rank(square)
                if (piece.color == chess.WHITE and rank > 0) or \
                   (piece.color == chess.BLACK and rank < 7):
                    p_val += 30

            # 3. Center Control
            if square in self.center_squares:
                p_val += 40

            # 4. King Safety
            if ptype == chess.KING and total_pieces > 12:
                if square in self.early_king_penalty_squares:
                    p_val -= 60

            # 5. Pawn push in endgame
            if ptype == chess.PAWN and total_pieces < 10:
                rank = chess.square_rank(square)
                advance = rank if piece.color == chess.WHITE else 7 - rank
                p_val += advance * 10

            score += p_val if same_color else -p_val

        # Castling bonus
        if board.has_castling_rights(self.color):
            score += 25

        # Optional: your is_castled helper (if you still want it)
        if self.is_castled(board, self.color):
            score += 50

        return score

    def is_castled(self, board, color):
        """Your original helper — unchanged"""
        king_sq = board.king(color)
        if king_sq is None:
            return False
        if color == chess.WHITE:
            return king_sq in (chess.C1, chess.G1)
        return king_sq in (chess.C8, chess.G8)

    def openning(self, board):
        """
        Optional: you can override this if you want book moves.
        Returning None falls back to search (your original behavior).
        """
        # Example: force English as white
        if board.fullmove_number == 1 and self.color == chess.WHITE:
            m = chess.Move.from_uci("c2c4")
            if m in board.legal_moves:
                return m
        return None   # use normal search

    def name(self):
        return f"Your Chess Bot (depth {self.depth})"