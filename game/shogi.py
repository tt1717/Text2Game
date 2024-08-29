import tkinter as tk
import random

class GameState:
    def __init__(self, board_size=9, player=None, enemy=None, depth=0):
        self.N = board_size
        self.depth = depth

        # Initialize the board
        self.board = [[' ' for _ in range(self.N)] for _ in range(self.N)]
        
        # Set up initial board for Shogi (simplified version for this example)
        self.setup_board()

        if player is None or enemy is None:
            self.player = {'K': [(0, 4)]}  # King for player 1, at initial position (simplified)
            self.enemy = {'k': [(8, 4)]}  # King for player 2, at initial position (simplified)
        else:
            self.player = player
            self.enemy = enemy

    def setup_board(self):
        # Set up a simplified initial board for Shogi (only Kings are placed as an example)
        self.board[0][4] = 'K'  # Player 1's King
        self.board[8][4] = 'k'  # Player 2's King

    def is_lose(self):
        # Check if the player has lost (if their King is captured)
        if not self.player['K']:
            return True
        return False

    def is_draw(self):
        # Check if the game is a draw (a simple check for demonstration purposes)
        if self.depth >= 100:  # Arbitrary limit to prevent infinite games
            return True
        return False
    
    def is_done(self):
        # The game is done if either player has lost or the game is a draw
        return self.is_lose() or self.is_draw()
    
    def legal_actions(self):
        # Determine the legal actions (moves) for the current player
        actions = []
        # In a real game, this would check all pieces and determine valid moves
        # Here, we simplify by checking moves for the King only
        for pos in self.player['K']:
            x, y = pos
            # Example moves: up, down, left, right (assuming board bounds)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.N and 0 <= ny < self.N:
                    actions.append((x, y, nx, ny))  # (from_x, from_y, to_x, to_y)
        return actions
    
    def next(self, action):
        N = self.N
        # Create the next state
        state = GameState(board_size=N, player=self.player.copy(), enemy=self.enemy.copy(), depth=self.depth + 1)

        # Execute action
        x, y, nx, ny = action
        piece = state.board[x][y]
        state.board[x][y] = ' '
        state.board[nx][ny] = piece

        # Update piece positions
        if piece.isupper():  # Player 1's piece
            state.player['K'].remove((x, y))
            state.player['K'].append((nx, ny))
        else:  # Player 2's piece
            state.enemy['k'].remove((x, y))
            state.enemy['k'].append((nx, ny))

        # Swap players
        state.player, state.enemy = state.enemy, state.player

        return state
    
    def is_first_player(self):
        return self.depth % 2 == 0


class GameUI(tk.Frame):
    def __init__(self, master=None, board_size=9):
        tk.Frame.__init__(self, master)
        self.master.title('Shogi Game')
        
        # Game state
        self.state = GameState(board_size=board_size)
        self.N = self.state.N
        self.L = 50 * self.N  # Board size (can be adjusted for better appearance)
        
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

        # Simplified: Assume user always selects a valid move
        legal_moves = self.state.legal_actions()
        if legal_moves:
            action = random.choice(legal_moves)
            self.state = self.state.next(action)
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
                self.c.create_rectangle(x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size, fill="beige")
                
                piece = self.state.board[x][y]
                if piece != ' ':
                    self.c.create_text(x * cell_size + cell_size / 2, y * cell_size + cell_size / 2, text=piece, font=("Helvetica", 24))
