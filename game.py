class GameBoard:
    def __init__(self, layout):
        self.board = [list(row) for row in layout]
        self.rows = len(self.board)
        self.cols = len(self.board[0])

    def is_wall(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.board[row][col] == 'W'
        return True  # Treat out-of-bounds as walls

    def get_cell(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.board[row][col]
        return None

    def remove_item(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            item = self.board[row][col]
            if item == '.' or item == 'P':
                self.board[row][col] = ' '  # Mark as empty
                return item
        return None

class PacMan:
    def __init__(self, start_row, start_col):
        self.row = start_row
        self.col = start_col
        self.direction = 'RIGHT'  # Default direction
        self.lives = 3
        self.score = 0
        self.powered_up = False # Add a flag for power-up state

    def move(self, direction, game_board):
        new_row, new_col = self.row, self.col
        if direction == 'UP':
            new_row -= 1
        elif direction == 'DOWN':
            new_row += 1
        elif direction == 'LEFT':
            new_col -= 1
        elif direction == 'RIGHT':
            new_col += 1

        self.direction = direction # Update direction regardless of wall collision

        if not game_board.is_wall(new_row, new_col):
            self.row, self.col = new_row, new_col

    def eat_pellet(self):
        self.score += 10

    def eat_power_up(self):
        self.score += 50
        self.powered_up = True
        # We'll need a timer for the power-up effect in a later step

class Ghost:
    def __init__(self, start_row, start_col, mode='SCATTER'):
        self.row = start_row
        self.col = start_col
        self.mode = mode # SCATTER, CHASE, FRIGHTENED

    def move(self, game_board):
        # Basic random movement for now, avoiding walls
        import random
        possible_moves = []
        # Check UP
        if not game_board.is_wall(self.row - 1, self.col):
            possible_moves.append('UP')
        # Check DOWN
        if not game_board.is_wall(self.row + 1, self.col):
            possible_moves.append('DOWN')
        # Check LEFT
        if not game_board.is_wall(self.row, self.col - 1):
            possible_moves.append('LEFT')
        # Check RIGHT
        if not game_board.is_wall(self.row, self.col + 1):
            possible_moves.append('RIGHT')

        if possible_moves:
            chosen_move = random.choice(possible_moves)
            if chosen_move == 'UP':
                self.row -= 1
            elif chosen_move == 'DOWN':
                self.row += 1
            elif chosen_move == 'LEFT':
                self.col -= 1
            elif chosen_move == 'RIGHT':
                self.col += 1

    def check_collision_pacman(self, pacman_row, pacman_col):
        return self.row == pacman_row and self.col == pacman_col

from ai import MinimaxAgent # Import the AI Agent
import time # For potential sleep in the game loop

class Game:
    def __init__(self, layout, ai_agent_depth=None): # ai_agent_depth can be None for human player
        self.game_board = GameBoard(layout)
        self.ai_agent = None
        if ai_agent_depth is not None:
            self.ai_agent = MinimaxAgent(depth=ai_agent_depth)

        self.pacman_start_pos = None
        self.ghost_start_pos = []

        for r_idx, row in enumerate(layout):
            for c_idx, cell in enumerate(row):
                if cell == 'S':
                    self.pacman_start_pos = (r_idx, c_idx)
                elif cell == 'G':
                    self.ghost_start_pos.append((r_idx, c_idx))

        if self.pacman_start_pos is None:
            raise ValueError("Pac-Man start position 'S' not found in layout.")

        self.pacman = PacMan(self.pacman_start_pos[0], self.pacman_start_pos[1])

        self.ghosts = []
        for r, c in self.ghost_start_pos:
            self.ghosts.append(Ghost(r,c))
            # Remove 'G' from board after ghost is created
            if self.game_board.get_cell(r,c) == 'G':
                 self.game_board.board[r][c] = ' '


        # Remove 'S' from board after Pac-Man is created
        if self.game_board.get_cell(self.pacman.row, self.pacman.col) == 'S':
            self.game_board.board[self.pacman.row][self.pacman.col] = ' '


        self.game_state = 'PLAYING' # PLAYING, GAME_OVER, WIN
        self.power_up_timer = 0 # Timer for Pac-Man's power-up
        self.current_turn = 0 # To keep track of game turns for AI or display

    def update(self):
        # This method is called *after* Pac-Man has made a move (via handle_input)
        # or if no move is made but game needs to advance (e.g. just ghost moves, timers)
        if self.game_state != 'PLAYING':
            return

        # 1. Process Pac-Man's move (already done by handle_input externally, then PacMan.move)
        # PacMan.move() is called by handle_input

        # 2. Check for pellets/power-ups at Pac-Man's new position
        cell_content = self.game_board.get_cell(self.pacman.row, self.pacman.col)
        if cell_content == '.':
            self.pacman.eat_pellet()
            self.game_board.remove_item(self.pacman.row, self.pacman.col)
        elif cell_content == 'P':
            self.pacman.eat_power_up()
            self.game_board.remove_item(self.pacman.row, self.pacman.col)
            self.power_up_timer = 10 # Example: power-up lasts 10 updates
            # Change ghosts to FRIGHTENED mode
            for ghost in self.ghosts:
                ghost.mode = 'FRIGHTENED'


        # 3. Update power-up timer and state
        if self.pacman.powered_up:
            if self.power_up_timer > 0:
                self.power_up_timer -= 1
            else:
                self.pacman.powered_up = False
                # Change ghosts back to their default mode (e.g., CHASE or SCATTER)
                for ghost in self.ghosts:
                    ghost.mode = 'CHASE' # Or SCATTER, depending on your logic

        # 4. Update ghost positions
        for ghost in self.ghosts:
            ghost.move(self.game_board)

        # 5. Check for collisions (Pac-Man with ghosts)
        for ghost in self.ghosts:
            if ghost.check_collision_pacman(self.pacman.row, self.pacman.col):
                if self.pacman.powered_up:
                    # Pac-Man eats the ghost
                    self.pacman.score += 200 # Score for eating a ghost
                    # Reset ghost to start position or a "holding pen"
                    # For simplicity, let's reset to its initial start.
                    # This needs the initial start positions to be stored or passed.
                    # For now, let's find the first 'G' again or store it.
                    # A better way would be to store initial positions for each ghost.
                    # Let's assume ghost_start_pos stores these.
                    # This part needs refinement if multiple ghosts have distinct starts.
                    # For now, if there are multiple ghosts, they'll all reset to the first ghost's start.
                    # This should be improved by giving each ghost an individual start_pos attribute.
                    if self.ghost_start_pos: # Check if ghost_start_pos is not empty
                        ghost.row, ghost.col = self.ghost_start_pos[self.ghosts.index(ghost) % len(self.ghost_start_pos)]
                    ghost.mode = 'CHASE' # Or SCATTER
                else:
                    # Ghost catches Pac-Man
                    self.pacman.lives -= 1
                    if self.pacman.lives <= 0:
                        self.game_state = 'GAME_OVER'
                    else:
                        # Reset Pac-Man to his start position
                        self.pacman.row, self.pacman.col = self.pacman_start_pos
                        # Optionally, reset ghosts' positions too
                        for g_idx, g in enumerate(self.ghosts):
                            g.row, g.col = self.ghost_start_pos[g_idx % len(self.ghost_start_pos)]
                    break # Stop checking other ghosts if Pac-Man is caught

        # 6. Check for win condition (all pellets eaten)
        pellets_left = False
        for r in range(self.game_board.rows):
            for c in range(self.game_board.cols):
                if self.game_board.get_cell(r, c) == '.':
                    pellets_left = True
                    break
            if pellets_left:
                break

        if not pellets_left:
            self.game_state = 'WIN'

    def handle_input(self, direction):
        if self.game_state == 'PLAYING':
            self.pacman.move(direction, self.game_board)
            # After Pac-Man moves, immediately call update to process consequences:
            # eating pellets, ghost movement, collisions, game state changes.
            self.update()

    def play_ai_turn(self):
        if self.ai_agent and self.game_state == 'PLAYING':
            print(f"\n--- Turn {self.current_turn} (AI) ---")

            # Log moderately distant ghosts for focused analysis
            pac_r, pac_c = self.pacman.row, self.pacman.col
            moderately_distant_ghosts = []
            for g in self.ghosts:
                if g.mode != 'FRIGHTENED':
                    dist = abs(pac_r - g.row) + abs(pac_c - g.col)
                    if dist == 3 or dist == 4:
                        moderately_distant_ghosts.append(((g.row, g.col), dist))
            if moderately_distant_ghosts:
                print(f"PacMan at ({pac_r},{pac_c}). Moderately distant active ghosts: {moderately_distant_ghosts}")

            current_game_state_for_ai = self.get_state_for_ai()
            # Optional: Print AI's view of the board
            # print("AI sees board:")
            # for row in current_game_state_for_ai['board']:
            #     print("".join(row))

            action = self.ai_agent.get_best_action(self) # Pass current game instance
            print(f"AI chose action: {action}")
            self.handle_input(action) # This will move Pac-Man and trigger update()
            self.current_turn +=1
        elif self.game_state != 'PLAYING':
            print("Game is not in PLAYING state, AI turn skipped.")


    def is_game_over(self):
        return self.game_state == 'GAME_OVER' or self.game_state == 'WIN'

    def get_state_for_ai(self):
        # This method will be more fleshed out later.
        # For now, a simple representation:
        board_state = [row[:] for row in self.game_board.board] # Deep copy
        board_state[self.pacman.row][self.pacman.col] = 'S' # Mark Pac-Man
        for i, ghost in enumerate(self.ghosts):
            # Mark ghosts, potentially with numbers or different characters if needed
            # For now, just 'G'. If ghosts overlap, this will only show one.
            board_state[ghost.row][ghost.col] = 'G'

        return {
            "board": board_state,
            "pacman_pos": (self.pacman.row, self.pacman.col),
            "pacman_lives": self.pacman.lives,
            "pacman_score": self.pacman.score,
            "pacman_powered_up": self.pacman.powered_up,
            "power_up_timer": self.power_up_timer,
            "ghosts_pos": [(ghost.row, ghost.col) for ghost in self.ghosts],
            "ghosts_modes": [ghost.mode for ghost in self.ghosts],
            "game_state": self.game_state
        }

# Example Layout:
# WWWWWWWWWW
# W S  . P W
# W WWW.WW W
# W G . .  W
# W WWWWWWWW
# S = Pac-Man, G = Ghost, W = Wall, . = Pellet, P = Power-up

if __name__ == '__main__':
    layouts = {
        "Original": [
            "WWWWWWWWWW",
            "W S P. .GW",
            "W WWW.WW W",
            "W  . . . W",
            "W WWWWWWWW",
            "W G    P.W",
            "WWWWWWWWWW"
        ],
        "Open Field": [
            "WWWWWWWWWW",
            "W S  G   W",
            "W .  . . W",
            "W  .P. . W",
            "W .  . . W",
            "W   G  S W", # Second Pacman Start 'S' will be ignored, first one is taken. Ghost here.
            "WWWWWWWWWW"
        ],
        "Corridors": [
            "WWWWWWWWWW",
            "WS.P.G.W.W", # Start, pellet, Powerup, pellet, Ghost, pellet, Wall, pellet, Wall
            "W W W WW W",
            "W.W.W.G.PW", # pellet, Wall, pellet, Wall, pellet, Ghost, pellet, Powerup, Wall
            "W W W WW W",
            "W. . .S. .W", # Pellet, space, pellet, space, Second S (ignored), pellet, space, pellet, Wall
            "WWWWWWWWWW"
        ],
        "Simple Chase": [ # For observing ghost interaction primarily
            "WWWWWW",
            "WS G.W", # Pacman, Ghost, Pellet, Wall
            "W.P .W", # Pellet, Powerup, Pellet, Wall
            "WWWWWW"
        ]
    }

    ai_depth_to_test = 2 # Using depth 2 for quicker test runs
    max_turns_per_game = 30 # Max turns for each layout test

    for layout_name, layout_config in layouts.items():
        print(f"\n\n--- Starting Test Scenario: {layout_name} ---")
        # The second 'S' in "Open Field" and "Corridors" will be ignored by current Game constructor logic,
        # which takes the first 'S' it finds. This is acceptable for this test.
        # If a layout has no 'S' or no 'G', Game init will raise error or behave unexpectedly.
        # These layouts are assumed to be valid for basic testing.
        try:
            game = Game(layout_config, ai_agent_depth=ai_depth_to_test)
        except ValueError as e:
            print(f"Error initializing game for layout {layout_name}: {e}")
            continue

        print("Initial board state:")
        initial_ai_state = game.get_state_for_ai()
        for r_chars in initial_ai_state['board']: print("".join(r_chars))
        print(f"Pac-Man initial pos: {game.pacman_start_pos}")
        print(f"Ghost initial pos: {game.ghost_start_pos}")
        print(f"Lives: {game.pacman.lives}, Score: {game.pacman.score}")

        turn_count = 0
        if game.ai_agent:
            print(f"\n--- AI Controlled Game Start ({layout_name}) ---")
            while not game.is_game_over() and turn_count < max_turns_per_game:
                game.play_ai_turn() # AI makes a move, game updates

                current_board_state_for_display = game.get_state_for_ai()['board']
                for r_chars in current_board_state_for_display: print("".join(r_chars))

                print(f"Pac-Man pos: ({game.pacman.row}, {game.pacman.col})")
                print(f"Score: {game.pacman.score}, Lives: {game.pacman.lives}, PoweredUp: {game.pacman.powered_up} (Timer: {game.power_up_timer})")
                # Ensure ghost modes are printed; they are in game.ghosts list of objects
                ghost_details = []
                for g in game.ghosts:
                    ghost_details.append(f"({g.row},{g.col},{g.mode})")
                print(f"Ghosts: {', '.join(ghost_details)}")
                print(f"Game State: {game.game_state}")

                turn_count += 1
                if os.getenv("CI") != "true": # Avoid sleep in CI environment for faster tests
                    time.sleep(0.2) # Sleep to observe the game, reduced for faster multi-layout tests

            print(f"\n--- Game Over ({layout_name}: {game.game_state}) after {turn_count} turns ---")
            print(f"Final Score: {game.pacman.score}, Lives: {game.pacman.lives}")
        else:
            print(f"Skipping AI run for {layout_name} as no AI agent was initialized.")

    # Final section for manual testing if needed (no AI)
    if False: # Set to True to run a manual example
        print("\n--- Manual Game Mode Example (Not part of automated test) ---")
        manual_layout = [
            "WWWWW",
            "WS.GW",
            "WWWWW"
        ]
        manual_game = Game(manual_layout) # No AI depth
        print("Initial state for manual game:")
        for r_chars in manual_game.get_state_for_ai()['board']: print("".join(r_chars))
        # manual_game.handle_input('RIGHT') # Example
        # for r_chars in manual_game.get_state_for_ai()['board']: print("".join(r_chars))
        print("Manual mode example finished.")

import os # For checking CI environment variable
