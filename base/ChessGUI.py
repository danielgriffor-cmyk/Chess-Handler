import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import chess

SQUARE_SIZE = 70
LIGHT = "#f0d9b5"
DARK = "#b58863"
PREV_LIGHT = "#FFCF33"
PREV_DARK = "#B49B0A"
HIGHLIGHT = "#ec3838"

class chessGUI:
    def __init__(self, white_player='human', black_player=None):
        self.move_time = 100
        self.board = chess.Board()
        self.white_player = white_player
        self.black_player = black_player

        self.root = tk.Tk()
        self.root.title("Chess")

        self.canvas = tk.Canvas(
            self.root,
            width=8*SQUARE_SIZE,
            height=8*SQUARE_SIZE
        )
        self.canvas.pack()

        # 🔑 Make sure images exist before draw()
        self.images = {}
        self.load_images()
        self.make_move_images()

        self.selected = None
        self.legal_targets = []
        self.legal_moves = []
        self.nudge_targets = []
        self.prev_sq = []

        self.status = tk.Label(self.root, text="", font=("Arial", 14))
        self.status.pack()

        self.eval_frame = tk.Frame(self.root)
        self.eval_frame.pack()

        self.white_eval = tk.Label(
            self.eval_frame,
            text="White: 0.0",
            font=("Arial", 12),
            fg="white",
            bg="black",
            padx=10,
            pady=5
        )
        self.white_eval.pack(side=tk.LEFT, padx=5)

        self.black_eval = tk.Label(
            self.eval_frame,
            text="Black: 0.0",
            font=("Arial", 12),
            fg="white",
            bg="black",
            padx=10,
            pady=5
        )
        self.black_eval.pack(side=tk.LEFT, padx=5)

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw()

        # Start bot move immediately if it's bot vs bot and Black is first
        self.root.after(self.move_time, self.bot_turn)

    def update_evaluation(self, white_eval, black_eval):
        """Update the evaluation display for both sides"""
        self.white_eval.config(text=f"White: {white_eval:+.1f}")
        self.black_eval.config(text=f"Black: {black_eval:+.1f}")

    def load_images(self):
        piece_map = {
            "P": "w_pawn",
            "N": "w_knight",
            "B": "w_bishop",
            "R": "w_rook",
            "Q": "w_queen",
            "K": "w_king",
            "p": "b_pawn",
            "n": "b_knight",
            "b": "b_bishop",
            "r": "b_rook",
            "q": "b_queen",
            "k": "b_king",
        }

        for symbol, name in piece_map.items():
            img = tk.PhotoImage(file=f"pieces/{name}.png")
            img = img.subsample(2, 2)  # resize as needed
            self.images[symbol] = img

    def make_move_images(self):
        dot_size = 25
        ring_size = SQUARE_SIZE - 12

        def make_dot(bg_hex, alpha=70):
            dot_size = 25
            # convert hex to RGB
            bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (1, 3, 5))
            # opaque background
            bg_img = Image.new("RGBA", (dot_size, dot_size), bg_rgb + (255,))
            # fully transparent layer
            dot = Image.new("RGBA", (dot_size, dot_size), (0, 0, 0, 0))
            d = ImageDraw.Draw(dot)
            # draw a circle with semi-transparent fill
            d.ellipse(
                (0, 0, dot_size-1, dot_size-1),
                fill=(60, 60, 60, alpha)
            )
            # composite the circle on the opaque square background
            img = Image.alpha_composite(bg_img, dot)
            return ImageTk.PhotoImage(img)

        self.move_dot_light = make_dot(LIGHT)
        self.move_dot_dark  = make_dot(DARK)
        self.move_dot_prev_light = make_dot(PREV_LIGHT)
        self.move_dot_prev_dark = make_dot(PREV_DARK)

        # ring (captures)
        ring = Image.new("RGBA", (ring_size, ring_size), (0, 0, 0, 0))
        d = ImageDraw.Draw(ring)
        d.ellipse((3, 3, ring_size-4, ring_size-4), outline=(60,60,60,200), width=4)
        self.move_ring = ImageTk.PhotoImage(ring)
        
    def draw(self):
        self.update_evaluation(self.white_player.evaluate(self.board), self.black_player.evaluate(self.board))
        self.canvas.delete("all")
        p = 0
        for r in range(8):
            for f in range(8):
                x1 = f * SQUARE_SIZE
                y1 = (7 - r) * SQUARE_SIZE
                color = LIGHT if (r + f) % 2 == 0 else DARK
                sq = chess.square(f, r)

                if p in self.prev_sq:
                    color = PREV_LIGHT if (r + f) % 2 == 0 else PREV_DARK

                if self.board.is_check() and sq == self.board.king(self.board.turn):
                    color = HIGHLIGHT

                self.canvas.create_rectangle(
                    x1, y1, x1 + SQUARE_SIZE, y1 + SQUARE_SIZE, fill=color, outline=color
                )

                piece = self.board.piece_at(sq)
                if piece:
                    self.canvas.create_image(
                        x1 + SQUARE_SIZE // 2,
                        y1 + SQUARE_SIZE // 2,
                        image=self.images[piece.symbol()]
                    )
                p += 1

        for move in self.legal_moves:
            to_sq = move.to_square
            f = chess.square_file(to_sq)
            r = chess.square_rank(to_sq)

            x = f * SQUARE_SIZE + SQUARE_SIZE // 2
            y = (7 - r) * SQUARE_SIZE + SQUARE_SIZE // 2

            for move in self.legal_moves:
                to_sq = move.to_square
                f = chess.square_file(to_sq)
                r = chess.square_rank(to_sq)

                x = f * SQUARE_SIZE + SQUARE_SIZE // 2
                y = (7 - r) * SQUARE_SIZE + SQUARE_SIZE // 2

                if self.board.piece_at(to_sq):
                    self.canvas.create_image(x, y, image=self.move_ring)
                else:
                    is_light = (r + f) % 2 == 0
                    dot = self.move_dot_light if is_light else self.move_dot_dark
                    if to_sq in self.prev_sq:
                        dot = self.move_dot_prev_light if is_light else self.move_dot_prev_dark
                    self.canvas.create_image(x, y, image=dot)

    def square_at(self, x, y):
        file = x // SQUARE_SIZE
        rank = 7 - (y // SQUARE_SIZE)
        return chess.square(file, rank)

    def compute_targets(self, square):
        self.legal_targets.clear()
        self.legal_moves.clear()

        # normal legal moves
        for m in self.board.legal_moves:
            if m.from_square == square:
                self.legal_targets.append(m.to_square)

        for m in self.board.legal_moves:
            if m.from_square == square:
                self.legal_moves.append(m)

    def set_board(self, fen):
        self.board.set_fen(fen)
        
    def update_status(self):
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            self.status.config(text=f"Checkmate! {winner} wins.")
            return True

        if self.board.is_stalemate():
            self.status.config(text="Stalemate! Draw.")
            return True

        if self.board.is_check():
            side = "White" if self.board.turn == chess.WHITE else "Black"
            self.status.config(text=f"{side} is in check!")
        else:
            self.status.config(text="")

        return False

    def on_click(self, event):
        if self.board.is_game_over():
            return

        current_player = self.white_player if self.board.turn == chess.WHITE else self.black_player
        if current_player != 'human':
            return

        sq = self.square_at(event.x, event.y)

        if self.selected is None:
            piece = self.board.piece_at(sq)
            if piece and piece.color == self.board.turn:
                self.selected = sq
                self.compute_targets(sq)
        else:
            if sq in self.legal_targets or sq in self.nudge_targets:
                self.prev_sq = [self.selected, sq]
                self.board.push(chess.Move(self.selected, sq))
                self.after_player_move()

            self.selected = None
            self.legal_targets.clear()
            self.legal_moves.clear()

        self.draw()

    def bot_turn(self):
        if self.board.is_game_over():
            return

        current_player = self.white_player if self.board.turn == chess.WHITE else self.black_player
        if current_player == 'human' or current_player is None:
            return

        move, is_nudge = current_player.choose_move(self.board)

        if move is not None:
            self.prev_sq.clear()
            curr_board = self.board.piece_map().copy()
            self.board.push(move)
            changed_board = self.board.piece_map().copy()
            for part in range(64):
                if curr_board.get(part) != changed_board.get(part):
                    self.prev_sq.append(part)
            self.draw()
            self.update_status()

        next_player = self.white_player if self.board.turn == chess.WHITE else self.black_player
        if next_player != 'human' and not self.board.is_game_over():
            self.root.after(self.move_time, self.bot_turn)

    def after_player_move(self):
        self.update_evaluation(self.white_player.evaluate(self.board), self.black_player.evaluate(self.board))
        if self.update_status():
            return
        self.root.after(self.move_time, self.bot_turn)

    def run(self):
        self.root.mainloop()
