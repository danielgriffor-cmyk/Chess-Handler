import tkinter as tk
import chess
import random
import math

class Bot:
    def __init__(self, color=chess.BLACK, depth=2):
        self.color = color
        self.depth = depth

    def evaluate(self, board):
        """
        Override this method in subclasses.
        Should return a numeric evaluation from the perspective of self.color
        """
        raise NotImplementedError

    def main_eval(self, board):
        score = self.evaluate(board)
        if board.turn != self.color:
            return score
        return score

    def all_moves(self, board):
        moves = []
        my_color = board.turn

        for move in board.legal_moves:
            board.push(move)

            # Is my king attacked after the move?
            if not board.is_attacked_by(not my_color, board.king(my_color)):
                moves.append((move, False))

            board.pop()

        return moves

    def minimax(self, board, depth=None, alpha=-1e9, beta=1e9, maximizing=None):
        if depth is None:
            depth = self.depth
        if maximizing is None:
            maximizing = board.turn == self.color

        # Terminal node
        if depth == 0:
            return self.quiescence(board, alpha, beta), None

        if board.is_game_over():
            return self.main_eval(board), None

        best_move = None
        moves = self.all_moves(board)

        if not moves:
            return self.main_eval(board), None

        # -------- MOVE ORDERING --------
        # Captures first → massive pruning improvement
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

    def quiescence(self, board, alpha, beta):
        stand_pat = self.main_eval(board)

        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        for move in board.legal_moves:
            if not board.is_capture(move) and not board.gives_check(move):
                continue

            board.push(move)
            score = -self.quiescence(board, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score < alpha:
                alpha = score

        return alpha

    def choose_move(self, board, depth=None):
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

        return best

