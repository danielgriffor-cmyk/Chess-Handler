import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageDraw, ImageTk
import chess
import chess.pgn
import math
import threading
import base64
from io import BytesIO
from base64 import b64decode

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

        self.white_eval_bot = None
        self.black_eval_bot = None

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
        self.prev_sq = []

        self.status = tk.Label(self.root, text="", font=("Arial", 14))
        self.status.pack()

        self.eval_frame = tk.Frame(self.root)
        self.eval_frame.pack()

        TARGET_SIZE = (80, 80) 

        whitebot_image = None
        blackbot_image = None
        try: whitebot_image = white_player.IMAGE_DATA
        except: whitebot_image = None
        try: blackbot_image = black_player.IMAGE_DATA
        except: blackbot_image = None

        if whitebot_image:
            try:
                # Clean the string
                data = whitebot_image.split("base64,")[-1] if "base64," in str(whitebot_image) else whitebot_image
                
                # 1. Decode and open with Pillow
                img_data = b64decode(data)
                pil_img = Image.open(BytesIO(img_data))
                
                # 2. Resize to EXACT pixels
                resized_img = pil_img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                
                # 3. Convert to Tkinter format and save unique reference
                self.white_img = ImageTk.PhotoImage(resized_img)
                self.white_label = tk.Label(self.eval_frame, image=self.white_img)
                self.white_label.pack(side=tk.LEFT, padx=5)
            except Exception as e:
                print(f"White image error: {e}")

        if blackbot_image:
            try:
                data = blackbot_image.split("base64,")[-1] if "base64," in str(blackbot_image) else blackbot_image
                
                # Repeat for Black bot
                img_data = b64decode(data)
                pil_img = Image.open(BytesIO(img_data))
                resized_img = pil_img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                
                self.black_img = ImageTk.PhotoImage(resized_img)
                self.black_label = tk.Label(self.eval_frame, image=self.black_img)
                self.black_label.pack(side=tk.RIGHT, padx=5)
            except Exception as e:
                print(f"Black image error: {e}")

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

        # copy PGN button
        self.copy_pgn_btn = tk.Button(self.root, text="Copy PGN", command=self.copy_pgn)
        self.copy_pgn_btn.pack(pady=2)

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw()

        # Start bot move immediately if it's bot vs bot and Black is first
        self.root.after(self.move_time, self.bot_turn)

    def get_eval_bots(self, white_eval_bot, black_eval_bot):
        self.white_eval_bot = white_eval_bot
        self.black_eval_bot = black_eval_bot

    def update_evaluation(self, white_eval, black_eval):
        """Update the evaluation display for both sides"""
        self.white_eval.config(text=f"White: {white_eval:+.1f}")
        self.black_eval.config(text=f"Black: {black_eval:+.1f}")

    def ask_promotion(self):
        """Ask user for pawn promotion piece"""
        choices = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}
        while True:
            resp = simpledialog.askstring("Promotion", "Promote pawn to (q,r,b,n):", parent=self.root)
            if resp is None:
                return chess.QUEEN
            key = resp.lower().strip()
            if key in choices:
                return choices[key]

    def copy_pgn(self):
        """Copy the current game's PGN to the clipboard"""
        try:
            pgn = chess.pgn.Game.from_board(self.board)
            pgn.headers["White"] = "Human" if self.white_player == "human" else self.white_player.true_name()
            pgn.headers["Black"] = "Human" if self.black_player == "human" else self.black_player.true_name()
            pgn_str = str(pgn)
            self.root.clipboard_clear()
            self.root.clipboard_append(pgn_str)
            # brief status message
            self.status.config(text="PGN copied to clipboard")
            self.root.after(2000, lambda: self.status.config(text=""))
        except Exception as e:
            self.status.config(text=f"PGN copy failed: {e}")
            self.root.after(3000, lambda: self.status.config(text=""))

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
        # refresh PGN text each redraw
        pgn = chess.pgn.Game.from_board(self.board)

        white_eval = 0
        black_eval = 0
        # evaluation bots take precedence; otherwise use the player bot if it's not human
        if self.white_eval_bot is not None:
            white_eval = self.white_eval_bot.evaluate(self.board)
        elif self.white_player != "human":
            white_eval = self.white_player.evaluate(self.board)
        else:
            white_eval = math.nan
        
        if self.black_eval_bot is not None:
            black_eval = self.black_eval_bot.evaluate(self.board)
        elif self.black_player != "human":
            black_eval = self.black_player.evaluate(self.board)
        else:
            black_eval = math.nan

        self.update_evaluation(white_eval, black_eval)
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
            if sq in self.legal_targets:
                promotion = None
                moving_piece = self.board.piece_at(self.selected)
                # handle pawn promotion
                if moving_piece and moving_piece.piece_type == chess.PAWN:
                    rank = chess.square_rank(sq)
                    if rank == 0 or rank == 7:
                        promotion = self.ask_promotion()
                self.prev_sq = [self.selected, sq]
                self.board.push(chess.Move(self.selected, sq, promotion=promotion))
                self.after_player_move()

            self.selected = None
            self.legal_targets.clear()
            self.legal_moves.clear()

        self.draw()

    def bot_turn(self):
        # kick off a bot move computation in a background thread so the UI stays responsive
        if self.board.is_game_over():
            return

        current_player = self.white_player if self.board.turn == chess.WHITE else self.black_player
        if current_player == 'human' or current_player is None:
            return

        # copy board for thread safety; the original board may be modified by user events
        board_copy = self.board.copy()

        def compute_move():
            move = current_player.choose_move(board_copy)
            # schedule application of the move back on the main thread
            self.root.after(0, lambda: self._apply_bot_move(move))

        threading.Thread(target=compute_move, daemon=True).start()

    def _apply_bot_move(self, move):
        # this runs on the Tkinter main thread
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
        if self.update_status():
            return
        self.root.after(self.move_time, self.bot_turn)

    def run(self):
        self.root.mainloop()