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

    def __init__(self, color=chess.BLACK, depth=2, qsearch=False, qdepth=4):
        self.color = color
        self.depth = depth
        self.qsearch = qsearch
        self.qdepth = qdepth
        self.IMAGE_DATA = self.to_image_data(self.image())

        self.turn = 0
        self.transposition_table = {}
        self.past_moves_hash = {}
        self.has_castled = None
        self.op_has_castled = None

        self.op_checks = 0
        self.self_checks = 0

    def get_checks(self, board):
        temp_board = chess.Board()
        checks = {chess.WHITE: 0, chess.BLACK: 0}

        for move in board.move_stack:
            temp_board.push(move)
            if temp_board.is_check():
                checks[not temp_board.turn and chess.BLACK or chess.WHITE] += 1
        if self.color == chess.WHITE:
            self.self_checks = checks[1]
            self.op_checks = checks[0]
        else:
            self.op_checks = checks[1]
            self.self_checks = checks[0]

    def image(self):
        return "base/ChessBotBaseIcon.png"
    
    def max_eval(self):
        return 10

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
        return f"Chess Bot"
    
    def true_name(self):
        return self.name() + f" (depth {self.depth}, qsearch {self.qdepth if self.qsearch else "None"})"

    def evaluate(self, board):
        raise NotImplementedError

    def opening(self, board):
        return None

    def all_moves(self, board):
        moves = list(board.legal_moves)
        moves.sort(
            key=lambda m: mvv_lva_score(board, m),
            reverse=True
        )
        return moves

    def quiescence(self, board, depth, alpha, beta):
        stand_pat = self.main_eval(board)  # now correctly perspective-relative
        
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)

        if depth == 0 or board.is_game_over():
            return alpha

        for move in self.all_moves(board):
            if not board.is_capture(move) and not board.gives_check(move):
                continue
            board.push(move)
            score = -self.quiescence(board, depth - 1, -beta, -alpha)
            board.pop()
            if score >= beta:
                return beta
            alpha = max(alpha, score)

        return alpha

    def main_eval(self, board):
        self.get_checks(board)
        score = self.evaluate(board)
        return score if board.turn == self.color else -score

    def minimax(self, board, depth, alpha, beta):
        h = chess.polyglot.zobrist_hash(board)

        # Only use cached result if it was searched at least as deep
        if h in self.transposition_table:
            cached_score, cached_depth = self.transposition_table[h]
            if cached_depth >= depth:
                return cached_score

        if depth == 0 or board.is_game_over():
            if self.qsearch:
                return self.quiescence(board, self.qdepth, alpha, beta)
            return self.main_eval(board)

        value = -1e9
        for move in self.all_moves(board):
            board.push(move)
            value = max(value, -self.minimax(board, depth - 1, -beta, -alpha))
            board.pop()
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        # Cache with depth so shallow results don't override deep ones
        self.transposition_table[h] = (value, depth)
        return value

    def choose_move(self, board: chess.Board, depth=None, remaining_time=None):
        last_board = board.copy()
        move = self.opening(board)
        if move is not None and move in board.legal_moves:
            self.turn += 1
            return move

        self.turn += 1
        h = chess.polyglot.zobrist_hash(board)

        #if h in self.past_moves_hash:
            #return self.past_moves_hash[h]

        for move in board.legal_moves:
            board.push(move)
            if board.is_checkmate():
                board.pop()
                return move
            board.pop()

        if depth is None:
            depth = self.depth

        if remaining_time is not None:
            if remaining_time < 50:
                depth = max(1, depth - 3)
            elif remaining_time < 300:
                depth = max(1, depth - 2)
            elif remaining_time < 500:
                depth = max(1, depth - 1)

        moves = self.all_moves(board)

        if depth > 1:
            def eval_move(move):
                board_copy = board.copy()
                board_copy.push(move)
                score = -self.minimax(board_copy, depth - 1, -1e9, 1e9)
                return score, move

            with ThreadPoolExecutor() as executor:
                scored_moves = list(executor.map(eval_move, moves))
        else:
            scored_moves = []
            for move in moves:
                board.push(move)
                score = -self.minimax(board, depth - 1, -1e9, 1e9)
                board.pop()
                scored_moves.append((score, move))

        if not scored_moves:
            return None

        scored_moves.sort(key=lambda x: x[0], reverse=True)
        best_score = scored_moves[0][0]
        best_moves = [m for s, m in scored_moves if abs(s - best_score) < 1e-6]
        best_move = random.choice(best_moves) if best_moves else scored_moves[0][1]

        self.past_moves_hash[h] = best_move
        self.move_chosen(best_move)
        return best_move

    def move_chosen(self, move):
        pass

    def update_castling_status(self, move, board):
        if board.is_castling(move):
            moving_color = board.color_at(move.from_square)
            if moving_color == self.color:
                if board.is_kingside_castling(move):
                    self.has_castled = chess.KING
                elif board.is_queenside_castling(move):
                    self.has_castled = chess.QUEEN
            else:
                if board.is_kingside_castling(move):
                    self.op_has_castled = chess.KING
                elif board.is_queenside_castling(move):
                    self.op_has_castled = chess.QUEEN
    

    def reset(self):
        self.transposition_table.clear()
        self.past_moves_hash.clear()
        self.turn = 0
        self.has_castled = None
        self.op_has_castled = None
