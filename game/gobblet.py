import tkinter as tk
import random
import tkinter.messagebox


class GameState:
    def __init__(self, board_size=3, board=None, player_pieces=None, enemy_pieces=None, depth=0, current_player=1):
        self.N = board_size
        N = self.N
        self.depth = depth
        self.current_player = current_player  # 1 for player, -1 for enemy

        if board is None:
            # Initialize empty board
            self.board = [[[] for _ in range(N)] for _ in range(N)]
        else:
            # Deep copy of the board
            self.board = [[cell[:] for cell in row] for row in board]

        if player_pieces is None:
            # Initialize player pieces (size: count)
            self.player_pieces = {1: 2, 2: 2, 3: 2}
        else:
            self.player_pieces = player_pieces.copy()

        if enemy_pieces is None:
            self.enemy_pieces = {1: 2, 2: 2, 3: 2}
        else:
            self.enemy_pieces = enemy_pieces.copy()

    def is_lose(self):
        N = self.N
        # Create a grid of the top pieces' players
        grid = [[0]*N for _ in range(N)]
        for x in range(N):
            for y in range(N):
                stack = self.board[x][y]
                if stack:
                    top_piece = stack[-1]
                    grid[x][y] = top_piece[0]  # Player number

        # Check rows, columns, and diagonals for three in a line of opponent's pieces
        enemy = -self.current_player
        lines = []

        # Rows
        for x in range(N):
            lines.append([grid[x][y] for y in range(N)])
        # Columns
        for y in range(N):
            lines.append([grid[x][y] for x in range(N)])
        # Diagonals
        lines.append([grid[i][i] for i in range(N)])
        lines.append([grid[i][N-1-i] for i in range(N)])

        for line in lines:
            if all(cell == enemy for cell in line):
                return True
        return False

    def is_draw(self):
        # Simplified: game is never a draw in this implementation
        return False

    def is_done(self):
        return self.is_lose() or self.is_draw()

    def legal_actions(self):
        actions = []
        N = self.N

        # For each piece size that the player has in hand
        for size in [1, 2, 3]:
            if self.player_pieces.get(size, 0) > 0:
                # Try placing it on the board
                for x in range(N):
                    for y in range(N):
                        stack = self.board[x][y]
                        if not stack:
                            # Cell is empty, can place any piece
                            actions.append(('place', size, x, y))
                        else:
                            top_piece = stack[-1]
                            top_size = top_piece[1]
                            if size > top_size:
                                # Can gobble up the top piece
                                actions.append(('place', size, x, y))

        # For each piece that the player has on the board and is visible (on top)
        for x in range(N):
            for y in range(N):
                stack = self.board[x][y]
                if stack:
                    top_piece = stack[-1]
                    if top_piece[0] == self.current_player:
                        size = top_piece[1]
                        # Try moving this piece to another cell
                        for dx in range(N):
                            for dy in range(N):
                                if (dx, dy) == (x, y):
                                    continue
                                target_stack = self.board[dx][dy]
                                if not target_stack:
                                    # Can move to empty cell
                                    actions.append(('move', x, y, dx, dy))
                                else:
                                    target_top_piece = target_stack[-1]
                                    target_size = target_top_piece[1]
                                    if size > target_size:
                                        # Can gobble up the top piece
                                        actions.append(('move', x, y, dx, dy))
        return actions

    def next(self, action):
        N = self.N
        # Create the next state
        state = GameState(board_size=N, board=self.board, player_pieces=self.player_pieces,
                          enemy_pieces=self.enemy_pieces, depth=self.depth + 1, current_player=self.current_player)

        # Apply the action
        action_type = action[0]
        if action_type == 'place':
            size, x, y = action[1], action[2], action[3]
            # Place the piece
            state.board = [[cell[:] for cell in row] for row in self.board]  # Deep copy of board
            state.board[x][y].append((self.current_player, size))
            # Decrease the player's piece count
            state.player_pieces = self.player_pieces.copy()
            state.player_pieces[size] -= 1

            # Copy enemy_pieces
            state.enemy_pieces = self.enemy_pieces.copy()

        elif action_type == 'move':
            from_x, from_y, to_x, to_y = action[1], action[2], action[3], action[4]
            # Move the piece
            state.board = [[cell[:] for cell in row] for row in self.board]  # Deep copy of board
            moving_piece = state.board[from_x][from_y].pop()
            state.board[to_x][to_y].append(moving_piece)
            # player_pieces and enemy_pieces remain the same
            state.player_pieces = self.player_pieces.copy()
            state.enemy_pieces = self.enemy_pieces.copy()

        # Swap players
        state.current_player = -self.current_player
        # Swap player_pieces and enemy_pieces
        state.player_pieces, state.enemy_pieces = state.enemy_pieces, state.player_pieces

        return state

    def is_first_player(self):
        return self.current_player == 1


class GameUI(tk.Frame):
    # Initialization
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master.title('Gobblet Gobblers')

        self.L = 300  # Canvas size
        self.grid_size = 3  # Board is 3x3
        self.cell_size = self.L / self.grid_size  # Use floating point division

        # Generating the game state
        self.state = GameState()
        self.N = self.state.N

        # Main frame layout
        self.grid()

        # Creating the canvas for the game board
        self.c = tk.Canvas(self, width=self.L, height=self.L, highlightthickness=0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.grid(row=1, column=1, padx=10, pady=10)

        # Result message label
        self.result_message = tk.Label(self, text="", font=("Helvetica", 16))
        self.result_message.grid(row=0, column=1)

        self.selected_piece = None
        self.selected_size = None

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

        # Get the clicked cell
        x = int(event.x // self.cell_size)
        y = int(event.y // self.cell_size)
        if x < 0 or x >= N or y < 0 or y >= N:
            return

        if self.selected_piece is None:
            # First click: select a piece or select a cell to place a piece
            stack = self.state.board[x][y]
            if stack and stack[-1][0] == self.state.current_player:
                # The top piece is the player's own piece, select it for movement
                self.selected_piece = (x, y)
                self.on_draw()  # Update drawing to show selection
            else:
                # Empty cell or opponent's piece, prompt for placing a piece
                # Get list of available sizes
                available_sizes = [size for size in [1, 2, 3] if self.state.player_pieces.get(size, 0) > 0]
                if not available_sizes:
                    # No pieces to place
                    return

                # Prompt the user to select a size
                size = self.prompt_for_size(available_sizes)
                if size is None:
                    return

                # Check if placing the piece here is legal
                action = ('place', size, x, y)
                if action in self.state.legal_actions():
                    self.state = self.state.next(action)
                    self.on_draw()
                    if self.state.is_done():
                        self.display_result()
                        self.master.after(1000, self.reset_game)
                        return
                    else:
                        # AI's turn
                        self.master.after(500, self.turn_of_ai)
                else:
                    # Illegal action
                    tk.messagebox.showinfo("Invalid Move", "You cannot place the piece here.")
        else:
            # Second click: select destination for movement
            from_x, from_y = self.selected_piece
            action = ('move', from_x, from_y, x, y)
            if action in self.state.legal_actions():
                self.state = self.state.next(action)
                self.on_draw()
                self.selected_piece = None
                if self.state.is_done():
                    self.display_result()
                    self.master.after(1000, self.reset_game)
                    return
                else:
                    # AI's turn
                    self.master.after(500, self.turn_of_ai)
            else:
                # Illegal move
                tk.messagebox.showinfo("Invalid Move", "You cannot move the piece there.")
                self.selected_piece = None
                self.on_draw()  # Update drawing to remove selection

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
        self.selected_piece = None

    def prompt_for_size(self, available_sizes):
        size_names = {1: "Small", 2: "Medium", 3: "Large"}
        self.selected_size = None
        dialog = tk.Toplevel()
        dialog.title("Select Piece Size")
        dialog.grab_set()  # Make the dialog modal
        tk.Label(dialog, text="Select a piece size to place:").pack()
        for s in available_sizes:
            button = tk.Button(dialog, text=size_names[s], command=lambda s=s: self.set_selected_size(s, dialog))
            button.pack()
            button.configure(height=1)  # Set button height to avoid NSButton warning
        dialog.wait_window()
        return self.selected_size

    def set_selected_size(self, size, dialog):
        self.selected_size = size
        dialog.destroy()

    # Update the drawing
    def on_draw(self):
        N = self.N
        self.c.delete("all")
        # Draw grid lines
        for i in range(N + 1):
            x = i * self.cell_size
            self.c.create_line(x, 0, x, self.L)
            self.c.create_line(0, x, self.L, x)
        # Ensure the rightmost and bottom lines are drawn
        self.c.create_line(self.L - 1, 0, self.L - 1, self.L)
        self.c.create_line(0, self.L - 1, self.L, self.L - 1)

        # Draw selected cell background
        if self.selected_piece:
            x, y = self.selected_piece
            self.c.create_rectangle(x * self.cell_size, y * self.cell_size,
                                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                    fill="#DDFFDD", outline="green", width=3)
        else:
            # No cell is selected
            pass

        # Draw pieces
        for x in range(N):
            for y in range(N):
                stack = self.state.board[x][y]
                if stack:
                    # Get the top piece
                    top_piece = stack[-1]
                    player = top_piece[0]
                    size = top_piece[1]
                    # Determine color
                    color = "blue" if player == 1 else "red"
                    # Draw the piece
                    # Size mapping: 1 -> small, 2 -> medium, 3 -> large
                    size_scale = {1: 0.4, 2: 0.6, 3: 0.8}
                    s = self.cell_size * size_scale[size]
                    cx = x * self.cell_size + self.cell_size / 2
                    cy = y * self.cell_size + self.cell_size / 2
                    self.c.create_oval(cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2, fill=color, outline="black")

    # Run the game
if __name__ == '__main__':
    root = tk.Tk()
    game = GameUI(master=root)
    game.mainloop()
