import tkinter as tk
import random

class GameState:
    def __init__(self, board_size, player=None, enemy=None, depth=0):
        self.N = board_size
        self.depth = depth
        
        # Initialize the board
        self.board = [[0] * self.N for _ in range(self.N)]
        
        # Set initial positions (Assuming 1 is player, -1 is enemy, and 0 is empty)
        mid = self.N // 2
        self.board[mid-1][mid-1] = self.board[mid][mid] = 1
        self.board[mid-1][mid] = self.board[mid][mid-1] = -1
        
        if player is None or enemy is None:
            self.player = 1  # Assume player starts with 1
            self.enemy = -1  # Enemy starts with -1
        else:
            self.player = player
            self.enemy = enemy

    def is_lose(self):
        # Check if the enemy has more pieces or if there are no legal moves for the player
        if self.is_done() and self.count_pieces(self.player) < self.count_pieces(self.enemy):
            return True
        return False

    def is_draw(self):
        # Check if both players have the same number of pieces when no legal moves are left
        if self.is_done() and self.count_pieces(self.player) == self.count_pieces(self.enemy):
            return True
        return False
    
    def is_done(self):
        # Game is done if neither player has a legal move or the board is full
        return not any(self.legal_actions()) and not any(self.next().legal_actions())
    
    def legal_actions(self):
        actions = []
        for x in range(self.N):
            for y in range(self.N):
                if self.board[x][y] == 0 and self.can_place(x, y):
                    actions.append((x, y))
        return actions
    
    def next(self, action=None):
        # Create a new state with the updated board and switched players
        next_state = GameState(board_size=self.N, player=self.player, enemy=self.enemy, depth=self.depth + 1)
        next_state.board = [row[:] for row in self.board]
        
        if action:
            x, y = action
            next_state.board[x][y] = self.player
            next_state.flip_pieces(x, y)
        
        # Swap players
        next_state.player, next_state.enemy = next_state.enemy, next_state.player
        return next_state
    
    def is_first_player(self):
        return self.depth % 2 == 0

    def can_place(self, x, y):
        # Check if a move can be placed at (x, y) and would flip at least one enemy piece
        if self.board[x][y] != 0:
            return False
        return any(self.check_direction(x, y, dx, dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)])
    
    def check_direction(self, x, y, dx, dy):
        # Check a specific direction for flippable pieces
        x += dx
        y += dy
        if not (0 <= x < self.N and 0 <= y < self.N) or self.board[x][y] != self.enemy:
            return False
        x += dx
        y += dy
        while 0 <= x < self.N and 0 <= y < self.N:
            if self.board[x][y] == 0:
                return False
            if self.board[x][y] == self.player:
                return True
            x += dx
            y += dy
        return False
    
    def flip_pieces(self, x, y):
        # Flip the pieces in all valid directions from the placed piece
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            if self.check_direction(x, y, dx, dy):
                self.flip_in_direction(x, y, dx, dy)
    
    def flip_in_direction(self, x, y, dx, dy):
        x += dx
        y += dy
        while self.board[x][y] == self.enemy:
            self.board[x][y] = self.player
            x += dx
            y += dy
    
    def count_pieces(self, player):
        return sum(row.count(player) for row in self.board)



class GameUI(tk.Frame):
    def __init__(self, master=None, board_size=8):
        tk.Frame.__init__(self, master)
        self.master.title('Othello Game')
        
        # Game state
        self.state = GameState(board_size=board_size)
        self.N = self.state.N
        self.L = 50 * self.N  # Board size (can be adjusted for better appearance)
        
        self.select = -1
        
        # Main frame layout
        self.grid()
        
        # Create canvas for game board
        self.c = tk.Canvas(self, width=self.L, height=self.L, highlightthickness=0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.grid(row=1, column=1, padx=10, pady=10)
        
        # Display result label
        self.result_message = tk.Label(self, text="", font=("Helvetica", 14))
        self.result_message.grid(row=0, column=1)
        
        self.on_draw()
        
    def turn_of_human(self, event):
        if self.state.is_done():
            return
        if not self.state.is_first_player():
            return

        x = event.x // (self.L // self.N)
        y = event.y // (self.L // self.N)
        
        if (x, y) in self.state.legal_actions():
            self.state = self.state.next((x, y))
            self.on_draw()
            if not self.state.is_done():
                self.master.after(500, self.turn_of_ai)
        
    def turn_of_ai(self):
        if self.state.is_done():
            self.display_result()
            self.master.after(1000, self.reset_game)
            return
        
        actions = self.state.legal_actions()
        if actions:
            action = random.choice(actions)
            self.state = self.state.next(action)
            self.on_draw()
            
        if self.state.is_done():
            self.display_result()
            self.master.after(1000, self.reset_game)
    
    def display_result(self):
        if self.state.is_draw():
            self.result_message.config(text="Draw", fg="black")
        elif self.state.is_lose():
            self.result_message.config(text="You Lose", fg="blue")
        else:
            self.result_message.config(text="You Win", fg="red")
    
    def reset_game(self):
        self.state = GameState(board_size=self.N)
        self.on_draw()
        self.result_message.config(text="")
    
    def on_draw(self):
        self.c.delete("all")
        cell_size = self.L // self.N
        
        for x in range(self.N):
            for y in range(self.N):
                color = "green"
                self.c.create_rectangle(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill=color)
                
                if self.state.board[x][y] == 1:
                    self.c.create_oval(x * cell_size + 5, y * cell_size + 5, (x + 1) * cell_size - 5, (y + 1) * cell_size - 5, fill="black")
                elif self.state.board[x][y] == -1:
                    self.c.create_oval(x * cell_size + 5, y * cell_size + 5, (x + 1) * cell_size - 5, (y + 1) * cell_size - 5, fill="white")
