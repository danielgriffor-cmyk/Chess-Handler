import tkinter as tk
import chess
import chess.pgn
from ChessGUI import chessGUI

import SimpleChessBot
import ComplexChessBot
import RandomChessBot
import CheckChessBot

Human = "human"

black_bot = ComplexChessBot.Bot(color = chess.BLACK, depth=3, qsearch=False)
white_bot = Human

gui = chessGUI(white_player=white_bot, black_player=black_bot)
gui.move_time = 100

gui.run()

pgn = chess.pgn.Game.from_board(gui.board)
pgn.headers["White"] = "Human" if white_bot == Human else white_bot.name()
pgn.headers["Black"] = "Human" if black_bot == Human else black_bot.name()

print(pgn)