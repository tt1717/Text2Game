import tkinter as tk
import random


class GameState:
    def __init__(self, board_size, player, enemy, depth=0):
        self.N = board_size
        N = self.N
        self.player = player
        self.enemy = enemy
        self.depth = depth

    def is_lose(self):
        # Check if it's a loss
        return None

    def is_draw(self):
        # Check if it's a draw
        return None
    
    # Check if the game is over
    def is_done(self):
        return self.is_lose() or self.is_draw()
    
    def legal_actions(self):
        actions = []
                
        return actions
    
    def next(self, action):
        N = self.N
        # Create the next state
        state = GameState(board_size=N, player=self.player.copy(), enemy=self.enemy.copy(), depth=self.depth + 1)

        # Swap players
        state.player, state.enemy = state.enemy, state.player

        return state
    
    # Check if it's the first player's turn
    def is_first_player(self):
        return self.depth % 2 == 0


class GameUI(tk.Frame):
    # Initialization
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master.title('Board Game')

        # Generating the game state
        self.state = GameState()
        self.N = self.state.N

        # Main frame layout
        self.grid()

        # Creating the canvas for the game board
        self.c = tk.Canvas(self, width=self.L, height=self.L, highlightthickness=0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.grid(row=1, column=1, padx=10, pady=10)

        # Updating the drawing
        self.on_draw()

    # Human's turn
    def turn_of_human(self, event):
        N = self.N
        # If the game is over
        if self.state.is_done():
            return

        # If it is not the first player's turn
        if not self.state.is_first_player():
            return
        
        # AI's turn
        self.master.after(500, self.turn_of_ai)

    # AI's turn
    def turn_of_ai(self):
        # If the game is over
        if self.state.is_done():
            self.display_result()
            self.master.after(1000, self.reset_game)
            return

        # Get the action
        actions = self.state.legal_actions()
        if actions:
            action = random.choice(actions)
            self.state = self.state.next(action)
            self.on_draw()

        if self.state.is_done():
            self.display_result()
            self.master.after(1000, self.reset_game)
            return

    def display_result(self):
        is_lose = self.state.is_lose() if self.state.is_first_player() else not self.state.is_lose()
        if is_lose:
            self.result_message.config(text="You Lose", fg="blue")
        else:
            self.result_message.config(text="You Win", fg="red")
    
    def reset_game(self):
        self.state = GameState()
        self.on_draw()
        self.result_message.config(text="")

    # Update the drawing
    def on_draw(self):
        N = self.N
        is_first_player = self.state.is_first_player()
