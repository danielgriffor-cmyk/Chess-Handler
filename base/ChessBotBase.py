import tkinter as tk
import chess
import chess.polyglot
import random
import math
from concurrent.futures import ThreadPoolExecutor
import base64
from pathlib import Path

PIECE_VALUE = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def mvv_lva_score(board, move):
    if not board.is_capture(move):
        return 0

    victim = board.piece_at(move.to_square)
    attacker = board.piece_at(move.from_square)

    if victim is None or attacker is None:
        return 0

    return PIECE_VALUE[victim.piece_type] * 10 - PIECE_VALUE[attacker.piece_type]

class Bot:
    turn = 0
    transposition_table = {}
    past_moves_hash = {}
    is_enpassant = False
    is_castle = False
    is_promote = False

    def __init__(self, color=chess.BLACK, depth=2, qsearch=False, qdepth=4):
        self.color = color
        self.depth = depth
        self.qsearch = qsearch
        self.qdepth = qdepth
        self.IMAGE_DATA = self.to_image_data(self.image())

    def image(self):
        return "base/ChessBotBaseIcon.png"

    def to_image_data(self, image_path: str) -> str:
        """
        Encodes the image at the given path as a base64 string
        suitable for use in IMAGE_DATA.
        """
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(path, "rb") as f:
            encoded_bytes = base64.b64encode(f.read())
            encoded_str = encoded_bytes.decode("utf-8")

        # prepend the standard base64 header for PNG
        return f"data:image/png;base64,{encoded_str}"

    def name(self):
        return f"Chess Bot (depth {self.depth})"

    def evaluate(self, board):
        raise NotImplementedError

    def openning(self, board):
        return None

    def main_eval(self, board):
        h = chess.polyglot.zobrist_hash(board)
        if h in self.transposition_table:
            return self.transposition_table[h] + random.random() / 1000
        else:
            score = self.evaluate(board)
            self.transposition_table[h] = score
        return score + random.random() / 1000

    def all_moves(self, board):
        moves = list(board.legal_moves)
        moves.sort(
            key=lambda m: mvv_lva_score(board, m),
            reverse=True
        )
        return moves

    def minimax(self, board, depth, alpha, beta, maximizing):

        if depth == 0 or board.is_game_over():
            return self.main_eval(board)

        if maximizing:
            value = -1e9
            for move in board.legal_moves:
                board.push(move)
                value = max(value, self.minimax(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = 1e9
            for move in board.legal_moves:
                board.push(move)
                value = min(value, self.minimax(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
        
    def perspective_eval(self, board):
        base = self.evaluate(board)
        return base if board.turn == self.color else -base

    def quiescence(self, board, depth):
        stand_pat = self.main_eval(board)
        
        if depth == 0 or board.is_repetition(2):
            return stand_pat
        
        best_score = stand_pat
        
        for move in board.legal_moves:
            if not board.is_capture(move) and not board.gives_check(move):
                continue
            board.push(move)
            score = -self.quiescence(board, depth - 1)
            board.pop()
            best_score = max(best_score, score)
        
        return best_score
        
    def choose_move(self, board, depth=None):
        
        move = None
        move = self.openning(board)

        if move != None:
            if move in board.legal_moves:
                return move

        self.turn += 1

        h = chess.polyglot.zobrist_hash(board)

        if h in self.past_moves_hash:
            return self.past_moves_hash[h]

        # --- Mate in 1 override ---
        for move in board.legal_moves:
            board.push(move)
            if board.is_checkmate():
                board.pop()
                return move
            board.pop()

        # --- normal minimax ---
        if depth is None:
            depth = self.depth

        maximizing = board.turn == self.color

        # if we're searching deeper than one ply, we can evaluate each first move
        # in parallel to make use of multiple cores. the recursive minimax call
        # uses its own board copy so no shared state is modified.
        if depth > 1:
            moves = self.all_moves(board)
            best_score = -1e9 if maximizing else 1e9
            best_move = None

            def eval_move(move):
                board_copy = board.copy()
                board_copy.push(move)
                score = self.minimax(board_copy, depth - 1, -1e9, 1e9, not maximizing)
                return score, move

            with ThreadPoolExecutor() as executor:
                for score, move_tuple in executor.map(eval_move, moves):
                    if (maximizing and score > best_score) or (not maximizing and score < best_score):
                        best_score = score
                        best_move = move_tuple

            if best_move is None:
                legal_moves = list(board.legal_moves)
                if legal_moves:
                    return legal_moves[0]
                return None
            self.past_moves_hash[h] = best_move
            self.move_chosen(best_move)
            return best_move

        # fall back to single-threaded minimax for shallow searches
        best_score = -1e9 if maximizing else 1e9
        best_move = None

        for move in board.legal_moves:
            board.push(move)
            score = self.minimax(board, depth - 1, -1e9, 1e9, not maximizing)
            board.pop()

            if (maximizing and score > best_score) or (not maximizing and score < best_score):
                best_score = score
                best_move = move

        if best_move is None:
            legal_moves = list(board.legal_moves)

            move = legal_moves[0] if legal_moves else None
            self.past_moves_hash[h] = move
            self.move_chosen(move)
            return move

        self.past_moves_hash[h] = best_move
        self.move_chosen(best_move)
        return best_move

    def move_chosen(self, move):
        pass

    def reset(self):
        self.transposition_table.clear()
        self.past_moves_hash.clear()
        self.turn = 0
