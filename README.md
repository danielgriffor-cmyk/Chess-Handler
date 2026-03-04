Chess Handler is an open-source chess handler that lets users play against and create their own simple chess bots.

Recent versions include basic multithreading for the AI engine – bot searches are executed in background threads and the GUI no longer freezes while the computer is thinking. Additionally the top‑level move search uses multiple cores when available, so higher depths finish faster.

It isn't very optimized so be warned.

This engine utilizes the `python-chess` library, which offers a variety of tools for efficient chess gaming.

# How to play

You can play against a chess bot or even another human opponent (locally) by using the string `"human"` in place of a color declaration in the `ChessHandler.py` file,

for example, 
```python
white_bot = "human"
black_bot = ComplexChessBot.Bot(color = chess.BLACK, depth = 3)
```
lets the human (white) play against the complex chess bot (black)

Just remember to set the color of the bot to its color when it does evaluation, else it will play the worst possible moves (to it).

# How to make a chess bot

To make a chess bot, you must create your own class. This class should extend the base chess bot, formatted as
```python
from ChessBotBase import Bot

class Bot(Bot):
  ...
```
The class must be named Bot.

When running this bot, you get a `NotImplementedError`. This is because there is no evaluation logic.

To write evaluation logic, overwrite the `evaluate` function.

for example,
```python
from base.ChessBotBase import Bot
import chess

class Bot(Bot):
  def evaluate(self, board):
    if board.is_stalemate():
      return 100
    return 0
```
always plays for stalemate if it can see it, or else it plays the first legal move. 

Chess bots also automatically play mate in one, but do not look for mate in more than one.


Another thing that you need to add to your chess bot, is a name.

A name is really easy to add to your bot. Using the stalemate bot as an example:

```python
from base.ChessBotBase import Bot
import chess

class Bot(Bot):
  def name(self):
    return "Stalemate Bot"

  def evaluate(self, board):
    if board.is_stalemate():
      return 100
    return 0
```

The evaluation function is based off of the bots color, which is stored as a `chess.Color` type in the variable `self.color`.
