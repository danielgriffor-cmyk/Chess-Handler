import chess
import random
import base.ChessBotBase as ChessBotBase
import math




PAWN = 1
PAWN_DEVELOPMENT_MOD = 0.5

KNIGHT = 3
KNIGHT_DEVELOPMENT_MOD = 2

BISHOP = 4
BISHOP_DEVELOPMENT_MOD = 1.25

ROOK = 6
ROOK_DEVELOPMENT_MOD = 2

QUEEN = 11
QUEEN_DEVELOPMENT_MOD = 4
EARLY_QUEEN_DEVELOPMENT_MOD = -100


TEMPO_MOD = 1.1

MATERIAL_MOD = 1.3
OP_MATERIAL_MOD = -1

TRAP_BONUS = 1
OP_TRAP_BONUS = -1

DEVELOP_MOD = 0.15
OP_DEVELOP_MOD = -0.125

ATTACKER_MOD = 0.01

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

    def is_developed(self, square, piece):
        rank = chess.square_rank(square)
        
        if piece == chess.PAWN:
            return rank != (1 if self.color == chess.WHITE else 6)

        start_squares = {
            chess.KNIGHT: [chess.B1, chess.G1] if self.color == chess.WHITE else [chess.B8, chess.G8],
            chess.BISHOP: [chess.C1, chess.F1] if self.color == chess.WHITE else [chess.C8, chess.F8],
            chess.ROOK:   [chess.A1, chess.H1] if self.color == chess.WHITE else [chess.A8, chess.H8],
            chess.QUEEN:  [chess.D1] if self.color == chess.WHITE else [chess.D8],
            chess.KING:   [chess.E1] if self.color == chess.WHITE else [chess.E8],
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
                dev = self.is_developed(square, piece)
                if color == self.color:
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
                else:
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

        self.get_pieces(board)
        self.get_developed(board)

        p = len(self.pieces) / 26

        BEGINNING = (3 * p) - 2
        MIDDLE = 1 - abs(3 * p - 1.5)
        END = 1 - (3 * p)

        ################### MATERIAL ###################

        material = len(self.pawns) * PAWN
        material += len(self.knights) * KNIGHT
        material += len(self.bishops) * BISHOP
        material += len(self.rooks) * ROOK
        material += len(self.queens) * QUEEN

        op_material = len(self.op_pawns) * PAWN
        op_material += len(self.op_knights) * KNIGHT
        op_material += len(self.op_bishops) * BISHOP
        op_material += len(self.op_rooks) * ROOK
        op_material += len(self.op_queens) * QUEEN
        
        ################### DEVELOPMENT ###################

        development = len(self.pawns_dev) * PAWN_DEVELOPMENT_MOD
        development += len(self.knights_dev) * KNIGHT_DEVELOPMENT_MOD
        development += len(self.bishops_dev) * BISHOP_DEVELOPMENT_MOD
        development += len(self.rooks_dev) * ROOK_DEVELOPMENT_MOD
        development += len(self.queens_dev) * QUEEN_DEVELOPMENT_MOD
        development += len(self.queens_dev) * EARLY_QUEEN_DEVELOPMENT_MOD * BEGINNING

        op_development = len(self.op_pawns_dev) * PAWN_DEVELOPMENT_MOD
        op_development += len(self.op_knights_dev) * KNIGHT_DEVELOPMENT_MOD
        op_development += len(self.op_bishops_dev) * BISHOP_DEVELOPMENT_MOD
        op_development += len(self.op_rooks_dev) * ROOK_DEVELOPMENT_MOD
        op_development += len(self.op_queens_dev) * QUEEN_DEVELOPMENT_MOD
        op_development += len(self.op_queens_dev) * EARLY_QUEEN_DEVELOPMENT_MOD * BEGINNING

        ################### ATTACKS / DEFENCE ###################

        coverage = []

        for square in self.pieces:
            piece_type = board.piece_type_at(square)
            if board.is_pinned(not self.color, square):
                pass
            coverage += board.attacks(square)

        ################### EVALUATION ###################

        score += material * MATERIAL_MOD
        score += op_material * OP_MATERIAL_MOD

        score += development * DEVELOP_MOD
        score += development * OP_DEVELOP_MOD

        score += len(coverage) * ATTACKER_MOD

        if board.is_checkmate():
            if board.turn == self.color:
                return -math.inf
            else:
                return math.inf
            
        if board.turn == self.color:
            score *= TEMPO_MOD
        else:
            score /= TEMPO_MOD

        return score
    