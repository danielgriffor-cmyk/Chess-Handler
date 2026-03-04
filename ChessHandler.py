import tkinter as tk
import chess
import chess.pgn
from base.ChessGUI import chessGUI

import bots.complexChessBot as ComplexChessBot
import bots.stalemateChessBot as StalemateChessBot
import bots.cheeburber as Cheeburber
import bots.escanor as Escanor
import bots.shallowTeal as ShallowTeal
import bots.kamikazeGambiterBot as KamikazeGambiterBot

Human = "human"

white_bot = ComplexChessBot.Bot(color = chess.WHITE, depth=2, qsearch=False)
black_bot = ComplexChessBot.Bot(color = chess.BLACK, depth=2, qsearch=False)

gui = chessGUI(white_player=white_bot, black_player=black_bot)
gui.move_time = 100


gui.run()

pgn = chess.pgn.Game.from_board(gui.board)
pgn.headers["White"] = "Human" if white_bot == Human else white_bot.name()
pgn.headers["Black"] = "Human" if black_bot == Human else black_bot.name()

print(pgn)
