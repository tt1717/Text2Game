import tkinter as tk
import random

class GameState:
    def __init__(self, board_size=(4, 3), board=None, pieces_in_hand=None, depth=0):
        self.rows, self.cols = board_size
        self.depth = depth

        # Initialize the board with default pieces
        if board:
            self.board = [row[:] for row in board]
        else:
            self.board = [[0] * self.cols for _ in range(self.rows)]
            # Enemy's pieces (top row)
            self.board[0][0], self.board[0][1], self.board[0][2] = -2, -4, -3  # キリン, ライオン, ゾウ
            # Enemy's chick piece
            self.board[1][1] = -1  # ひよこ
            # Player's chick piece
            self.board[2][1] = 1   # ひよこ
            # Player's pieces (bottom row)
            self.board[3][0], self.board[3][1], self.board[3][2] = 3, 4, 2  # ゾウ, ライオン, キリン

        # Initialize captured pieces (pieces in hand)
        if pieces_in_hand:
            self.pieces_in_hand = {
                True: pieces_in_hand[True][:],
                False: pieces_in_hand[False][:]
            }
        else:
            self.pieces_in_hand = {True: [], False: []}  # {is_first_player: [pieces]}

    def is_lose(self):
        winner = self.get_winner()
        if winner is None:
            return False
        return (winner == 'second') if self.is_first_player() else (winner == 'first')

    def is_draw(self):
        # Implement draw condition if any
        return False  # No draw condition implemented

    def is_done(self):
        return self.get_winner() is not None

    def get_winner(self):
        # Check for win conditions
        first_player_lion_exists = False
        second_player_lion_exists = False
        first_player_lion_in_opponent_back_rank = False
        second_player_lion_in_opponent_back_rank = False
        for y in range(self.rows):
            for x in range(self.cols):
                piece = self.board[y][x]
                if piece == 4:
                    first_player_lion_exists = True
                    if y == 0:
                        first_player_lion_in_opponent_back_rank = True
                elif piece == -4:
                    second_player_lion_exists = True
                    if y == self.rows - 1:
                        second_player_lion_in_opponent_back_rank = True

        if not first_player_lion_exists:
            return 'second'
        if not second_player_lion_exists:
            return 'first'
        if first_player_lion_in_opponent_back_rank:
            return 'first'
        if second_player_lion_in_opponent_back_rank:
            return 'second'
        return None

    def legal_actions(self):
        actions = []
        is_first = self.is_first_player()

        # Generate move actions for pieces on the board
        for y in range(self.rows):
            for x in range(self.cols):
                piece = self.board[y][x]
                if (is_first and piece > 0) or (not is_first and piece < 0):
                    moves = self.get_piece_moves(piece, y, x, is_first)
                    for dy, dx in moves:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.rows and 0 <= nx < self.cols:
                            target_piece = self.board[ny][nx]
                            if (is_first and target_piece <= 0) or (not is_first and target_piece >= 0):
                                # Empty square or opponent's piece
                                actions.append(('move', y, x, ny, nx))

        # Generate drop actions for pieces in hand
        pieces_in_hand = self.pieces_in_hand[is_first]
        for piece in pieces_in_hand:
            for y in range(self.rows):
                for x in range(self.cols):
                    if self.board[y][x] == 0:
                        actions.append(('drop', piece, y, x))
        return actions

    def get_piece_moves(self, piece, y, x, is_first_player):
        moves = []
        piece_type = abs(piece)

        if piece_type == 1:  # Chick
            dy = -1 if is_first_player else 1
            moves.append((dy, 0))
        elif piece_type == 2:  # Giraffe
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            moves.extend(directions)
        elif piece_type == 3:  # Elephant
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            moves.extend(directions)
        elif piece_type == 4:  # Lion
            directions = [(-1, -1), (-1, 0), (-1, 1),
                          (0, -1),          (0, 1),
                          (1, -1),  (1, 0), (1, 1)]
            moves.extend(directions)
        elif piece_type == 5:  # Hen (promoted chick)
            # Hen can move to all adjacent squares except backward diagonals
            if is_first_player:
                directions = [(-1, -1), (-1, 0), (-1, 1),
                              (0, -1),          (0, 1),
                                         (1, 0)]
            else:
                directions = [(1, -1),  (1, 0),  (1, 1),
                              (0, -1),          (0, 1),
                                         (-1, 0)]
            moves.extend(directions)
        return moves

    def next(self, action):
        state = GameState(board_size=(self.rows, self.cols), board=self.board, pieces_in_hand=self.pieces_in_hand, depth=self.depth + 1)

        is_first = self.is_first_player()
        if action[0] == 'move':
            _, y1, x1, y2, x2 = action
            piece = state.board[y1][x1]
            target_piece = state.board[y2][x2]
            # Move the piece
            state.board[y1][x1] = 0
            # Handle capture
            if target_piece != 0:
                captured_piece_type = abs(target_piece)
                if captured_piece_type == 5:
                    # Captured piece was a Hen, demote it to Chick
                    captured_piece_type = 1
                # Add captured piece to player's hand (unpromoted and with correct sign)
                captured_piece = captured_piece_type
                state.pieces_in_hand[is_first].append(captured_piece)
            # Handle promotion
            # If the piece is a Chick moving into back rank, promote to Hen
            if abs(piece) == 1 and ((is_first and y2 == 0) or (not is_first and y2 == self.rows - 1)):
                piece = 5 if piece > 0 else -5  # Promote to Hen
            state.board[y2][x2] = piece
        elif action[0] == 'drop':
            _, piece, y, x = action
            piece_to_place = piece if is_first else -piece
            state.board[y][x] = piece_to_place
            # Remove the piece from the player's hand
            state.pieces_in_hand[is_first].remove(piece)
        return state

    def is_first_player(self):
        return self.depth % 2 == 0

class GameUI(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master.title('どうぶつしょうぎ')

        self.state = GameState()
        self.rows = self.state.rows
        self.cols = self.state.cols
        self.L = 300  # Size of the board
        self.cell_size = self.L // max(self.rows, self.cols)

        self.selected_piece = None  # For keeping track of selected piece
        self.selected_piece_pos = None
        self.player_captured_positions = []
        self.opponent_captured_positions = []

        self.ai_selected_piece_pos = None
        self.ai_placed_piece_pos = None
        self.ai_selected_captured_index = None

        self.player_placed_piece_pos = None  # For highlighting player's placement
        self.player_selected_captured_index = None

        self.grid()
        self.result_message = tk.Label(self, text="", font=("Helvetica", 14))
        self.result_message.grid(row=0, column=1)

        self.opponent_captured_canvas = tk.Canvas(self, width=self.L, height=self.cell_size, highlightthickness=0)
        self.opponent_captured_canvas.grid(row=1, column=1)

        self.c = tk.Canvas(self, width=self.L, height=self.L, highlightthickness=0)
        self.c.bind('<Button-1>', self.on_click)
        self.c.grid(row=2, column=1, padx=10, pady=10)

        self.player_captured_canvas = tk.Canvas(self, width=self.L, height=self.cell_size, highlightthickness=0)
        self.player_captured_canvas.bind('<Button-1>', self.on_player_captured_click)
        self.player_captured_canvas.grid(row=3, column=1)

        self.message_label = tk.Label(self, text="", font=("Helvetica", 12))
        self.message_label.grid(row=4, column=1)

        self.on_draw()

    def on_click(self, event):
        if self.state.is_done():
            return
        if not self.state.is_first_player():
            return

        x = event.x // self.cell_size
        y = event.y // self.cell_size

        if not (0 <= x < self.cols and 0 <= y < self.rows):
            self.message_label.config(text="Invalid Move")
            self.on_draw()
            return

        if self.selected_piece is None:
            # First click, select a piece
            piece = self.state.board[y][x]
            if piece > 0:
                self.selected_piece = piece
                self.selected_piece_pos = (y, x)
                self.highlight_square(y, x)
            else:
                self.message_label.config(text="Invalid Move")
        else:
            # Second click, move or drop the piece
            action = None
            if self.selected_piece_pos:
                # Moving a piece on the board
                y1, x1 = self.selected_piece_pos
                action = ('move', y1, x1, y, x)
            else:
                # Dropping a piece from hand
                action = ('drop', self.selected_piece, y, x)

            if action in self.state.legal_actions():
                self.state = self.state.next(action)
                self.player_placed_piece_pos = (y, x)
                self.selected_piece = None
                self.selected_piece_pos = None
                self.player_selected_captured_index = None
                self.message_label.config(text="")
                self.on_draw()
                if self.state.is_done():
                    self.display_result()
                    self.master.after(2000, self.reset_game)
                else:
                    self.master.after(500, self.turn_of_ai)
            else:
                # Invalid move
                self.message_label.config(text="Invalid Move")
                self.on_draw()

    def on_player_captured_click(self, event):
        if self.state.is_done():
            return
        if not self.state.is_first_player():
            return

        x = event.x
        for idx, (x1, x2, piece) in enumerate(self.player_captured_positions):
            if x1 <= x <= x2:
                # Clicked on this captured piece
                self.selected_piece = piece
                self.selected_piece_pos = None  # Indicate we are dropping
                self.player_selected_captured_index = idx
                self.highlight_captured_piece(idx, color="green")
                self.on_draw()
                break

    def highlight_square(self, y, x):
        self.on_draw()
        self.c.create_rectangle(x * self.cell_size, y * self.cell_size,
                                (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                outline="blue", width=3)

    def highlight_player_move(self):
        # Highlight player's placed piece
        if self.player_placed_piece_pos:
            y, x = self.player_placed_piece_pos
            self.c.create_rectangle(x * self.cell_size, y * self.cell_size,
                                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                    outline="blue", width=3)

    def highlight_ai_move(self):
        # Highlight AI's selected piece and placement
        if self.ai_selected_piece_pos:
            y, x = self.ai_selected_piece_pos
            self.c.create_rectangle(x * self.cell_size, y * self.cell_size,
                                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                    outline="red", width=3)
        if self.ai_placed_piece_pos:
            y, x = self.ai_placed_piece_pos
            self.c.create_rectangle(x * self.cell_size, y * self.cell_size,
                                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                    outline="red", width=3)

    def highlight_captured_piece(self, idx, color="green"):
        x = idx * self.cell_size
        y = 0
        self.player_captured_canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size,
                                                     outline=color, width=3)

    def highlight_opponent_captured_piece(self):
        if self.ai_selected_captured_index is not None:
            idx = self.ai_selected_captured_index
            x = idx * self.cell_size
            y = 0
            self.opponent_captured_canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size,
                                                           outline="green", width=3)

    def turn_of_ai(self):
        if self.state.is_done():
            self.display_result()
            self.master.after(2000, self.reset_game)
            return

        actions = self.state.legal_actions()
        if actions:
            action = random.choice(actions)
            # Store AI's move for highlighting
            self.ai_selected_piece_pos = None
            self.ai_placed_piece_pos = None
            self.ai_selected_captured_index = None

            if action[0] == 'move':
                _, y1, x1, y2, x2 = action
                self.ai_selected_piece_pos = (y1, x1)
                self.ai_placed_piece_pos = (y2, x2)
            elif action[0] == 'drop':
                # For drop, select from captured pieces
                piece = action[1]
                self.ai_selected_piece_pos = None  # AI selects from captured pieces, not on board
                self.ai_placed_piece_pos = (action[2], action[3])
                # Find index of the piece in AI's captured pieces
                try:
                    self.ai_selected_captured_index = self.state.pieces_in_hand[False].index(piece)
                except ValueError:
                    self.ai_selected_captured_index = None

            self.state = self.state.next(action)
            self.player_placed_piece_pos = None  # Clear player's highlight
            self.on_draw()

        if self.state.is_done():
            self.display_result()
            self.master.after(2000, self.reset_game)
        else:
            self.message_label.config(text="")
            # Clear AI move highlights after some time
            self.master.after(500, self.clear_ai_highlights)

    def clear_ai_highlights(self):
        self.ai_selected_piece_pos = None
        self.ai_placed_piece_pos = None
        self.ai_selected_captured_index = None
        self.on_draw()

    def display_result(self):
        winner = self.state.get_winner()
        if winner == 'first':
            self.result_message.config(text="You Win!", fg="blue")
        elif winner == 'second':
            self.result_message.config(text="You Lose!", fg="red")

    def reset_game(self):
        self.state = GameState()
        self.selected_piece = None
        self.selected_piece_pos = None
        self.player_placed_piece_pos = None
        self.player_selected_captured_index = None
        self.message_label.config(text="")
        self.result_message.config(text="")
        self.ai_selected_piece_pos = None
        self.ai_placed_piece_pos = None
        self.ai_selected_captured_index = None
        self.on_draw()

    def on_draw(self):
        self.c.delete("all")
        # Draw the board
        for y in range(self.rows):
            for x in range(self.cols):
                fill_color = "lightblue" if y < 2 else "lightgreen"
                self.c.create_rectangle(x * self.cell_size, y * self.cell_size,
                                        (x + 1) * self.cell_size, (y + 1) * self.cell_size, fill=fill_color)
                piece = self.state.board[y][x]
                if piece != 0:
                    self.draw_piece(self.c, x * self.cell_size, y * self.cell_size, piece)

        # Draw horizontal line at the bottom of the board (adjusted to 3 cells)
        self.c.create_line(0, self.L, self.cols * self.cell_size, self.L, fill='black', width=2)

        # Highlight moves
        self.highlight_ai_move()
        self.highlight_player_move()
        self.highlight_opponent_captured_piece()

        self.draw_opponent_captured_pieces()
        self.draw_player_captured_pieces()

    def draw_piece(self, canvas, x, y, piece):
        color = "black" if piece > 0 else "white"
        piece_names = {
            1: "ひ", 2: "キ", 3: "ゾ", 4: "ラ", 5: "に",
            -1: "ひ", -2: "キ", -3: "ゾ", -4: "ラ", -5: "に"
        }
        canvas.create_text(x + self.cell_size // 2,
                           y + self.cell_size // 2,
                           text=piece_names[piece], font=("Helvetica", 24), fill=color)

    def draw_captured_piece(self, canvas, x, y, piece):
        color = "black" if piece > 0 else "white"
        piece_names = {
            1: "ひ", 2: "キ", 3: "ゾ", 4: "ラ", 5: "に",
            -1: "ひ", -2: "キ", -3: "ゾ", -4: "ラ", -5: "に"
        }
        canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill="lightgrey")
        canvas.create_text(x + self.cell_size // 2,
                           y + self.cell_size // 2,
                           text=piece_names[piece], font=("Helvetica", 24), fill=color)

    def draw_player_captured_pieces(self):
        self.player_captured_canvas.delete("all")
        self.player_captured_positions = []
        pieces = self.state.pieces_in_hand[True]
        for i, piece in enumerate(pieces):
            x = i * self.cell_size
            y = 0
            self.draw_captured_piece(self.player_captured_canvas, x, y, piece)
            self.player_captured_positions.append((x, x + self.cell_size, piece))
        # Highlight selected captured piece if any
        if self.player_selected_captured_index is not None:
            idx = self.player_selected_captured_index
            x = idx * self.cell_size
            y = 0
            self.player_captured_canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size,
                                                         outline="green", width=3)
        # Draw horizontal line at the bottom (adjusted to captured pieces length)
        length = max(self.L, len(pieces) * self.cell_size)
        self.player_captured_canvas.create_line(0, self.cell_size, length, self.cell_size, fill='black', width=2)

    def draw_opponent_captured_pieces(self):
        self.opponent_captured_canvas.delete("all")
        self.opponent_captured_positions = []
        pieces = self.state.pieces_in_hand[False]
        for i, piece in enumerate(pieces):
            x = i * self.cell_size
            y = 0
            self.draw_captured_piece(self.opponent_captured_canvas, x, y, -piece)
            self.opponent_captured_positions.append((x, x + self.cell_size, piece))
        # Highlight AI's selected captured piece if any
        if self.ai_selected_captured_index is not None:
            idx = self.ai_selected_captured_index
            x = idx * self.cell_size
            y = 0
            self.opponent_captured_canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size,
                                                           outline="green", width=3)
        # Draw horizontal line at the bottom (adjusted to captured pieces length)
        length = max(self.L, len(pieces) * self.cell_size)
        self.opponent_captured_canvas.create_line(0, self.cell_size, length, self.cell_size, fill='black', width=2)

if __name__ == "__main__":
    root = tk.Tk()
    game = GameUI(master=root)
    game.mainloop()
