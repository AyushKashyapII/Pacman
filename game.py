class GameBoard:
    def __init__(self, layout: list[str]):
        self.initial_layout = [list(row) for row in layout] # Store the original layout
        self.grid = [list(row) for row in layout] # Current state of the board
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])

    def is_wall(self, row: int, col: int) -> bool:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] == 'W'
        return True  # Treat out-of-bounds as walls

    def get_cell(self, row: int, col: int) -> str | None:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def remove_item(self, row: int, col: int) -> str | None:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            item = self.grid[row][col]
            if item == '.' or item == 'P':
                self.grid[row][col] = ' '  # Mark as empty
                return item
        return None

    def get_pellet_count(self) -> int:
        count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == '.':
                    count += 1
        return count


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

import pygame # Import Pygame
from ai import MinimaxAgent # Import the AI Agent
import time # For potential sleep in the game loop
import os # For checking CI environment variable


# Pygame constants
SCREEN_WIDTH = 600  # Default, can be overridden by layout
SCREEN_HEIGHT = 680 # Default, can be overridden by layout + UI space
CELL_SIZE = 20      # Pixel size of each cell in the grid
GRID_OFFSET_Y = 80  # Increased offset for score, lives, and game state text
GAME_FPS = 10       # Frame rate for the game

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)   # Pac-Man
BLUE = (0, 0, 255)       # Walls
WHITE = (255, 255, 255)  # Pellets, UI Text
RED = (255, 0, 0)        # Ghost 1 (Blinky)
PINK = (255, 184, 222)   # Ghost 2 (Pinky)
CYAN = (0, 255, 255)     # Ghost 3 (Inky)
ORANGE = (255, 184, 82)  # Ghost 4 (Clyde)
FRIGHTENED_GHOST_BLUE = (100, 100, 255)
PELLET_COLOR = WHITE
POWER_UP_COLOR = (0, 255, 0) # Green for power-ups

# Drawing element sizes (radii for circles, or use CELL_SIZE for squares)
PACMAN_RADIUS = int(CELL_SIZE * 0.4)
GHOST_RADIUS = int(CELL_SIZE * 0.4)
PELLET_RADIUS = int(CELL_SIZE * 0.1)
POWER_UP_RADIUS = int(CELL_SIZE * 0.3)

class Game:
    def __init__(self, layout, ai_agent_depth=None, screen=None, font=None): # Pass screen and font for Pygame
        self.game_board = GameBoard(layout) # GameBoard now stores initial_layout and current grid
        self.ai_agent = None
        if ai_agent_depth is not None:
            self.ai_agent = MinimaxAgent(depth=ai_agent_depth)

        self.pacman_start_pos = None
        self.ghost_start_pos_initial = [] # Store initial positions for reset

        # Find PacMan and Ghost start positions from the *initial* layout
        # The GameBoard's grid will be modified (S and G removed)
        for r_idx, row_list in enumerate(self.game_board.initial_layout):
            for c_idx, cell in enumerate(row_list):
                if cell == 'S':
                    if self.pacman_start_pos is None: # Take the first 'S'
                        self.pacman_start_pos = (r_idx, c_idx)
                elif cell == 'G':
                    self.ghost_start_pos_initial.append({'pos': (r_idx, c_idx), 'original_char': 'G'})

        if self.pacman_start_pos is None:
            raise ValueError("Pac-Man start position 'S' not found in layout.")

        self.pacman = PacMan(self.pacman_start_pos[0], self.pacman_start_pos[1])

        self.ghosts = []
        for i, g_info in enumerate(self.ghost_start_pos_initial):
            self.ghosts.append(Ghost(g_info['pos'][0], g_info['pos'][1]))
            # Remove 'G' from current grid after ghost is created
            if self.game_board.get_cell(g_info['pos'][0], g_info['pos'][1]) == 'G':
                 self.game_board.grid[g_info['pos'][0]][g_info['pos'][1]] = ' '


        # Remove 'S' from current grid after Pac-Man is created
        if self.game_board.get_cell(self.pacman.row, self.pacman.col) == 'S':
            self.game_board.grid[self.pacman.row][self.pacman.col] = ' '


        self.game_state = 'PLAYING' # PLAYING, GAME_OVER, WIN
        self.power_up_timer = 0 # Timer for Pac-Man's power-up
        self.current_turn = 0 # To keep track of game turns for AI or display

        # Pygame specific attributes
        self.screen = screen
        self.font = font
        self.ghost_colors = [RED, PINK, CYAN, ORANGE]
        self.manual_control = False # Default to AI control


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
                    # Reset ghost to its individual initial start position
                    ghost_initial_info = self.ghost_start_pos_initial[self.ghosts.index(ghost) % len(self.ghost_start_pos_initial)]
                    ghost.row, ghost.col = ghost_initial_info['pos']
                    ghost.mode = 'CHASE' # Or SCATTER
                else:
                    # Ghost catches Pac-Man
                    self.pacman.lives -= 1
                    if self.pacman.lives <= 0:
                        self.game_state = 'GAME_OVER'
                    else:
                        # Reset Pac-Man to his start position
                        self.pacman.row, self.pacman.col = self.pacman_start_pos
                        # Reset all ghosts to their initial positions and modes
                        for i, g in enumerate(self.ghosts):
                            g_initial_info = self.ghost_start_pos_initial[i % len(self.ghost_start_pos_initial)]
                            g.row, g.col = g_initial_info['pos']
                            g.mode = 'SCATTER' # Default mode after Pac-Man caught
                    break # Stop checking other ghosts if Pac-Man is caught

        # 6. Check for win condition (all pellets eaten)
        if self.game_board.get_pellet_count() == 0:
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

    # --- Pygame Drawing Methods ---
    def _draw_board(self, surface):
        for r_idx, row_list in enumerate(self.game_board.grid): # Use .grid for current state
            for c_idx, cell_type in enumerate(row_list):
                rect = pygame.Rect(c_idx * CELL_SIZE,
                                   r_idx * CELL_SIZE + GRID_OFFSET_Y,
                                   CELL_SIZE, CELL_SIZE)
                if cell_type == 'W':
                    pygame.draw.rect(surface, BLUE, rect)
                elif cell_type == '.':
                    center_x = int(c_idx * CELL_SIZE + CELL_SIZE / 2)
                    center_y = int(r_idx * CELL_SIZE + CELL_SIZE / 2 + GRID_OFFSET_Y)
                    pygame.draw.circle(surface, PELLET_COLOR, (center_x, center_y), PELLET_RADIUS)
                elif cell_type == 'P':
                    center_x = int(c_idx * CELL_SIZE + CELL_SIZE / 2)
                    center_y = int(r_idx * CELL_SIZE + CELL_SIZE / 2 + GRID_OFFSET_Y)
                    pygame.draw.circle(surface, POWER_UP_COLOR, (center_x, center_y), POWER_UP_RADIUS)

    def _draw_pacman(self, surface):
        center_x = int(self.pacman.col * CELL_SIZE + CELL_SIZE / 2)
        center_x = int(self.pacman.col * CELL_SIZE + CELL_SIZE / 2)
        center_y = int(self.pacman.row * CELL_SIZE + CELL_SIZE / 2 + GRID_OFFSET_Y)

        # Draw Pac-Man body
        pygame.draw.circle(surface, YELLOW, (center_x, center_y), PACMAN_RADIUS)

        # Draw mouth
        mouth_angle = 0.4 # radians, approx 23 degrees opening angle on each side
        # Determine points for the mouth triangle based on direction
        # Point 1 is always the center of Pac-Man
        p1 = (center_x, center_y)

        # Calculate points for an open wedge
        if self.pacman.direction == 'RIGHT':
            angle_offset = 0 # Mouth points right
        elif self.pacman.direction == 'LEFT':
            angle_offset = 3.14159 # Mouth points left (180 degrees)
        elif self.pacman.direction == 'UP':
            angle_offset = -3.14159 / 2 # Mouth points up (-90 degrees)
        elif self.pacman.direction == 'DOWN':
            angle_offset = 3.14159 / 2 # Mouth points down (90 degrees)
        else: # Default to right if direction is somehow None or invalid
             angle_offset = 0

        # Points for the arc of the mouth
        # Using polygon for mouth instead of arc for simplicity here
        # For a wedge shape (triangle)
        # p2 = (center_x + PACMAN_RADIUS * math.cos(angle_offset - mouth_angle),
        #       center_y + PACMAN_RADIUS * math.sin(angle_offset - mouth_angle))
        # p3 = (center_x + PACMAN_RADIUS * math.cos(angle_offset + mouth_angle),
        #       center_y + PACMAN_RADIUS * math.sin(angle_offset + mouth_angle))
        # pygame.draw.polygon(surface, BLACK, [p1, p2, p3])

        # Simpler: draw a black filled arc (pie slice) for the mouth
        # Start and stop angles for the arc
        # Angles are in radians. 0 is to the right. pygame.draw.arc needs radians.
        # Let's make mouth opening about 70 degrees (approx 1.2 radians)
        mouth_open_angle_rad = 1.2

        if self.pacman.direction == 'RIGHT':
            start_angle = angle_offset - mouth_open_angle_rad / 2
            end_angle = angle_offset + mouth_open_angle_rad / 2
        elif self.pacman.direction == 'LEFT':
            start_angle = angle_offset - mouth_open_angle_rad / 2
            end_angle = angle_offset + mouth_open_angle_rad / 2
        elif self.pacman.direction == 'UP':
            start_angle = angle_offset - mouth_open_angle_rad / 2
            end_angle = angle_offset + mouth_open_angle_rad / 2
        elif self.pacman.direction == 'DOWN':
            start_angle = angle_offset - mouth_open_angle_rad / 2
            end_angle = angle_offset + mouth_open_angle_rad / 2
        else: # Default if direction is weird
            start_angle = -mouth_open_angle_rad / 2
            end_angle = mouth_open_angle_rad / 2

        # Pygame's arc drawing is a bit tricky for a filled wedge.
        # A common way is to draw a circle and then a black polygon.
        # Let's use a simpler triangle approach for the mouth:
        # Points are: center, and two points on the circumference.
        # For simplicity, let's use a fixed orientation mouth for now, or skip if too complex.
        # Given the subtask constraints, a simpler visual cue or just the circle is acceptable.
        # Let's try drawing a black triangle for the mouth.
        # The triangle points need to be calculated carefully based on direction.
        # Example for 'RIGHT' direction:
        # p1 = (center_x, center_y)
        # p2 = (center_x + PACMAN_RADIUS, center_y - PACMAN_RADIUS // 2)
        # p3 = (center_x + PACMAN_RADIUS, center_y + PACMAN_RADIUS // 2)
        # pygame.draw.polygon(surface, BLACK, [p1,p2,p3])
        # This would be a wedge pointing right.
        # For now, let's use a simpler method: a black circle offset to look like a mouth.
        # This is very basic and not direction-dependent without more math.
        # A small black circle offset in the direction of movement.
        mouth_offset = int(PACMAN_RADIUS * 0.5)
        mouth_radius = int(PACMAN_RADIUS * 0.4)
        mx, my = center_x, center_y
        if self.pacman.direction == 'RIGHT': mx += mouth_offset
        elif self.pacman.direction == 'LEFT': mx -= mouth_offset
        elif self.pacman.direction == 'UP': my -= mouth_offset
        elif self.pacman.direction == 'DOWN': my += mouth_offset
        # pygame.draw.circle(surface, BLACK, (mx, my), mouth_radius)
        # This creates a dot, not a mouth.
        # Back to drawing an arc for Pacman himself if we want a mouth.
        # pygame.draw.arc(surface, YELLOW, rect, start_angle, stop_angle, width)
        # For a filled Pacman with mouth: draw a yellow pie slice.
        # Angles need to be in radians. 0 rad is to the right.
        # Let Pac-Man be a pie shape (circle with a wedge missing for mouth).
        # The mouth should be in the direction Pac-Man is moving.
        # Angle of the center of the mouth opening:
        if self.pacman.direction == 'RIGHT': pac_angle = 0
        elif self.pacman.direction == 'LEFT': pac_angle = 3.14159 # PI
        elif self.pacman.direction == 'UP': pac_angle = 3.14159 / 2 # PI/2
        elif self.pacman.direction == 'DOWN': pac_angle = -3.14159 / 2 # -PI/2
        else: pac_angle = 0

        mouth_span_angle = 0.7 # Radians, e.g. about 40 degrees
        start_angle = pac_angle + mouth_span_angle
        end_angle = pac_angle - mouth_span_angle

        # Pygame's arc has start_angle counter-clockwise from positive x-axis,
        # and end_angle also counter-clockwise.
        # To make it a wedge, we need to ensure start < end, or draw full circle then black wedge.
        # For simplicity, drawing Pacman as a full circle, then overlaying a black triangle for mouth.
        # This is easier to manage with directions.

        # Points for mouth triangle
        mouth_points = []
        offset_from_center = PACMAN_RADIUS
        if self.pacman.direction == 'RIGHT':
            mouth_points = [ (center_x, center_y),
                             (center_x + offset_from_center, center_y - PACMAN_RADIUS*0.7),
                             (center_x + offset_from_center, center_y + PACMAN_RADIUS*0.7) ]
        elif self.pacman.direction == 'LEFT':
            mouth_points = [ (center_x, center_y),
                             (center_x - offset_from_center, center_y - PACMAN_RADIUS*0.7),
                             (center_x - offset_from_center, center_y + PACMAN_RADIUS*0.7) ]
        elif self.pacman.direction == 'UP':
            mouth_points = [ (center_x, center_y),
                             (center_x - PACMAN_RADIUS*0.7, center_y - offset_from_center),
                             (center_x + PACMAN_RADIUS*0.7, center_y - offset_from_center) ]
        elif self.pacman.direction == 'DOWN':
            mouth_points = [ (center_x, center_y),
                             (center_x - PACMAN_RADIUS*0.7, center_y + offset_from_center),
                             (center_x + PACMAN_RADIUS*0.7, center_y + offset_from_center) ]

        if mouth_points:
             pygame.draw.polygon(surface, BLACK, mouth_points)


        if self.pacman.powered_up: # Maybe draw a power aura or change shape slightly
            pygame.draw.circle(surface, WHITE, (center_x, center_y), PACMAN_RADIUS + 2, 1)


    def _draw_ghosts(self, surface):
        eye_radius = int(GHOST_RADIUS * 0.2)
        eye_offset_x = int(GHOST_RADIUS * 0.3)
        eye_offset_y = int(GHOST_RADIUS * 0.25)

        for i, ghost in enumerate(self.ghosts):
            center_x = int(ghost.col * CELL_SIZE + CELL_SIZE / 2)
            center_y = int(ghost.row * CELL_SIZE + CELL_SIZE / 2 + GRID_OFFSET_Y)

            ghost_body_color = self.ghost_colors[i % len(self.ghost_colors)]
            if ghost.mode == 'FRIGHTENED':
                ghost_body_color = FRIGHTENED_GHOST_BLUE

            # Draw ghost body
            pygame.draw.circle(surface, ghost_body_color, (center_x, center_y), GHOST_RADIUS)

            # Draw eyes (simple static eyes for now)
            # Left eye
            pygame.draw.circle(surface, WHITE, (center_x - eye_offset_x, center_y - eye_offset_y), eye_radius)
            pygame.draw.circle(surface, BLACK, (center_x - eye_offset_x, center_y - eye_offset_y), int(eye_radius * 0.5)) # Pupil
            # Right eye
            pygame.draw.circle(surface, WHITE, (center_x + eye_offset_x, center_y - eye_offset_y), eye_radius)
            pygame.draw.circle(surface, BLACK, (center_x + eye_offset_x, center_y - eye_offset_y), int(eye_radius * 0.5)) # Pupil


    def _draw_ui(self, surface):
        if not self.font: return # No font, no UI

        # Regular font for most UI text
        score_text_render = self.font.render(f"Score: {self.pacman.score}", True, WHITE)
        lives_text_render = self.font.render(f"Lives: {self.pacman.lives}", True, WHITE)
        state_text_render = self.font.render(f"State: {self.game_state}", True, WHITE)
        turn_text_render = self.font.render(f"Turn: {self.current_turn}", True, WHITE)
        control_mode_text = "Manual" if self.manual_control else "AI"
        control_text_render = self.font.render(f"Control: {control_mode_text} (M to toggle)", True, WHITE)

        surface.blit(score_text_render, (10, 10))
        surface.blit(lives_text_render, (SCREEN_WIDTH - 120, 10))
        surface.blit(state_text_render, (SCREEN_WIDTH // 2 - 70, 10))
        surface.blit(turn_text_render, (10, 35))
        surface.blit(control_text_render, (SCREEN_WIDTH //2 - 100, 35))

        if self.pacman.powered_up:
            power_timer_text = self.font.render(f"Power: {self.power_up_timer}", True, POWER_UP_COLOR)
            surface.blit(power_timer_text, (SCREEN_WIDTH - 120, 35))

        # Game Over / Win Message
        if self.game_state == 'GAME_OVER' or self.game_state == 'WIN' or self.game_state == 'MAX_TURNS':
            message = ""
            if self.game_state == 'GAME_OVER': message = "GAME OVER"
            elif self.game_state == 'WIN': message = "YOU WIN!"
            elif self.game_state == 'MAX_TURNS': message = "MAX TURNS REACHED"

            if message:
                big_font = pygame.font.Font(None, 60) # Larger font for these messages
                message_render = big_font.render(message, True, RED if self.game_state == 'GAME_OVER' else GREEN)
                message_rect = message_render.get_rect(center=(self.screen.get_width() / 2,
                                                               self.screen.get_height() / 2 + GRID_OFFSET_Y / 2)) # Centered on game area

                # Optional: semi-transparent overlay
                overlay = pygame.Surface((message_rect.width + 20, message_rect.height + 20), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180)) # Black with alpha
                surface.blit(overlay, (message_rect.x - 10, message_rect.y - 10))
                surface.blit(message_render, message_rect)

        # Instructions Text
        small_font = pygame.font.Font(None, 24)
        instructions_text = "Arrow Keys: Move | M: Toggle AI/Manual | Q: Quit (in window)"
        instructions_render = small_font.render(instructions_text, True, WHITE)
        # Position at bottom center of the screen
        instr_rect = instructions_render.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() - 15))
        surface.blit(instructions_render, instr_rect)


    def draw(self, surface):
        surface.fill(BLACK) # Clear screen first
        self._draw_board(surface)
        self._draw_pacman(surface)
        self._draw_ghosts(surface)
        self._draw_ui(surface)


    def is_game_over(self):
        return self.game_state == 'GAME_OVER' or self.game_state == 'WIN'

    def get_state_for_ai(self):
        # Create a representation of the board that AI can use (e.g. with 'S' and 'G' markers)
        # For simulation, AI needs the *current* dynamic grid, not the initial one.
        sim_board_state = [row[:] for row in self.game_board.grid]

        # It's often better for the AI to get Pacman and Ghost objects or their dicts directly,
        # rather than parsing them from 'S' and 'G' markers on a board copy.
        # However, the current AI's _create_temp_game_from_state places S and G back.
        # Let's ensure the board sent to AI for its own simulation creation is clean of S/G
        # if _create_temp_game_from_state is going to place them.
        # The current version of _create_temp_game_from_state takes game_state_dict['board']
        # and places S and G markers itself. So, sim_board_state should be the raw grid.

        pacman_state = {
            'row': self.pacman.row,
            'col': self.pacman.col,
            'direction': self.pacman.direction, # Added direction
            'lives': self.pacman.lives,
            'powered_up': self.pacman.powered_up,
        }
        ghost_states = []
        for g in self.ghosts:
            ghost_states.append({
                'row': g.row,
                'col': g.col,
                'mode': g.mode
            })

        return {
            "board_grid": sim_board_state, # Current state of pellets, empty spaces, walls
            "pacman": pacman_state,
            "ghosts": ghost_states,
            "score": self.pacman.score,
            "power_up_timer": self.power_up_timer,
            "game_state": self.game_state, # PLAYING, GAME_OVER, WIN
            "num_pellets_left": self.game_board.get_pellet_count() # Added pellet count
            # Note: The AI's `_create_temp_game_from_state` uses 'board' for the grid.
            # Let's align keys or make AI adapter. For now, I'll add 'board' as a duplicate of 'board_grid'
            # for compatibility with current AI.
            "board": sim_board_state,
             "pacman_pos": (self.pacman.row, self.pacman.col), # convenience for AI
             "ghosts_pos": [(g['row'], g['col']) for g in ghost_states], # convenience for AI
             "ghosts_modes": [g['mode'] for g in ghost_states] # convenience for AI
        }


# Example Layout:
# WWWWWWWWWW
# W S  . P W
# W WWW.WW W
# W G . .  W
# W WWWWWWWW
# S = Pac-Man, G = Ghost, W = Wall, . = Pellet, P = Power-up

if __name__ == '__main__':
    pygame.init()
    pygame.font.init() # Explicitly initialize font module

    default_font = pygame.font.Font(None, 30) # Font for UI elements

    # Use the first layout to determine preferred screen size
    # This makes screen size dynamic to the loaded layout.
    layouts = {
        "Original": [
            "WWWWWWWWWW", "W S P. .GW", "W WWW.WW W", "W  . . . W",
            "W WWWWWWWW", "W G    P.W", "WWWWWWWWWW"
        ],
        "Open Field": [
            "WWWWWWWWWW", "W S  G   W", "W .  . . W", "W  .P. . W",
            "W .  . . W", "W   G  S W", "WWWWWWWWWW"
        ],
        "Corridors": [
            "WWWWWWWWWW", "WS.P.G.W.W", "W W W WW W", "W.W.W.G.PW",
            "W W W WW W", "W. . .S. .W", "WWWWWWWWWW"
        ],
        "Simple Chase": ["WWWWWW", "WS G.W", "W.P .W", "WWWWWW"]
    }

    ai_depth_to_test = 2
    max_turns_per_game = 40 # Reduced for automated test summary

    for layout_name, layout_config in layouts.items():
        print(f"\n\n--- Initializing Test for Layout: {layout_name} ---")

        game_rows = len(layout_config)
        game_cols = len(layout_config[0])
        screen_width_calculated = game_cols * CELL_SIZE
        screen_height_calculated = game_rows * CELL_SIZE + GRID_OFFSET_Y

        screen = pygame.display.set_mode((screen_width_calculated, screen_height_calculated))
        pygame.display.set_caption(f"Pac-Man AI - {layout_name}")

        game = Game(layout_config, ai_agent_depth=ai_depth_to_test, screen=screen, font=default_font)

        running_this_layout = True
        clock = pygame.time.Clock()

        print(f"Starting Pygame for layout: {layout_name}")
        print(f"Screen Width: {screen_width_calculated}, Screen Height: {screen_height_calculated}")
        print(f"Max turns for this layout: {max_turns_per_game}")

        # --- Automated Test Run Loop ---
        while running_this_layout:
            # Pygame event handling (minimal for automated test, mainly for QUIT and manual toggle)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_this_layout = False
                    # If one game window is quit, we might want to stop all tests.
                    # For now, it will just stop the current layout test.
                    # To stop all, a global 'all_running' flag would be needed.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m: # Still allow manual toggle for quick user intervention if desired
                        game.manual_control = not game.manual_control
                        print(f"Control mode toggled to: {'Manual' if game.manual_control else 'AI'}")

            # --- Game Logic Update (AI plays by default) ---
            if not game.manual_control and not game.is_game_over() and game.ai_agent:
                if game.current_turn < max_turns_per_game:
                    game.play_ai_turn()
                else: # Max turns reached for AI
                    if game.game_state == 'PLAYING':
                        print(f"Max turns ({max_turns_per_game}) reached for AI on layout {layout_name}.")
                        game.game_state = "MAX_TURNS"
                    running_this_layout = False # End current layout test
            elif game.is_game_over():
                running_this_layout = False # End current layout test if game over

            # --- Drawing ---
            if game.screen: # Only draw if screen is available
                 game.draw(screen)
                 pygame.display.flip()

            clock.tick(GAME_FPS) # Control game speed. For very fast non-visual test, this could be higher.

            if not running_this_layout: # Check if loop should terminate
                print(f"--- Finished testing layout: {layout_name} ---")
                print(f"Final State: {game.game_state}, Score: {game.pacman.score}, Lives: {game.pacman.lives}, Turns: {game.current_turn}")


        # --- Simulated Manual Control Test for "Simple Chase" layout ---
        if layout_name == "Simple Chase":
            print("\n--- Simulating Manual Control on 'Simple Chase' ---")
            # Re-initialize the game for a clean manual test starting state
            game = Game(layouts["Simple Chase"], ai_agent_depth=None, screen=screen, font=default_font) # No AI for this part
            game.manual_control = True # Set to manual
            print("Initial state for manual test:")
            if game.screen: game.draw(game.screen); pygame.display.flip()
            time.sleep(0.1) # Allow redraw

            manual_moves = ['RIGHT', 'RIGHT', 'DOWN'] # Example moves
            for move_idx, move_dir in enumerate(manual_moves):
                if not game.is_game_over():
                    print(f"Manual Test: Simulating move {move_idx + 1}: {move_dir}")
                    game.handle_input(move_dir)
                    if game.screen: game.draw(game.screen); pygame.display.flip()
                    print(f"  Pacman at: ({game.pacman.row}, {game.pacman.col}), Score: {game.pacman.score}, Lives: {game.pacman.lives}")
                    time.sleep(0.1) # Allow redraw and observation
                else:
                    print(f"Manual Test: Game ended early during move {move_idx + 1}.")
                    break
            print(f"Manual Test on 'Simple Chase' complete. Final Score: {game.pacman.score}, Lives: {game.pacman.lives}")
            # This game instance for manual test is now done. The loop will proceed to the next layout.

    print("\n\n--- All Layout Tests Concluded ---")
    pygame.quit()
