import tkinter as tk
import chess
import chess.polyglot
import random
import math

class Bot:
    def __init__(self, color=chess.BLACK, depth=2, qsearch=True, qdepth=4):
        self.color = color
        self.depth = depth
        self.qsearch = qsearch
        self.qdepth = qdepth
        self.turn = 0
        self.transposition_table = {}
        self.past_moves_hash = {}
        self.resigns = False

    def name(self):
        return f"Chess Bot (depth {self.depth})"

    def evaluate(self, board):
        raise NotImplementedError

    def main_eval(self, board):
        h = chess.polyglot.zobrist_hash(board)
        if h in self.transposition_table:
            return self.transposition_table[h] + random.random() / 1000
        else:
            score = self.evaluate(board)
            self.transposition_table[h] = score
        return score + random.random() / 1000

    def all_moves(self, board):
        moves = []

        for move in board.legal_moves:
            moves.append((move, False))

        return moves

    def minimax(self, board, depth=None, alpha=-1e9, beta=1e9, maximizing=None):
        if depth is None:
            depth = self.depth
        if maximizing is None:
            maximizing = board.turn == self.color

        # Terminal node
        if depth == 0:
            if self.qsearch:
                if maximizing:
                    return self.quiescence(board, self.qdepth), None
                else:
                    return -self.quiescence(board, self.qdepth), None
            else:
                return self.main_eval(board), None

        if board.is_game_over():
            return self.main_eval(board), None

        best_move = None
        moves = self.all_moves(board)

        if not moves:
            return self.main_eval(board), None
        moves.sort(
            key=lambda m: board.is_capture(m[0]),
            reverse=maximizing
        )

        if maximizing:
            value = -1e9
            for move, is_nudge in moves:
                board.push(move)
                score, _ = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()

                if score > value:
                    value = score
                    best_move = (move, is_nudge)

                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # beta cutoff

            return value, best_move

        else:
            value = 1e9
            for move, is_nudge in moves:
                board.push(move)
                score, _ = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()

                if score < value:
                    value = score
                    best_move = (move, is_nudge)

                beta = min(beta, value)
                if beta <= alpha:
                    break  # alpha cutoff

            return value, best_move

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
        self.turn += 1

        h = chess.polyglot.zobrist_hash(board)

        if h in self.past_moves_hash:
            return self.past_moves_hash[h]

        # --- Mate in 1 override ---
        for move in board.legal_moves:
            board.push(move)
            if board.is_checkmate():
                board.pop()
                return move, False
            board.pop()

        # --- normal minimax ---
        if depth is None:
            depth = self.depth

        maximizing = board.turn == self.color
        score, best = self.minimax(board, depth, -1e9, 1e9, maximizing)

        if best is None:
            legal_moves = list(board.legal_moves)
            if legal_moves:
                return legal_moves[0], False
            return None, False
        
        self.past_moves_hash[h] = best
        return best

    def reset(self):
        self.transposition_table.clear()
        self.past_moves_hash.clear()
        self.turn = 0
