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

# Lichess brown theme
LIGHT = "#f0d9b5"
DARK = "#b58863"
PREV_LIGHT = "#cdd16e"
PREV_DARK = "#aaa23a"
HIGHLIGHT = "#fa6d6d"
SELECT_LIGHT = "#dde26a"
SELECT_DARK = "#b9bb2e"
COORD_LIGHT = "#b58863"
COORD_DARK = "#f0d9b5"

BOARD_SIZE = 8 * SQUARE_SIZE
COORD_PAD = 20  # space for rank/file labels

class PromotionDialog(tk.Toplevel):
    def __init__(self, parent, color):
        super().__init__(parent)
        self.title("Promote pawn")
        self.resizable(False, False)
        self.result = chess.QUEEN
        self.grab_set()

        pieces = [
            (chess.QUEEN,  "Queen"),
            (chess.ROOK,   "Rook"),
            (chess.BISHOP, "Bishop"),
            (chess.KNIGHT, "Knight"),
        ]

        tk.Label(self, text="Promote to:", font=("Arial", 12, "bold"), pady=6).pack()

        self.var = tk.StringVar(value="Queen")
        frame = tk.Frame(self)
        frame.pack(padx=20, pady=4)

        for piece, name in pieces:
            rb = tk.Radiobutton(
                frame, text=name, variable=self.var, value=name,
                font=("Arial", 11), anchor="w", width=8
            )
            rb.pack(side=tk.LEFT, padx=4)

        tk.Button(self, text="Confirm", font=("Arial", 11), command=self._confirm,
                  bg="#4a7c59", fg="white", padx=10, pady=4).pack(pady=8)

        self.transient(parent)
        self.wait_window(self)

    def _confirm(self):
        mapping = {"Queen": chess.QUEEN, "Rook": chess.ROOK,
                   "Bishop": chess.BISHOP, "Knight": chess.KNIGHT}
        self.result = mapping[self.var.get()]
        self.destroy()


class chessGUI:
    def __init__(self, white_player='human', black_player=None):
        self.piece_set = "classic"

        self.move_time = 100
        self.board = chess.Board()
        self.white_player = white_player
        self.black_player = black_player

        self.white_eval_bot = None
        self.black_eval_bot = None

        self.root = tk.Tk()
        self.root.title("Chess Handler")
        self.root.configure(bg="#2b2b2b")

        icon_image = tk.PhotoImage(file='base/chessHandlerIcon.png')
        self.root.iconphoto(True, icon_image)

        # Canvas includes coord padding
        self.canvas = tk.Canvas(
            self.root,
            width=BOARD_SIZE + COORD_PAD,
            height=BOARD_SIZE + COORD_PAD,
            bg="#2b2b2b",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)

        self.images = {}
        self.load_images()
        self.make_move_images()

        self.selected = None
        self.legal_targets = []
        self.legal_moves = []
        self.prev_sq = []

        # Status bar
        self.status = tk.Label(
            self.root, text="", font=("Arial", 13, "bold"),
            bg="#2b2b2b", fg="#e0e0e0", pady=4
        )
        self.status.pack()

        # Eval panel
        self.eval_frame = tk.Frame(self.root, bg="#1e1e1e", pady=6)
        self.eval_frame.pack(fill=tk.X, padx=10, pady=(0, 8))

        TARGET_SIZE = (48, 48)

        whitebot_image = None
        blackbot_image = None
        try: whitebot_image = white_player.IMAGE_DATA
        except: pass
        try: blackbot_image = black_player.IMAGE_DATA
        except: pass

        try: self.white_eval_clamp = white_player.max_eval()
        except: self.white_eval_clamp = 10
        
        try: self.black_eval_clamp = black_player.max_eval()
        except: self.white_eval_clamp = 10
        
        # White side
        self.white_side = tk.Frame(self.eval_frame, bg="#1e1e1e")
        self.white_side.pack(side=tk.LEFT, padx=10)

        if whitebot_image:
            try:
                data = whitebot_image.split("base64,")[-1] if "base64," in str(whitebot_image) else whitebot_image
                img_data = b64decode(data)
                pil_img = Image.open(BytesIO(img_data)).resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                self.white_img = ImageTk.PhotoImage(pil_img)
                tk.Label(self.white_side, image=self.white_img, bg="#1e1e1e").pack(side=tk.LEFT, padx=4)
            except Exception as e:
                print(f"White image error: {e}")

        self.white_eval = tk.Label(
            self.white_side, text="White: 0.0",
            font=("Consolas", 12), fg="#f0f0f0", bg="#1e1e1e", padx=8
        )
        self.white_eval.pack(side=tk.LEFT)

        # Black side
        self.black_side = tk.Frame(self.eval_frame, bg="#1e1e1e")
        self.black_side.pack(side=tk.RIGHT, padx=10)

        if blackbot_image:
            try:
                data = blackbot_image.split("base64,")[-1] if "base64," in str(blackbot_image) else blackbot_image
                img_data = b64decode(data)
                pil_img = Image.open(BytesIO(img_data)).resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                self.black_img = ImageTk.PhotoImage(pil_img)
                tk.Label(self.black_side, image=self.black_img, bg="#1e1e1e").pack(side=tk.RIGHT, padx=4)
            except Exception as e:
                print(f"Black image error: {e}")

        self.black_eval = tk.Label(
            self.black_side, text="Black: 0.0",
            font=("Consolas", 12), fg="#f0f0f0", bg="#1e1e1e", padx=8
        )
        self.black_eval.pack(side=tk.RIGHT)

        # Eval bar (thin horizontal bar showing advantage)
        self.eval_bar_canvas = tk.Canvas(
            self.root, width=BOARD_SIZE + COORD_PAD, height=10,
            bg="#1e1e1e", highlightthickness=0
        )
        self.eval_bar_canvas.pack(padx=10)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(pady=6)
        self.copy_pgn_btn = tk.Button(
            btn_frame, text="Copy PGN", command=self.copy_pgn,
            font=("Arial", 10), bg="#4a4a4a", fg="white",
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2"
        )
        self.copy_pgn_btn.pack(side=tk.LEFT, padx=4)

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw()
        self.root.after(self.move_time, self.bot_turn)

    def get_eval_bots(self, white_eval_bot, black_eval_bot):
        self.white_eval_bot = white_eval_bot
        self.black_eval_bot = black_eval_bot

    def update_evaluation(self, white_eval, black_eval):
        try: wname = self.white_player.true_name()
        except: wname = "Player"
        try: bname = self.black_player.true_name()
        except: bname = "Player"

        def fmt(e):
            return f"{e:+.1f}" if not math.isnan(e) else "—"

        self.white_eval.config(text=f"White ({wname}): {fmt(white_eval)}")
        self.black_eval.config(text=f"Black ({bname}): {fmt(black_eval)}")
        self._draw_eval_bar(white_eval)

    def _draw_eval_bar(self, white_eval):
        self.eval_bar_canvas.delete("all")
        w = BOARD_SIZE + COORD_PAD
        if math.isnan(white_eval):
            self.eval_bar_canvas.create_rectangle(0, 0, w, 10, fill="#555", outline="")
            return
        if white_eval >= 0:
            clamped = min(white_eval, self.white_eval_clamp)
            ratio = 0.5 + (clamped / self.white_eval_clamp) * 0.5
        else:
            clamped = max(white_eval, -self.black_eval_clamp)
            ratio = 0.5 + (clamped / self.black_eval_clamp) * 0.5
        split = int(w * ratio)
        self.eval_bar_canvas.create_rectangle(0, 0, w, 10, fill="#333", outline="")
        self.eval_bar_canvas.create_rectangle(0, 0, split, 10, fill="#f0f0f0", outline="")

    def ask_promotion(self):
        color = self.board.turn
        dlg = PromotionDialog(self.root, color)
        return dlg.result

    def copy_pgn(self):
        try:
            pgn = chess.pgn.Game.from_board(self.board)
            pgn.headers["White"] = "Human" if self.white_player == "human" else self.white_player.true_name()
            pgn.headers["Black"] = "Human" if self.black_player == "human" else self.black_player.true_name()
            self.root.clipboard_clear()
            self.root.clipboard_append(str(pgn))
            self.status.config(text="PGN copied to clipboard")
            self.root.after(2000, lambda: self.status.config(text=""))
        except Exception as e:
            self.status.config(text=f"PGN copy failed: {e}")
            self.root.after(3000, lambda: self.status.config(text=""))

    def load_images(self):
        piece_map = {
            "P": f"{self.piece_set}/white-pawn",
            "N": f"{self.piece_set}/white-knight",
            "B": f"{self.piece_set}/white-bishop",
            "R": f"{self.piece_set}/white-rook",
            "Q": f"{self.piece_set}/white-queen",
            "K": f"{self.piece_set}/white-king",
            "p": f"{self.piece_set}/black-pawn",
            "n": f"{self.piece_set}/black-knight",
            "b": f"{self.piece_set}/black-bishop",
            "r": f"{self.piece_set}/black-rook",
            "q": f"{self.piece_set}/black-queen",
            "k": f"{self.piece_set}/black-king",
        }
        size = float(self.get_psdat_line(0))
        for symbol, name in piece_map.items():
            img = Image.open(f"pieces/{name}.png").convert("RGBA")
            new_w = int(img.width * size)
            new_h = int(img.height * size)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            self.images[symbol] = ImageTk.PhotoImage(img)

    def make_move_images(self):
        dot_size = 25
        ring_size = SQUARE_SIZE - 12

        def make_dot(bg_hex, alpha=80):
            bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (1, 3, 5))
            bg_img = Image.new("RGBA", (dot_size, dot_size), bg_rgb + (255,))
            dot = Image.new("RGBA", (dot_size, dot_size), (0, 0, 0, 0))
            d = ImageDraw.Draw(dot)
            d.ellipse((0, 0, dot_size-1, dot_size-1), fill=(30, 30, 30, alpha))
            return ImageTk.PhotoImage(Image.alpha_composite(bg_img, dot))

        self.move_dot_light = make_dot(LIGHT)
        self.move_dot_dark  = make_dot(DARK)
        self.move_dot_prev_light = make_dot(PREV_LIGHT)
        self.move_dot_prev_dark  = make_dot(PREV_DARK)

        ring = Image.new("RGBA", (ring_size, ring_size), (0, 0, 0, 0))
        d = ImageDraw.Draw(ring)
        d.ellipse((3, 3, ring_size-4, ring_size-4), outline=(30, 30, 30, 180), width=5)
        self.move_ring = ImageTk.PhotoImage(ring)

    def _sq_to_canvas(self, sq):
        """Return top-left canvas (x, y) for a square, accounting for coord padding."""
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        x = COORD_PAD + f * SQUARE_SIZE
        y = (7 - r) * SQUARE_SIZE
        return x, y

    def draw(self):
        white_eval = math.nan
        black_eval = math.nan

        if self.white_eval_bot is not None:
            white_eval = self.white_eval_bot.evaluate(self.board)
        elif self.white_player != "human":
            white_eval = self.white_player.evaluate(self.board)

        if self.black_eval_bot is not None:
            black_eval = self.black_eval_bot.evaluate(self.board)
        elif self.black_player != "human":
            black_eval = self.black_player.evaluate(self.board)

        self.update_evaluation(white_eval, black_eval)
        self.canvas.delete("all")

        # Draw squares
        for r in range(8):
            for f in range(8):
                sq = chess.square(f, r)
                x1 = COORD_PAD + f * SQUARE_SIZE
                y1 = (7 - r) * SQUARE_SIZE

                is_light = (r + f) % 2 == 0

                if sq == self.selected:
                    color = SELECT_LIGHT if is_light else SELECT_DARK
                elif sq in self.prev_sq:
                    color = PREV_LIGHT if is_light else PREV_DARK
                elif self.board.is_check() and sq == self.board.king(self.board.turn):
                    color = HIGHLIGHT
                else:
                    color = LIGHT if is_light else DARK

                self.canvas.create_rectangle(
                    x1, y1, x1 + SQUARE_SIZE, y1 + SQUARE_SIZE,
                    fill=color, outline=color
                )

                # Rank labels (left side)
                if f == 0:
                    self.canvas.create_text(
                        COORD_PAD - 6, y1 + SQUARE_SIZE // 2,
                        text=str(r + 1), font=("Arial", 9, "bold"),
                        fill=COORD_LIGHT if is_light else COORD_DARK,
                        anchor="e"
                    )

                # File labels (bottom)
                if r == 0:
                    self.canvas.create_text(
                        x1 + SQUARE_SIZE // 2, BOARD_SIZE + 6,
                        text=chess.FILE_NAMES[f], font=("Arial", 9, "bold"),
                        fill=COORD_LIGHT if is_light else COORD_DARK
                    )

        # Draw pieces
        for r in range(8):
            for f in range(8):
                sq = chess.square(f, r)
                x1 = COORD_PAD + f * SQUARE_SIZE
                y1 = (7 - r) * SQUARE_SIZE
                piece = self.board.piece_at(sq)
                if piece:
                    self.canvas.create_image(
                        x1 + SQUARE_SIZE // 2,
                        y1 + SQUARE_SIZE // 2,
                        image=self.images[piece.symbol()]
                    )

        # Draw move hints
        for move in self.legal_moves:
            to_sq = move.to_square
            f = chess.square_file(to_sq)
            r = chess.square_rank(to_sq)
            x = COORD_PAD + f * SQUARE_SIZE + SQUARE_SIZE // 2
            y = (7 - r) * SQUARE_SIZE + SQUARE_SIZE // 2
            is_light = (r + f) % 2 == 0

            if self.board.piece_at(to_sq):
                self.canvas.create_image(x, y, image=self.move_ring)
            else:
                if to_sq in self.prev_sq:
                    dot = self.move_dot_prev_light if is_light else self.move_dot_prev_dark
                else:
                    dot = self.move_dot_light if is_light else self.move_dot_dark
                self.canvas.create_image(x, y, image=dot)

    def square_at(self, x, y):
        file = (x - COORD_PAD) // SQUARE_SIZE
        rank = 7 - (y // SQUARE_SIZE)
        if 0 <= file <= 7 and 0 <= rank <= 7:
            return chess.square(file, rank)
        return None

    def compute_targets(self, square):
        self.legal_targets.clear()
        self.legal_moves.clear()
        for m in self.board.legal_moves:
            if m.from_square == square:
                self.legal_targets.append(m.to_square)
                self.legal_moves.append(m)

    def set_board(self, fen):
        self.board.set_fen(fen)

    def update_status(self):
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            self.status.config(text=f"✓ Checkmate! {winner} wins.")
            return True
        if self.board.is_stalemate():
            self.status.config(text="Stalemate — Draw.")
            return True
        if self.board.is_check():
            side = "White" if self.board.turn == chess.WHITE else "Black"
            self.status.config(text=f"⚠ {side} is in check!")
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
        if sq is None:
            return

        if self.selected is None:
            piece = self.board.piece_at(sq)
            if piece and piece.color == self.board.turn:
                self.selected = sq
                self.compute_targets(sq)
        else:
            if sq in self.legal_targets:
                promotion = None
                moving_piece = self.board.piece_at(self.selected)
                if moving_piece and moving_piece.piece_type == chess.PAWN:
                    rank = chess.square_rank(sq)
                    if rank == 0 or rank == 7:
                        promotion = self.ask_promotion()
                self.prev_sq = [self.selected, sq]
                board_before = self.board.copy()
                self._notify_bots_of_move(chess.Move(self.selected, sq, promotion=promotion), board_before)
                self.board.push(chess.Move(self.selected, sq, promotion=promotion))
                self.selected = None
                self.legal_targets.clear()
                self.legal_moves.clear()
                self.draw()
                self.after_player_move()
                return
            else:
                # Allow re-selecting a different own piece
                piece = self.board.piece_at(sq)
                if piece and piece.color == self.board.turn:
                    self.selected = sq
                    self.compute_targets(sq)
                else:
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

        board_copy = self.board.copy()

        def compute_move():
            move = current_player.choose_move(board_copy)
            self.root.after(0, lambda: self._apply_bot_move(move))

        threading.Thread(target=compute_move, daemon=True).start()

    def _apply_bot_move(self, move):
        if move is not None:
            self.prev_sq.clear()
            curr_board = self.board.piece_map().copy()
            board_before = self.board.copy()
            self._notify_bots_of_move(move, board_before)
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

    def _notify_bots_of_move(self, move, board_before):
        for player in (self.white_player, self.black_player):
            if player != 'human' and player is not None:
                if hasattr(player, 'update_castling_status'):
                    player.update_castling_status(move, board_before)

    def get_psdat_line(self, line):
        with open(f"pieces/{self.piece_set}/{self.piece_set}.psdat", "r") as file:
            return file.readlines()[line]

    def run(self):
        self.root.mainloop()
