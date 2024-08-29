import tkinter as tk
import random
from collections import deque
from copy import deepcopy

# Game state
class GameState:
    def __init__(self, board_size=3, num_walls=1, player=None, enemy=None, walls=None, depth=0):
        self.N = board_size
        N = self.N
        if N % 2 == 0:
            raise ValueError('The board size must be an odd number.')
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.player = player if player != None else [0] * 2
        self.enemy = enemy if enemy != None else [0] * 2
        self.walls = walls if walls != None else [0] * ((N - 1) ** 2)
        self.depth = depth
        self.draw_depth = 30

        if player == None or enemy == None:
            init_pos = N * (N - 1) + N // 2
            self.player[0] = init_pos
            self.player[1] = num_walls
            self.enemy[0] = init_pos 
            self.enemy[1] = num_walls

     # Check if it's a loss
    def is_lose(self):
        if self.enemy[0] // self.N == 0:
            return True
        return False

    # Check if it's a draw
    def is_draw(self):
        return self.depth >= self.draw_depth
    
    # Check if the game is over
    def is_done(self):
        return self.is_lose() or self.is_draw()
    
    def pieces_array(self):
        N = self.N
        def pieces_of(pieces):
            tables = []

            table = [0] * (N ** 2)
            table[pieces[0]] = 1
            tables.append(table)
                
            table = [pieces[1]] * (N ** 2)
            tables.append(table)

            return tables
        
        def walls_of(walls):
            tables = []

            table_h = [0] * (N ** 2)
            table_v = [0] * (N ** 2)

            for wp in range((N - 1) ** 2):
                x, y = wp // (N - 1), wp % (N - 1)

                if x < (N - 1) // 2 and y < (N - 1) // 2:
                    pos = N * x + y
                elif x > (N - 1) // 2 and y < (N - 1) // 2:
                    pos = N * x + (y + 1)
                elif x < (N - 1) // 2 and y > (N - 1) // 2:
                    pos = N * (x + 1) + y
                else:
                    pos = N * (x + 1) + (y + 1)

                if walls[wp] == 1:
                    table_h[pos] = 1
                elif walls[wp] == 2:
                    table_v[pos] = 1
                
            tables.append(table_h)
            tables.append(table_v)

            return tables
        
        return [pieces_of(self.player), pieces_of(self.enemy), walls_of(self.walls)]
    
    def legal_actions(self):
        """
        0 - (N ** 2 - 1): Move to a position
        N ** 2- (N ** 2 + (N - 1) ** 2 - 1): Place a horizontal wall
        (N ** 2 + (N - 1) ** 2) - (N ** 2 + 2 * (N - 1) ** 2 - 1): Place a vertical wall
        """
        actions = []
        actions.extend(self.legal_actions_pos(self.player[0]))

        if self.player[1] > 0:
            for pos in range((self.N - 1) ** 2):
                actions.extend(self.legal_actions_wall(pos))
                
        return actions

    def legal_actions_pos(self, pos):
        actions = []

        N = self.N
        walls = self.walls
        ep = self.enemy[0]

        x, y = pos // N, pos % N
        for dx, dy in self.directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N:
                np = N * nx + ny
                wp = (N - 1) * nx + ny

                if nx < x:
                    if y == 0:
                        if walls[wp] != 1:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if nx > 0 and walls[wp - (N - 1)] != 1:
                                    nnp = np - N
                                    actions.append(nnp)
                                elif (nx == 0 and walls[wp] != 2) or (nx > 0 and walls[wp - (N - 1)] != 2 and walls[wp] != 2):
                                    nnp = np + 1
                                    actions.append(nnp)
                    elif y == (N - 1):
                        if walls[wp - 1] != 1:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if nx > 0 and walls[wp - (N - 1) - 1] != 1:
                                    nnp = np -  N
                                    actions.append(nnp)
                                elif (nx == 0 and walls[wp - 1] != 2) or (nx > 0 and walls[wp - (N - 1) - 1] != 2 and walls[wp - 1] != 2):
                                    nnp = np - 1
                                    actions.append(nnp)
                    else:
                        if walls[wp - 1] != 1 and walls[wp] != 1:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if nx > 0 and walls[wp - (N - 1)] != 1 and walls[wp - (N - 1) - 1] != 1:
                                    nnp = np - N
                                    actions.append(nnp)
                                else:
                                    if (nx == 0 and walls[wp - 1] != 2) or (nx > 0 and walls[wp - (N - 1) - 1] != 2 and walls[wp - 1] != 2):
                                        nnp = np - 1
                                        actions.append(nnp)
                                    if (nx == 0 and walls[wp] != 2) or (nx > 0 and walls[wp - (N - 1)] != 2 and walls[wp] != 2):
                                        nnp = np + 1
                                        actions.append(nnp)
                if nx > x:
                    if y == 0:
                        if walls[wp - (N - 1)] != 1:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if nx < (N - 1) and walls[wp] != 1:
                                    nnp = np + N
                                    actions.append(nnp)
                                elif (nx == (N - 1) and walls[wp - (N - 1)] != 2) or (nx < (N - 1) and walls[wp - (N - 1)] != 2 and walls[wp] != 2):
                                    nnp = np + 1
                                    actions.append(nnp)
                    elif y == (N - 1):
                        if walls[wp - (N - 1) - 1] != 1:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if nx < (N - 1) and walls[wp - 1] != 1:
                                    nnp = np + N
                                    actions.append(nnp)
                                elif (nx == (N - 1) and walls[wp - (N - 1) - 1] != 2) or (nx < (N - 1) and walls[wp - (N - 1) - 1] != 2 and walls[wp - 1] != 2):
                                    nnp = np - 1
                                    actions.append(nnp)
                    else:
                        if walls[wp - (N - 1) - 1] != 1 and walls[wp - (N - 1)] != 1:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if nx < (N - 1) and walls[wp - 1] != 1 and walls[wp] != 1:
                                    nnp = np + N
                                    actions.append(nnp)
                                else:
                                    if (nx == (N - 1) and walls[wp - (N - 1) - 1] != 2) or (nx < (N - 1) and walls[wp - (N - 1) - 1] != 2 and walls[wp - 1] != 2):
                                        nnp = np - 1
                                        actions.append(nnp)
                                    if (nx == (N - 1) and walls[wp - (N - 1)] != 2) or (nx < (N - 1) and walls[wp - (N - 1)] != 2 and walls[wp] != 2):
                                        nnp = np + 1
                                        actions.append(nnp)
                if ny < y:
                    if x == 0:
                        if walls[wp] != 2:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if ny > 0 and walls[wp - 1] != 2:
                                    nnp = np - 1
                                    actions.append(nnp)
                                elif (ny == 0 and walls[wp] != 1) or (ny > 0 and walls[wp - 1] != 1 and walls[wp] != 1):
                                    nnp = np + N
                                    actions.append(nnp)
                    elif x == (N - 1):
                        if walls[wp - (N - 1)] != 2:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if ny > 0 and walls[wp - (N - 1) - 1] != 2:
                                    nnp = np - 1
                                    actions.append(nnp)
                                elif (ny == 0 and walls[wp - (N - 1)] != 1) or (ny > 0 and walls[wp - (N - 1) - 1] != 2 and walls[wp - (N - 1)] != 1):
                                    nnp = np - N
                                    actions.append(nnp)
                    else:
                        if walls[wp - (N - 1)] != 2 and walls[wp] != 2:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if ny > 0 and walls[wp - (N - 1) - 1] != 2 and walls[wp - 1] != 2:
                                    nnp = np - 1
                                    actions.append(nnp)
                                else:
                                    if (ny == 0 and walls[wp - (N - 1)] != 1) or (ny > 0 and walls[wp - (N - 1) - 1] != 2 and walls[wp - (N - 1)] != 1):
                                        nnp = np - N
                                        actions.append(nnp)
                                    if (ny == 0 and walls[wp] != 1) or (ny > 0 and (walls[wp - 1] != 1 or walls[wp] != 1)):
                                        nnp = np + N
                                        actions.append(nnp)
                if ny > y:
                    if x == 0:
                        if walls[wp - 1] != 2:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if ny < (N - 1) and walls[wp] != 2:
                                    nnp = np + 1
                                    actions.append(nnp)
                                elif (ny == (N - 1) and walls[wp - 1] != 1) or (ny < (N - 1) and walls[wp - 1] != 1 and walls[wp] != 1):
                                    nnp = np + N
                                    actions.append(nnp)
                    elif x == (N - 1):
                        if walls[wp - (N - 1) - 1] != 2:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if ny < (N - 1) and walls[wp - (N - 1)] != 2:
                                    nnp = np + 1
                                    actions.append(nnp)
                                elif (ny == (N - 1) and walls[wp - (N - 1) - 1] != 1) or (ny < (N - 1) and walls[wp - (N - 1) - 1] != 1 and walls[wp - (N - 1)] != 1):
                                    nnp = np - N
                                    actions.append(nnp)
                    else:
                        if walls[wp - (N - 1) - 1] != 2 and walls[wp - 1] != 2:
                            if np + ep != N ** 2 - 1:
                                actions.append(np)
                            else:
                                if ny < (N - 1) and walls[wp - (N - 1)] != 2 and walls[wp] != 2:
                                    nnp = np + 1
                                    actions.append(nnp)
                                else:
                                    if (ny == (N - 1) and walls[wp - (N - 1) - 1] != 1) or (ny < (N - 1) and walls[wp - (N - 1) - 1] != 1 and walls[wp - (N - 1)] != 1):
                                        nnp = np - N
                                        actions.append(nnp)
                                    if (ny == (N - 1) and walls[wp - 1] != 1) or (ny < (N - 1) and (walls[wp - 1] != 1 or walls[wp] != 1)):
                                        nnp = np + N
                                        actions.append(nnp)

        return actions

    def legal_actions_wall(self, pos):
        N = self.N
        walls = self.walls
        def can_place_wall(orientation, pos):
            if walls[pos] != 0:
                return False
            x, y = pos // (N - 1), pos % (N - 1)
            if orientation == 1:
                if y == 0:
                    if walls[pos + 1] == 1:
                        return False
                elif y == (N - 2):
                    if walls[pos - 1] == 1:
                        return False
                else:
                    if walls[pos - 1] == 1 or walls[pos + 1] == 1:
                        return False
            else:
                if x == 0:
                    if walls[pos + (N - 1)] == 2:
                        return False
                elif x == (N - 2):
                    if walls[pos - (N - 1)] == 2:
                        return False
                else:
                    if walls[pos - (N - 1)] == 2 or walls[pos + (N - 1)] == 2:
                        return False
            return True

        def can_reach_goal(orientation, pos):
            def bfs(state):
                queue = deque([state.player[0]])
                visited = set()
                while queue:
                    pos = queue.popleft()
                    nps = state.legal_actions_pos(pos)
                    for np in nps:
                        x, y = np // N, np % N
                        if y == 0:
                            return True
                        if np not in visited:
                            visited.add(np)
                            queue.append(np)
                return False

            self.walls[pos] = orientation

            player_state = GameState(board_size=N, player=self.player.copy(), enemy=self.enemy.copy(), walls=deepcopy(self.walls), depth=self.depth)

            can_reach_player = bfs(player_state)

            action = pos
            if orientation == 1:
                action += N ** 2
            else:
                action += N ** 2 + (N - 1) ** 2

            enemy_state = player_state.next(action)

            can_reach_enemy = bfs(enemy_state)

            self.walls[pos] = 0

            return can_reach_player and can_reach_enemy
    
        actions = []

        if can_place_wall(1, pos) and can_reach_goal(1, pos):
            actions.append(N ** 2 + pos)
        if can_place_wall(2, pos) and can_reach_goal(2, pos):
            actions.append(N ** 2 + (N - 1) ** 2 + pos)

        return actions
    
    def rotate_walls(self):
        N = self.N
        rotated_walls = [0] * len(self.walls)
        for i in range((N - 1) ** 2):
            rotated_walls[i] = self.walls[(N - 1) ** 2 - 1 - i]
        self.walls = rotated_walls
    
    def next(self, action):
        N = self.N
        # Create the next state
        state = GameState(board_size=N, player=self.player.copy(), enemy=self.enemy.copy(), walls=deepcopy(self.walls), depth=self.depth + 1)

        if action < N ** 2:
            # Move piece
            state.player[0] = action
        elif action < N ** 2 + (N - 1) ** 2:
            # Place horizontal wall
            pos = action - N ** 2
            state.walls[pos] = 1
            state.player[1] -= 1
        else:
            # Place vertical wall
            pos = action - N ** 2 - (N - 1) ** 2
            state.walls[pos] = 2
            state.player[1] -= 1

        state.rotate_walls()

        # Swap players
        state.player, state.enemy = state.enemy, state.player

        return state
    
    # Check if it's the first player's turn
    def is_first_player(self):
        return self.depth % 2 == 0



# Defining the Game UI
class GameUI(tk.Frame):
    # Initialization
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master.title('Quoridor')

        # Generating the game state
        self.state = GameState()
        self.N = self.state.N
        self.D = 200  # Cell size (pixels)
        self.L = self.N * self.D  # Canvas size

        self.select = -1  # Selection (-1: none, 0~(N*N-1): square)
        self.placing_wall = False  # Flag to indicate if we are placing a wall

        # Main frame layout
        self.grid()

        # Creating the canvas for the game board
        self.c = tk.Canvas(self, width=self.L, height=self.L, highlightthickness=0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.grid(row=1, column=1, padx=10, pady=10)

        # Displaying the player's walls on the left
        self.player_walls_frame = tk.Frame(self)
        self.player_walls_frame.grid(row=1, column=2, padx=10, pady=10)
        self.player_walls = tk.Label(self.player_walls_frame, text="Player Walls", anchor="center", justify=tk.CENTER, font=('Helvetica', 24))
        self.player_walls.pack()

        # Displaying the enemy's walls on the right
        self.enemy_walls_frame = tk.Frame(self)
        self.enemy_walls_frame.grid(row=1, column=0, padx=10, pady=10)
        self.enemy_walls = tk.Label(self.enemy_walls_frame, text="Enemy Walls", anchor="center", justify=tk.CENTER, font=('Helvetica', 24))
        self.enemy_walls.pack()

        # Displaying the action buttons below the game board
        self.controls_frame = tk.Frame(self)
        self.controls_frame.grid(row=2, column=1, padx=10, pady=10)
        self.wall_button = tk.Button(self.controls_frame, text="Place Wall", command=self.place_wall_mode)
        self.wall_button.pack()

        self.wall_direction = tk.StringVar(value="horizontal")
        self.wall_horizontal_button = tk.Radiobutton(self.controls_frame, text="Horizontal", variable=self.wall_direction, value="horizontal")
        self.wall_vertical_button = tk.Radiobutton(self.controls_frame, text="Vertical", variable=self.wall_direction, value="vertical")
        self.wall_horizontal_button.pack()
        self.wall_vertical_button.pack()

        # Result message
        self.result_message = tk.Label(self, text="", font=('Helvetica', 60))
        self.result_message.grid(row=0, column=1, pady=10)

        # Updating the drawing
        self.on_draw()

    def place_wall_mode(self):
        self.placing_wall = not self.placing_wall
        self.wall_button.config(text="Move Piece" if self.placing_wall else "Place Wall")

    # Human's turn
    def turn_of_human(self, event):
        N = self.N
        D = self.D
        # If the game is over
        if self.state.is_done():
            return

        # If it is not the first player's turn
        if not self.state.is_first_player():
            return

        # Calculate the selection and move position
        if self.placing_wall:
            x, y = (event.x - D // 2) // D, (event.y - D // 2) // D
            print(x, y)
            if 0 <= x < N - 1 and 0 <= y < N - 1:
                self.place_wall(x, y)
        else:
            x, y = event.x // D, event.y // D
            self.select = N * y + x
            action = self.select

            # Convert selection and move to action

            # If the action is not legal
            if not (action in self.state.legal_actions()):
                self.select = -1
                self.on_draw()
                return

            # Get the next state
            self.state = self.state.next(action)
            self.select = -1
            self.on_draw()

        # AI's turn
        self.master.after(500, self.turn_of_ai)

    def place_wall(self, x, y):
        N = self.N
        # Adjusted logic for placing walls at grid points
        if self.wall_direction.get() == "horizontal":
            action = N ** 2 + (N - 1) * y + x
        else:
            action = N ** 2 + (N - 1) ** 2 + (N - 1) * y + x

        # Check if the action is legal
        if action in self.state.legal_actions():
            # Get the next state
            self.state = self.state.next(action)
            self.placing_wall = False
            self.wall_button.config(text="Place Wall")
            self.on_draw()
        else:
            self.placing_wall = False
            self.wall_button.config(text="Place Wall")
            self.on_draw()

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

    # Draw the piece
    def draw_piece(self, index, color):
        N = self.N
        D = self.D
        x = (index % N) * D
        y = (index // N) * D
        margin = D // 10
        self.c.create_oval(x + margin, y + margin, x + D - margin, y + D - margin, fill=color, outline='black')

    # Draw the walls
    def draw_walls(self):
        N = self.N
        D = self.D
        for i in range(len(self.state.walls)):
            x, y = i % (N - 1), i // (N - 1)
            if self.state.walls[i] == 1:
                x1, y1 = x * D, (y + 1) * D
                x2, y2 = (x + 2) * D, (y + 1) * D
                self.c.create_line(x1, y1, x2, y2, width=16.0, fill='#D1B575')
            elif self.state.walls[i] == 2:
                x1, y1 = (x + 1) * D, y * D
                x2, y2 = (x + 1) * D, (y + 2) * D
                self.c.create_line(x1, y1, x2, y2, width=16.0, fill='#D1B575')

    # Update the drawing
    def on_draw(self):
        N = self.N
        D = self.D
        L = self.L
        is_first_player = self.state.is_first_player()

        # Grid
        self.c.delete('all')
        self.c.create_rectangle(0, 0, L, L, width=0.0, fill='#4B4B4B')
        for i in range(1, N):
            self.c.create_line(i * D, 0, i * D, L, width=16.0, fill='#8B0000')
            self.c.create_line(0, i * D, L, i * D, width=16.0, fill='#8B0000')

        # Pieces
        p_pos = self.state.player[0] if is_first_player else self.state.enemy[0]
        e_pos = self.state.enemy[0] if is_first_player else self.state.player[0]
        e_pos = N ** 2 - 1 - e_pos

        self.draw_piece(p_pos, '#D2B48C')
        self.draw_piece(e_pos, '#5D3A3A')

        p_walls = self.state.player[1] if is_first_player else self.state.enemy[1]
        e_walls = self.state.enemy[1] if is_first_player else self.state.player[1]

        # Update the wall count
        self.player_walls.config(text=f"Player Walls\n{p_walls}")
        self.enemy_walls.config(text=f"Enemy Walls\n{e_walls}")

        if not is_first_player:
            self.state.rotate_walls()

        # Walls
        self.draw_walls()

        if not is_first_player:
            self.state.rotate_walls()
