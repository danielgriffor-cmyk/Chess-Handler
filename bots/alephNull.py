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


TEMPO_MOD = [1.05,0,0,0]

MATERIAL_MOD = [1, 0.5, -0.2, 3]
OP_MATERIAL_MOD = [-1.05, -0.5, 0.2, 0]

DEVELOP_MOD = [0.75, 0, 0, 0]
OP_DEVELOP_MOD = [0.7, 0, 0, 0]

COVERAGE_MOD = [0.0025, 0, 0, 0]
OP_COVERAGE_MOD = [-0.003, 0, 0, 0]

SIMPLIFICATION_MOD = [0.05, 0, 0, 0]

def bound(x):
    return max(min(x,1),0)

class Bot(ChessBotBase.Bot):
    pieces = []
    values = {chess.PAWN: PAWN, chess.KNIGHT: KNIGHT, chess.BISHOP: BISHOP, chess.ROOK: ROOK, chess.QUEEN: QUEEN}

    def name(self):
        return "Aleph Null"

    def openning(self, board):
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
        elif self.turn == 0 and self.color == chess.WHITE:
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

        def mod_list(MOD_LIST):
            score = MOD_LIST[0]
            score += MOD_LIST[1] * BEGINNING
            score += MOD_LIST[2] * MIDDLE
            score += MOD_LIST[3] * END
            return score

        self.get_pieces(board)
        self.get_developed(board)

        p = len(self.pieces) / 15

        BEGINNING = bound((3 * p) - 2)
        MIDDLE = bound(1 - abs(3 * p - 1.5))
        END = bound(1 - (3 * p))

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

        for square in self.pieces:
            if not board.is_pinned(not self.color, square):
                coverage += list(board.attacks(square))
            
        for square in self.op_pieces:
            if not board.is_pinned(self.color, square):
                op_coverage += list(board.attacks(square))
            

        ################### EVALUATION ###################

        score += material * mod_list(MATERIAL_MOD)
        score += op_material * mod_list(OP_MATERIAL_MOD)
        score -= len(self.total_pieces) * mod_list(SIMPLIFICATION_MOD)

        score += development * mod_list(DEVELOP_MOD)
        score += op_development * mod_list(OP_DEVELOP_MOD)

        score += len(coverage) * mod_list(COVERAGE_MOD)
        score += len(op_coverage) * mod_list(OP_COVERAGE_MOD)

        if board.is_checkmate():
            if board.turn == self.color:
                return -math.inf
            else:
                return math.inf
            

        if board.turn == self.color:
            score *= mod_list(TEMPO_MOD)
        else:
            score /= mod_list(TEMPO_MOD)

        return score
    