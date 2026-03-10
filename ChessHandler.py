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
import bots.alephNull as AlephNull

PLAYER = "human"

white_bot = ShallowTeal.Bot(color = chess.WHITE, depth=2, qsearch=True)
black_bot = AlephNull.Bot(color = chess.BLACK, depth=2, qsearch=True)

gui = chessGUI(white_player=white_bot, black_player=black_bot)

gui.piece_set = "neo"
gui.move_time = 100


gui.run()

pgn = chess.pgn.Game.from_board(gui.board)
pgn.headers["White"] = "Player" if white_bot == "human" else white_bot.true_name()
pgn.headers["Black"] = "Player" if black_bot == "human" else black_bot.true_name()

print(pgn)
