import chess
import random
import base.ChessBotBase as ChessBotBase
import math


#[Base, Beginning, Middle, End]

PAWN = [1, 0, 0, 0]
PAWN_DEVELOPMENT_MOD = [0, 2, 1, 0.15]

KNIGHT = [3, 0, 0, 0]
KNIGHT_DEVELOPMENT_MOD = [0, 3, 2, 0.25]

BISHOP = [4, 0, 0, 0]
BISHOP_DEVELOPMENT_MOD = [0, 2, 3, 0.25]

ROOK = [6, 0, 0, 0]
ROOK_DEVELOPMENT_MOD = [0, -2, 2, 7]

QUEEN = [11, 0, -2, 1]
QUEEN_DEVELOPMENT_MOD = [0, -10, 2, 9]

SIMPLIFICATION_MOD = [0, 0, 0, 0]


MATERIAL_MOD = [1, 0.5, -0.2, 3]
OP_MATERIAL_MOD = [-1.05, -0.5, 0.2, 0]

DEVELOP_MOD = [0.75, 0, 0, 0]
OP_DEVELOP_MOD = [0.70, 0, 0, 0]

COVERAGE_MOD = [0.0025, 0, 0, 0]
OP_COVERAGE_MOD = [-0.003, 0, 0, 0]

ATTACKED_MOD = [-0.1, 0, 0, 0]
OP_ATTACKED_MOD = [0.1, 0, 0, 0]

DEFENDED_MOD = [0.1, 0, 0, 0]
OP_DEFENDED_MOD = [-0.1, 0, 0, 0]


TEMPO_MOD = [1, 0.15, 0.05, 0.10]

KINGSIDE_CASTLE_MOD = [0.5, 0.5, 1, 1.5]
QUEENSIDE_CASTLE_MOD = [0.5, 0.5, 1, 1.5]

OPPOSITE_CASTLE_MOD = [0, 0.2, 0.3, 0.4]

EMPTY = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]

PAWN_TABLE = [EMPTY, [
     0,  0,  0,  0,  0,  0,  0,  0,  # rank 1
     5, 10, 10,-20,-20, 10, 10,  5,  # rank 2
     5, -5,-10,  0,  0,-10, -5,  5,  # rank 3
     0,  0,  0, 20, 20,  0,  0,  0,  # rank 4
     5,  5, 10, 25, 25, 10,  5,  5,  # rank 5
    10, 10, 20, 30, 30, 20, 10, 10,  # rank 6
    50, 50, 50, 50, 50, 50, 50, 50,  # rank 7
     0,  0,  0,  0,  0,  0,  0,  0,  # rank 8
], [
      0,   0,   0,   0,   0,   0,   0,   0,  # rank 1
     10,  10,  10, -60, -60,  10,  10,  10,  # rank 2
    -40, -30, -20, -10, -10, -20, -30, -40,  # rank 3
     10,  20,  30,  40,  40,  30,  20,  10,  # rank 4
      0,  10,  10,  20,  20,  10,  10,   0,  # rank 5
     20,  30,  30,  50,  50,  30,  30,  20,  # rank 6
     50,  60,  60,  70,  70,  60,  60,  50,  # rank 7
      0,   0,   0,   0,   0,   0,   0,   0,  # rank 8
], [
      0,   0,   0,   0,   0,   0,   0,   0,  # rank 1
    -30, -30, -20, -10, -10, -20, -30, -30,  # rank 2
    -20,   0,   0,  10,  10,   0,   0, -20,  # rank 3
      0,  10,  10,  20,  20,  10,  10,   0,  # rank 4
     10,  20,  30,  30,  30,  20,  20,  10,  # rank 5
     20,  30,  40,  50,  50,  40,  30,  20,  # rank 6
     50,  60,  80,  90,  90,  80,  60,  50,  # rank 7
      0,   0,   0,   0,   0,   0,   0,   0,  # rank 8
] ]

KNIGHT_TABLE = [[
    -50,-40,-30,-30,-30,-30,-40,-50,  # rank 1
    -40,-20,  0,  5,  5,  0,-20,-40,  # rank 2
    -30,  5, 10, 15, 15, 10,  5,-30,  # rank 3
    -30,  0, 15, 20, 20, 15,  0,-30,  # rank 4
    -30,  5, 15, 20, 20, 15,  5,-30,  # rank 5
    -30,  0, 10, 15, 15, 10,  0,-30,  # rank 6
    -40,-20,  0,  0,  0,  0,-20,-40,  # rank 7
    -50,-40,-30,-30,-30,-30,-40,-50,  # rank 8
], EMPTY, EMPTY, EMPTY]

BISHOP_TABLE = [[
    -20,-10,-10,-10,-10,-10,-10,-20,  # rank 1
    -10,  5,  0,  0,  0,  0,  5,-10,  # rank 2
    -10, 10, 10, 10, 10, 10, 10,-10,  # rank 3
    -10,  0, 10, 10, 10, 10,  0,-10,  # rank 4
    -10,  5,  5, 10, 10,  5,  5,-10,  # rank 5
    -10,  0,  5, 10, 10,  5,  0,-10,  # rank 6
    -10,  0,  0,  0,  0,  0,  0,-10,  # rank 7
    -20,-10,-10,-10,-10,-10,-10,-20,  # rank 8
], EMPTY, EMPTY, EMPTY]

ROOK_TABLE = [EMPTY, [
     0,  0,  0,  5,  5,  0,  0,  0,  # rank 1
    -5,  0,  0,  0,  0,  0,  0, -5,  # rank 2
    -5,  0,  0,  0,  0,  0,  0, -5,  # rank 3
    -5,  0,  0,  0,  0,  0,  0, -5,  # rank 4
    -5,  0,  0,  0,  0,  0,  0, -5,  # rank 5
    -5,  0,  0,  0,  0,  0,  0, -5,  # rank 6
     5, 10, 10, 10, 10, 10, 10,  5,  # rank 7
     0,  0,  0,  0,  0,  0,  0,  0,  # rank 8
], [
    -40, -30,  20,  20,  20,  20, -30, -40,  # rank 1
    -20,   0,   0,   0,   0,   0,   0, -20,  # rank 2
    -20,   0,   0,   0,   0,   0,   0, -20,  # rank 3
    -20,   0,   0,  10,  10,   0,   0, -20,  # rank 4
    -10,   0,  10,  10,  10,  10,   0, -10,  # rank 5
    -10,   0,  10,  20,  20,  10,   0, -10,  # rank 6
      0,  30,  40,  50,  50,  40,  30,   0,  # rank 7
    -30, -10,   0,   0,   0,   0, -10, -30,  # rank 8
], [
     25,  10,   0,   0,   0,   0,  10,  25,  # rank 1
     10,   5,  10,  20,  20,  10,   5,  10,  # rank 2
    -40,   0,  10,  20,  20,  10,   0, -40,  # rank 3
    -20,   0,  10,  20,  20,  10,   0, -20,  # rank 4
    -20,   0,  10,  20,  20,  10,   0, -20,  # rank 5
    -40,   0,  10,  20,  20,  10,   0, -40,  # rank 6
      5,  10,  40,  50,  50,  40,  10,   5,  # rank 7
     10,   5,  10,   0,   0,  10,   5,  10,  # rank 8
] ]

QUEEN_TABLE = [EMPTY, [
      0,  10,  20,  60,  60,  20,  10,   0,  # rank 1
    -10, -20, -20, -30, -30, -20, -20, -10,  # rank 2
    -10,   0, -10, -10, -10, -10,   0, -10,  # rank 3
     10, -10, -10, -10, -10, -10, -10,  10,  # rank 4
     10,   0,   0,   0,   0,   0,   0,  10,  # rank 5
    -20, -30, -30, -10, -10, -30, -30, -20,  # rank 6
    -10,   0,  10,  10,  10,  10,   0, -10,  # rank 7
      0, -10,   0,   0,   0,   0, -10,   0,  # rank 8
], [
    -20,-10,-10, -5, -5,-10,-10,-20,  # rank 1
    -10,  0,  5,  0,  0,  0,  0,-10,  # rank 2
    -10,  5,  5,  5,  5,  5,  0,-10,  # rank 3
      0,  0,  5,  5,  5,  5,  0, -5,  # rank 4
     -5,  0,  5,  5,  5,  5,  0, -5,  # rank 5
    -10,  0,  5,  5,  5,  5,  0,-10,  # rank 6
    -10,  0,  0,  0,  0,  0,  0,-10,  # rank 7
    -20,-10,-10, -5, -5,-10,-10,-20,  # rank 8
], [
      0,   0, -20,   0,   0, -20,   0,   0,  # rank 1
      0,  10,  -5,  -5,  -5,  -5,  10,   0,  # rank 2
      0, -10,  20,  10,  10,  20, -10,   0,  # rank 3
    -20, -10,  10,  60,  60,  10, -10, -20,  # rank 4
    -20, -10,  10,  60,  60,  10, -10, -20,  # rank 5
      0, -10,  20,  10,  10,  20, -10,   0,  # rank 6
      0,  10,  -5,  -5,  -5,  -5,  10,   0,  # rank 7
      0,   0, -20,   0,   0, -20,   0,   0,  # rank 8
] ]

KING_TABLE = [EMPTY, [
     20, 30, 10,  0,  0, 10, 30, 20,  # rank 1
     20, 20,  0,  0,  0,  0, 20, 20,  # rank 2
    -10,-20,-20,-20,-20,-20,-20,-10,  # rank 3
    -20,-30,-30,-40,-40,-30,-30,-20,  # rank 4
    -30,-40,-40,-50,-50,-40,-40,-30,  # rank 5
    -30,-40,-40,-50,-50,-40,-40,-30,  # rank 6
    -30,-40,-40,-50,-50,-40,-40,-30,  # rank 7
    -30,-40,-40,-50,-50,-40,-40,-30,  # rank 8
], [
    -50,-30,-30,-30,-30,-30,-30,-50,  # rank 1
    -30,-30,  0,  0,  0,  0,-30,-30,  # rank 2
    -30,-10, 20, 30, 30, 20,-10,-30,  # rank 3
    -30,-10, 30, 40, 40, 30,-10,-30,  # rank 4
    -30,-10, 30, 40, 40, 30,-10,-30,  # rank 5
    -30,-10, 20, 30, 30, 20,-10,-30,  # rank 6
    -30,-20,-10,  0,  0,-10,-20,-30,  # rank 7
    -50,-40,-30,-20,-20,-30,-40,-50,  # rank 8
], [
      0,   0, -20,   0,   0, -20,   0,   0,  # rank 1
      0,  10,  -5,  -5,  -5,  -5,  10,   0,  # rank 2
      0, -10,  20,  10,  10,  20, -10,   0,  # rank 3
    -20, -10,  10,  60,  60,  10, -10, -20,  # rank 4
    -20, -10,  10,  60,  60,  10, -10, -20,  # rank 5
      0, -10,  20,  10,  10,  20, -10,   0,  # rank 6
      0,  10,  -5,  -5,  -5,  -5,  10,   0,  # rank 7
      0,   0, -20,   0,   0, -20,   0,   0,  # rank 8
] ]

PST_MOD = [0.06, 0.15, -0.02, -0.03]
OP_PST_MOD = [-0.03, -0.1, 0.1, 0.02]

def bound(x):
    return max(min(x,1),0)

class Bot(ChessBotBase.Bot):
    pieces = []
    values = {chess.PAWN: PAWN, chess.KNIGHT: KNIGHT, chess.BISHOP: BISHOP, chess.ROOK: ROOK, chess.QUEEN: QUEEN}

    def name(self):
        return "Aleph Null"

    def image(self):
        return "icons/AlephNullIcon.png"

    def opening(self, board):
        fen = str(board.fen().split(" ")[0])
        move = None
        if self.turn > 1:
            return None
        if fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": #empty
            move = "e2e4"
        elif fen == "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": #d4
            move = "d7d5"
        elif fen == "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R": #Nf3
            move = "c7c5"
        elif fen == "rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR": #Nc3
            move = "d7d5"
        elif fen == "rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR": #f4
            move = "g8f6"
        elif self.turn == 0 and self.color == chess.BLACK:
            move = "e7e5"

        ################### WHTIE RESPONSES ###################

        elif fen == "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR": # e4 e5 Normal Variation
            move = "g1f3"
        elif fen == "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR": # e4 d5 Scandinavian
            move = "e4d5"
        elif fen == "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR": # e4 Nf6 Alekhine 
            move = "e4e5"
        elif fen == "rnbqkbnr/pppppp1p/8/6p1/4P3/8/PPPP1PPP/RNBQKBNR": # e4 g5 Borg
            move = "b1c3"
        elif fen == "rnbqkbnr/ppppp1pp/8/5p2/4P3/8/PPPP1PPP/RNBQKBNR": # e4 f5 Duras Gambit
            move = "e4f5"
        elif fen == "r1bqkbnr/pppppppp/n7/8/4P3/8/PPPP1PPP/RNBQKBNR": # e4 Na6 Lemming
            move = "g1f3"
        elif fen == "rnbqkbnr/p1pppppp/8/1p6/4P3/8/PPPP1PPP/RNBQKBNR": # e4 b5 ?!
            move = "f1b5"
        elif self.turn == 1 and self.color == chess.WHITE:
            move = "d2d4"

        if move == None:
            return None
        return chess.Move.from_uci(move)

    def get_pieces(self, board):
        pieces = []

        for piece_type in chess.PIECE_TYPES:
            pieces.append(board.pieces(piece_type, self.color) or [])
            pieces.append(board.pieces(piece_type, not self.color) or [])

        self.pawns = pieces[0]
        self.knights = pieces[2]
        self.bishops = pieces[4]
        self.rooks = pieces[6]
        self.queens = pieces[8]
        self.kings = pieces[10]

        self.op_pawns = pieces[1]
        self.op_knights = pieces[3]
        self.op_bishops = pieces[5]
        self.op_rooks = pieces[7]
        self.op_queens = pieces[9]
        self.op_kings = pieces[11]

        self.pieces = list(self.pawns) + list(self.knights) + list(self.bishops) + list(self.rooks) + list(self.queens)
        self.op_pieces = list(self.op_pawns) + list(self.op_knights) + list(self.op_bishops) + list(self.op_rooks) + list(self.op_queens)

        self.total_pieces = self.pieces + self.op_pieces

    def is_developed(self, square, piece, color):
        rank = chess.square_rank(square)

        if piece == chess.PAWN:
            return rank != (1 if color == chess.WHITE else 6)

        start_squares = {
            chess.KNIGHT: [chess.B1, chess.G1] if color == chess.WHITE else [chess.B8, chess.G8],
            chess.BISHOP: [chess.C1, chess.F1] if color == chess.WHITE else [chess.C8, chess.F8],
            chess.ROOK:   [chess.A1, chess.H1] if color == chess.WHITE else [chess.A8, chess.H8],
            chess.QUEEN:  [chess.D1] if color == chess.WHITE else [chess.D8],
            chess.KING:   [chess.E1] if color == chess.WHITE else [chess.E8],
        }

        return square not in start_squares.get(piece, [])
    
    def get_developed(self, board):
        self.pawns_dev = []
        self.knights_dev = []
        self.bishops_dev = []
        self.rooks_dev = []
        self.queens_dev = []
        
        self.op_pawns_dev = []
        self.op_knights_dev = []
        self.op_bishops_dev = []
        self.op_rooks_dev = []
        self.op_queens_dev = []

        square = chess.A1
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, rank)
                piece = board.piece_type_at(square)
                color = board.color_at(square)
                dev = self.is_developed(square, piece, self.color)
                op_dev = self.is_developed(square, piece, not self.color) 
                if color == self.color and dev:
                    if piece == chess.PAWN:
                        self.pawns_dev.append(square)
                    elif piece == chess.KNIGHT:
                        self.knights_dev.append(square)
                    elif piece == chess.BISHOP:
                        self.bishops_dev.append(square)
                    elif piece == chess.ROOK:
                        self.rooks_dev.append(square)
                    elif piece == chess.QUEEN:
                        self.queens_dev.append(square)
                elif color != self.color and op_dev:
                    if piece == chess.PAWN:
                        self.op_pawns_dev.append(square)
                    elif piece == chess.KNIGHT:
                        self.op_knights_dev.append(square)
                    elif piece == chess.BISHOP:
                        self.op_bishops_dev.append(square)
                    elif piece == chess.ROOK:
                        self.op_rooks_dev.append(square)
                    elif piece == chess.QUEEN:
                        self.op_queens_dev.append(square)
        
    def evaluate(self, board: chess.Board):

        score = 0

        ################### SETUP ###################
        
        if board.is_checkmate():
            if board.turn == self.color:
                return -math.inf
            else:
                return math.inf

        self.get_pieces(board)
        self.get_developed(board)

        p = len(self.pieces) / 15

        BEGINNING = bound((3 * p) - 2)
        MIDDLE = bound(1 - abs(3 * p - 1.5))
        END = bound(1 - (3 * p))

        def mod_list(MOD_LIST):
            score = MOD_LIST[0]
            score += MOD_LIST[1] * BEGINNING
            score += MOD_LIST[2] * MIDDLE
            score += MOD_LIST[3] * END
            return score
        
        def pst_lookup(table, square, color):
            if color == chess.WHITE:
                idx = square
            else:
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                idx = (7 - rank) * 8 + file
            return table[0][idx] + table[1][idx] * BEGINNING + table[2][idx] * MIDDLE + table[3][idx] * END

        ################### MATERIAL ###################

        material = len(self.pawns) * mod_list(PAWN)
        material += len(self.knights) * mod_list(KNIGHT)
        material += len(self.bishops) * mod_list(BISHOP)
        material += len(self.rooks) * mod_list(ROOK)
        material += len(self.queens) * mod_list(QUEEN)

        op_material = len(self.op_pawns) * mod_list(PAWN)
        op_material += len(self.op_knights) * mod_list(KNIGHT)
        op_material += len(self.op_bishops) * mod_list(BISHOP)
        op_material += len(self.op_rooks) * mod_list(ROOK)
        op_material += len(self.op_queens) * mod_list(QUEEN)
        
        ################### DEVELOPMENT ###################
        
        development = len(self.pawns_dev) * mod_list(PAWN_DEVELOPMENT_MOD)
        development += len(self.knights_dev) * mod_list(KNIGHT_DEVELOPMENT_MOD)
        development += len(self.bishops_dev) * mod_list(BISHOP_DEVELOPMENT_MOD)
        development += len(self.rooks_dev) * mod_list(ROOK_DEVELOPMENT_MOD)
        development += len(self.queens_dev) * mod_list(QUEEN_DEVELOPMENT_MOD)

        op_development = len(self.op_pawns_dev) * mod_list(PAWN_DEVELOPMENT_MOD)
        op_development += len(self.op_knights_dev) * mod_list(KNIGHT_DEVELOPMENT_MOD)
        op_development += len(self.op_bishops_dev) * mod_list(BISHOP_DEVELOPMENT_MOD)
        op_development += len(self.op_rooks_dev) * mod_list(ROOK_DEVELOPMENT_MOD)
        op_development += len(self.op_queens_dev) * mod_list(QUEEN_DEVELOPMENT_MOD)

        ################### ATTACKS / DEFENCE ###################

        coverage = []
        op_coverage = []

        defended = []
        op_defended = []

        attacked = []
        op_attacked = []

        for square in self.pieces:
            attacks = board.attacks(square)
            if not board.is_pinned(not self.color, square):
                coverage += list(attacks)
            for square in list(attacks):
                piece = board.piece_at(square)
                if piece == None:
                    continue
                if piece.color == self.color:
                    defended.append(piece)
                if piece.color != self.color:
                    attacked.append(piece)

        for square in self.op_pieces:
            attacks = board.attacks(square)
            if not board.is_pinned(self.color, square):
                op_coverage += list(attacks)
            for square in list(attacks):
                piece = board.piece_at(square)
                if piece == None:
                    continue
                if piece.color != self.color:
                    op_defended.append(piece)
                if piece.color == self.color:
                    op_attacked.append(piece)
            

        ################### CASTLE ###################

        castle_k_score = 1 if self.has_castled == chess.KING else 0
        castle_q_score = 1 if self.has_castled == chess.QUEEN else 0

        op_castle_k_score = 1 if self.op_has_castled == chess.KING else 0
        op_castle_q_score = 1 if self.op_has_castled == chess.QUEEN else 0

        ################### PST ###################

        pst_map = {
            chess.PAWN:   PAWN_TABLE,
            chess.KNIGHT: KNIGHT_TABLE,
            chess.BISHOP: BISHOP_TABLE,
            chess.ROOK:   ROOK_TABLE,
            chess.QUEEN:  QUEEN_TABLE,
            chess.KING:   KING_TABLE,
        }

        pst_score = 0
        op_pst_score = 0

        for piece_type, table in pst_map.items():
            for square in board.pieces(piece_type, self.color):
                pst_score += pst_lookup(table, square, self.color)
            for square in board.pieces(piece_type, not self.color):
                op_pst_score += pst_lookup(table, square, not self.color)

        score += pst_score * mod_list(PST_MOD)
        score -= op_pst_score * mod_list(PST_MOD)

        ################### EVALUATION ###################

        #score += castle_k_score * mod_list(KINGSIDE_CASTLE_MOD)
        #score += castle_q_score * mod_list(QUEENSIDE_CASTLE_MOD)
        
        #score -= op_castle_k_score * mod_list(KINGSIDE_CASTLE_MOD)
        #score -= op_castle_q_score * mod_list(QUEENSIDE_CASTLE_MOD)

        score += pst_score * mod_list(PST_MOD)
        score += op_pst_score * mod_list(OP_PST_MOD)

        score += material * mod_list(MATERIAL_MOD)
        score += op_material * mod_list(OP_MATERIAL_MOD)
        score -= len(self.total_pieces) * mod_list(SIMPLIFICATION_MOD)

        score += development * mod_list(DEVELOP_MOD)
        score += op_development * mod_list(OP_DEVELOP_MOD)

        score += len(coverage) * mod_list(COVERAGE_MOD)
        score += len(op_coverage) * mod_list(OP_COVERAGE_MOD)
        
        score += len(attacked) * mod_list(ATTACKED_MOD)
        score += len(op_attacked) * mod_list(OP_ATTACKED_MOD)

        score += len(defended) * mod_list(DEFENDED_MOD)
        score += len(op_defended) * mod_list(OP_DEFENDED_MOD)


        if board.turn == self.color:
            score *= mod_list(TEMPO_MOD)
        else:
            score /= mod_list(TEMPO_MOD)

        
        if board.is_game_over() and not board.is_checkmate():
            score /= -8
        elif board.is_repetition(2):
            score /= -8

        return score
    