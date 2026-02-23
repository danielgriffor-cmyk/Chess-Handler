import tkinter as tk
import chess
import chess.pgn
from base.ChessGUI import chessGUI

import bots.ComplexChessBot as ComplexChessBot
import bots.StalemateChessBot as StalemateChessBot

Human = "human"

white_bot = ComplexChessBot.Bot(color = chess.WHITE, depth=2)
black_bot = ComplexChessBot.Bot(color = chess.BLACK, depth=3, qsearch=False)

gui = chessGUI(white_player=white_bot, black_player=black_bot)
gui.move_time = 1000

gui.run()

pgn = chess.pgn.Game.from_board(gui.board)
pgn.headers["White"] = "Human" if white_bot == Human else white_bot.name()
pgn.headers["Black"] = "Human" if black_bot == Human else black_bot.name()

print(pgn)