import math
import random
from game import Game, PacMan, Ghost, GameBoard # Assuming these can be imported

class MinimaxAgent:
    def __init__(self, depth=2):
        self.depth = depth

    def get_possible_pacman_actions(self, game_instance_or_state_dict):
        """
        Determines possible actions for Pac-Man.
        If Pac-Man is at (r, c), possible actions are UP, DOWN, LEFT, RIGHT,
        provided they don't lead into a wall.
        """
        # This needs access to the board configuration.
        # If it's a state_dict, board is in state_dict['board']
        # If it's a game_instance, use game_instance.game_board

        pacman_pos = None
        game_board_obj = None

        if isinstance(game_instance_or_state_dict, Game):
            pacman_pos = (game_instance_or_state_dict.pacman.row, game_instance_or_state_dict.pacman.col)
            game_board_obj = game_instance_or_state_dict.game_board
        elif isinstance(game_instance_or_state_dict, dict): # game_state_for_ai
            pacman_pos = game_instance_or_state_dict['pacman_pos']
            # We need a GameBoard object or similar logic for is_wall
            # For now, let's assume the state dict's board is just characters.
            # This highlights the need for a robust way to check walls from state_dict.
            # A temporary GameBoard could be created if layout is part of state_dict,
            # or if game_state_for_ai returns a more structured board.
            # For now, this will be a simplified check.
            # Let's assume the 'board' in state_dict is the primary source of truth for walls.
            current_board_layout_chars = game_instance_or_state_dict['board']

            # Hacky way to use is_wall without a full GameBoard if only state_dict is available.
            # This is not ideal. A better approach would be to instantiate a GameBoard
            # or have a utility function.
            class TempBoard:
                def __init__(self, layout_chars):
                    self.board = layout_chars
                    self.rows = len(layout_chars)
                    self.cols = len(layout_chars[0])
                def is_wall(self, r, c):
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        return self.board[r][c] == 'W'
                    return True # Out of bounds is a wall
            game_board_obj = TempBoard(current_board_layout_chars)

        else:
            raise TypeError("Input must be a Game instance or a state dictionary.")

        r, c = pacman_pos
        actions = []
        if not game_board_obj.is_wall(r - 1, c): actions.append('UP')
        if not game_board_obj.is_wall(r + 1, c): actions.append('DOWN')
        if not game_board_obj.is_wall(r, c - 1): actions.append('LEFT')
        if not game_board_obj.is_wall(r, c + 1): actions.append('RIGHT')

        return actions if actions else ['NONE'] # Return 'NONE' if no moves possible (e.g. trapped)

    def simulate_action_and_get_next_state(self, game_instance, action, is_pacman_turn=True):
        """
        Simulates an action (Pac-Man or Ghosts) on a *copy* of the game instance
        and returns the new state dictionary.
        This is a crucial and complex part.
        """
        # Create a deep copy of the game state to simulate on.
        # This requires the Game class to have a way to be initialized from a state dict,
        # or to have a deepcopy method.
        # For now, we'll assume direct manipulation of a temporary Game object,
        # which is simpler if the Game class structure allows for it.

        # The easiest way is to have a method in Game that can create a deep copy of itself.
        # Or, reconstruct a new Game object from the current game's layout and then
        # apply the current state (pacman pos, score, lives, ghost pos, pellet states etc.)
        # to this new object.

        # Simplified approach for now:
        # Create a new game instance based on the original layout,
        # then try to set its state. This is not perfect because the original
        # layout doesn't change (e.g. eaten pellets).
        # The 'get_state_for_ai' should ideally give the *current* board layout.

        # Let's assume `game_instance.get_state_for_ai()` returns a board that reflects eaten pellets.
        # And that we can create a new Game instance from this dynamic layout.

        current_state_dict = game_instance.get_state_for_ai()

        # Create a new GameBoard from the current board state
        # The Game constructor needs to be able to take a layout like this.
        # The 'S' and 'G' markers in ai_state['board'] need to be handled.
        # The Game constructor currently expects 'S' and 'G' to initialize pacman/ghosts.
        # This is a point of friction.

        # Simplification: We will create a "pseudo" game instance or manipulate a state dict.
        # For a true simulation, the Game class should ideally support:
        # 1. game_copy = game_instance.deep_copy()
        # 2. game_copy.handle_input(action) OR game_copy.update_ghosts()
        # 3. next_state_dict = game_copy.get_state_for_ai()

        # Given the current Game class, direct simulation is tricky without modifying it.
        # Let's try to make a new Game object and manually set states.
        # This is an approximation.

        # We need the original layout to initialize Game correctly, then apply changes.
        # This is becoming complex. A better way is to make Game class more flexible.

        # --- Alternative: Manipulate a state dictionary directly ---
        # This is also complex as we'd have to re-implement game logic (collision, eating, etc.)
        # on the dictionary representation.

        # --- Compromise for this step: ---
        # Assume we have a way to get a *new* Game instance that represents the desired state
        # after an action. This is a placeholder for a more robust simulation.

        # For the purpose of this AI structure, let's assume `game_instance.handle_input(action)`
        # and `game_instance.update()` can be called, and we can then get the new state.
        # This implies we'd be working on a *copy* of the game.
        # Python's `copy.deepcopy` might work on the `Game` object if all its attributes are copyable.
        import copy
        sim_game = copy.deepcopy(game_instance)

        if is_pacman_turn:
            if action != 'NONE': # 'NONE' action means Pac-Man stays put.
                 sim_game.handle_input(action) # This also calls update() in the current Game class
            else:
                # If action is 'NONE', Pac-Man doesn't move. Ghosts still move.
                # The current handle_input calls update(). If PacMan doesn't move,
                # we might just need to call update() for ghosts and game state checks.
                # However, handle_input with a specific direction IS Pacman's turn.
                # For 'NONE', we assume Pacman does nothing, then ghosts move.
                # So, call update for ghost moves and game status.
                 sim_game.update() # Ghosts move, pellets checked (if any under pacman), game state updates
        else:
            # This is for ghost turn. Ghosts move, collisions happen.
            # The current `sim_game.update()` handles ghost moves and subsequent checks.
            # We might need a more granular update if Pacman's turn and Ghost's turn are separate in Minimax.
            # In classic Minimax, MAX makes a move, then MIN makes a move.
            # So, after Pac-Man's simulated move (handle_input), the state reflects that.
            # Then, for min_value, ghosts would move from *that* state.
            sim_game.update() # This moves ghosts and updates game state

        return sim_game.get_state_for_ai()


    def get_best_action(self, game_instance):
        """
        Initiates the Minimax search for Pac-Man.
        """
        best_action = 'NONE'
        max_eval = -math.inf
        alpha = -math.inf
        beta = math.inf

        # Initial state for Pacman's turn (MAX node)
        # The actions are from the *current actual* game state
        possible_actions = self.get_possible_pacman_actions(game_instance)
        if not possible_actions: return 'NONE' # Should be handled by get_possible_pacman_actions returning ['NONE']

        for action in possible_actions:
            # Simulate Pac-Man's move. The state *after* Pac-Man's move is what ghosts see.
            # The `simulate_action_and_get_next_state` should handle this.
            # `is_pacman_turn=True` means Pacman makes 'action', then game updates (eats, etc.)
            # The resulting state is then passed to min_value.
            next_state_dict = self.simulate_action_and_get_next_state(game_instance, action, is_pacman_turn=True)

            # Now it's ghost's turn (MIN node) from next_state_dict
            # Depth is self.depth because this is the first level of lookahead.
            # The min_value will then call max_value with depth-1.
            # Pass the initial_layout from the game_board for reconstructing the static parts of the game.
            eval_score = self.min_value(next_state_dict, self.depth, alpha, beta, game_instance.game_board.initial_layout)

            if eval_score > max_eval:
                max_eval = eval_score
                best_action = action
            alpha = max(alpha, eval_score)

        return best_action

    def max_value(self, current_game_state_dict, depth, alpha, beta, original_layout):
        """
        Represents Pac-Man's turn in Minimax.
        `current_game_state_dict` is the state *before* Pac-Man makes a move.
        """
        if depth == 0 or current_game_state_dict['game_state'] != 'PLAYING':
            return self.evaluate_state(current_game_state_dict)

        max_eval = -math.inf

        # Need a way to get possible Pac-Man actions from a state dictionary
        # This requires instantiating a temporary Game or GameBoard from the state_dict
        # For now, let's assume get_possible_pacman_actions can handle a state_dict
        possible_actions = self.get_possible_pacman_actions(current_game_state_dict)

        for action in possible_actions:
            # Simulate Pac-Man's action from current_game_state_dict
            # This is tricky. We need to "play out" the action on the state_dict.
            # This implies creating a temporary Game object from current_game_state_dict,
            # applying the action, and then getting the resulting state_dict.

            # Create a temporary Game instance from the current_game_state_dict
            # This is the most challenging part of the state simulation.
            # The Game class needs a constructor that can take a state dictionary or full layout + state.
            temp_game_from_state = self._create_temp_game_from_state(current_game_state_dict, original_layout)

            next_state_after_pacman_move = self.simulate_action_and_get_next_state(temp_game_from_state, action, is_pacman_turn=True)

            eval_score = self.min_value(next_state_after_pacman_move, depth -1, alpha, beta, original_layout)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Pruning
        return max_eval

    def min_value(self, current_game_state_dict, depth, alpha, beta, original_layout):
        """
        Represents Ghosts' turn in Minimax.
        `current_game_state_dict` is the state *after* Pac-Man has made his move.
        Now, ghosts make their move(s).
        """
        if depth == 0 or current_game_state_dict['game_state'] != 'PLAYING':
            return self.evaluate_state(current_game_state_dict)

        min_eval = math.inf

        # In this state, ghosts make their move.
        # We need to simulate the ghosts' collective move from current_game_state_dict.
        # The `simulate_action_and_get_next_state` with `is_pacman_turn=False`
        # should handle this: it should just call the equivalent of `game.update()`
        # which moves all ghosts and updates game state.

        temp_game_from_state = self._create_temp_game_from_state(current_game_state_dict, original_layout)
        next_state_after_ghost_moves = self.simulate_action_and_get_next_state(temp_game_from_state, action=None, is_pacman_turn=False)

        # After ghosts move, it's Pac-Man's turn again.
        eval_score = self.max_value(next_state_after_ghost_moves, depth, alpha, beta, original_layout) # Note: depth for max_value is current depth, it will be depth-1 internally for next call. This seems off.
                                                                                                    # Depth should be depth-1 for the next call to max_value.
                                                                                                    # The depth parameter in min_value/max_value usually means "remaining depth".
                                                                                                    # So, if min_value is called with depth D, it calls max_value with D (if ghosts move as one) or D-1 (if one ghost moves then next).
                                                                                                    # Let's assume: Max(depth D) calls Min(depth D). Min(depth D) calls Max(depth D-1).

        eval_score = self.max_value(next_state_after_ghost_moves, depth -1, alpha, beta, original_layout)


        min_eval = min(min_eval, eval_score)
        beta = min(beta, eval_score)
        if beta <= alpha:
            break  # Pruning

        # If multiple ghost moves were to be considered independently (more complex):
        # For each ghost's possible move (or simplified: for one combined set of ghost moves):
        #   next_state_after_this_ghost_config = ...
        #   eval = self.max_value(next_state_after_this_ghost_config, depth - 1, alpha, beta)
        #   min_eval = min(min_eval, eval)
        #   beta = min(beta, eval)
        #   if beta <= alpha: break
        return min_eval

    def _create_temp_game_from_state(self, game_state_dict, original_layout_template):
        """
        Helper to create a temporary Game instance from a game_state dictionary.
        This is a critical and potentially complex part.
        It needs to accurately reconstruct the game state.
        `original_layout_template` is the initial static layout (walls, original pellet locations).
        `game_state_dict['board_grid']` (or `game_state_dict['board']`) reflects the *current* dynamic board.
        `original_layout_grid` is the static wall layout.
        """
        # Step 1: Initialize temp_game with the original static layout.
        # This sets up walls, and initial (but soon to be overridden) Pac-Man/Ghost/Pellet placements.
        # No Pygame screen/font needed for simulation. No nested AI.
        temp_game = Game(layout=original_layout_grid, ai_agent_depth=None, screen=None, font=None)

        # Step 2: Override game state from game_state_dict.

        # Board (Pellets/Power-ups):
        # The game_state_dict['board'] (or 'board_grid') contains the current pellet/power-up configuration.
        # The GameBoard of temp_game was initialized with original_layout_grid.
        # We need to update its 'grid' attribute to reflect the current state of pellets.
        current_grid_from_state = game_state_dict.get('board_grid') or game_state_dict.get('board')
        if current_grid_from_state:
            temp_game.game_board.grid = [row[:] for row in current_grid_from_state]
        else:
            # This case should ideally not happen if get_state_for_ai is providing the grid.
            # If it does, the temp_game.game_board.grid will remain as per original_layout_grid,
            # which might be okay if pellets are not changing or not crucial for this sim depth.
            # However, it's better to ensure 'board_grid' or 'board' is always in game_state_dict.
            pass

        # Pac-Man state:
        pacman_info = game_state_dict.get('pacman', {}) # Use .get for safety
        temp_game.pacman.row = pacman_info.get('row', temp_game.pacman.row)
        temp_game.pacman.col = pacman_info.get('col', temp_game.pacman.col)
        temp_game.pacman.direction = pacman_info.get('direction', temp_game.pacman.direction)
        temp_game.pacman.lives = pacman_info.get('lives', temp_game.pacman.lives)
        temp_game.pacman.powered_up = pacman_info.get('powered_up', temp_game.pacman.powered_up)

        temp_game.pacman.score = game_state_dict.get('score', temp_game.pacman.score) # Score is on PacMan in Game, but top-level in state dict
        temp_game.power_up_timer = game_state_dict.get('power_up_timer', temp_game.power_up_timer)

        # Ghosts state:
        ghost_info_list = game_state_dict.get('ghosts', [])
        # The number of ghosts in temp_game (from original_layout_grid) should match ghost_info_list.
        # If not, this indicates a discrepancy or a more dynamic ghost model not yet supported.
        for i in range(min(len(temp_game.ghosts), len(ghost_info_list))):
            ghost_state_info = ghost_info_list[i]
            temp_game.ghosts[i].row = ghost_state_info.get('row', temp_game.ghosts[i].row)
            temp_game.ghosts[i].col = ghost_state_info.get('col', temp_game.ghosts[i].col)
            temp_game.ghosts[i].mode = ghost_state_info.get('mode', temp_game.ghosts[i].mode)

        # Game-level state variables:
        temp_game.game_state = game_state_dict.get('game_state', temp_game.game_state)
        # temp_game.current_turn could be updated if needed: game_state_dict.get('current_turn', temp_game.current_turn)

        # Note: num_pellets_left is not directly set on temp_game, but its GameBoard.grid is updated.
        # If evaluate_state needs num_pellets_left directly from game_state_dict, it can use it.
        # Or, temp_game.game_board.get_pellet_count() could be called if evaluate_state has access to temp_game.

        return temp_game


    def evaluate_state(self, game_state): # game_state is game_state_dict
        """
        Evaluates the utility of a game state for Pac-Man.
        Higher scores are better for Pac-Man.
        """
        if game_state['game_state'] == 'WIN':
            return 10000 + game_state['score'] # Use score from state_dict
        if game_state['game_state'] == 'GAME_OVER':
            # Use lives from pacman sub-dictionary if available, else fallback
            pac_lives = game_state.get('pacman', {}).get('lives', 0)
            if 'pacman_lives' in game_state : # check old key for safety
                pac_lives = game_state['pacman_lives']

            return -10000 - (3 - pac_lives) * 1000

        current_score = game_state['score']

        # Pellet heuristic
        # num_pellets is now directly in game_state
        num_pellets = game_state.get('num_pellets_left', 0)
        min_dist_pellet = float('inf')

        # Use pacman_pos from state_dict for pac_r, pac_c
        pac_r, pac_c = game_state.get('pacman', {}).get('row'), game_state.get('pacman', {}).get('col')
        if 'pacman_pos' in game_state: # fallback for old key
             pac_r, pac_c = game_state['pacman_pos']


        if pac_r is not None and pac_c is not None:
            # Iterate over the board from game_state to find pellets
            # game_state['board'] or game_state['board_grid'] should be used
            current_grid = game_state.get('board_grid') or game_state.get('board')
            if current_grid:
                for r_idx, row in enumerate(current_grid):
                    for c_idx, cell in enumerate(row):
                        if cell == '.':
                            # num_pellets count is already directly from game_state_dict['num_pellets_left']
                            dist = abs(pac_r - r_idx) + abs(pac_c - c_idx)
                            if dist < min_dist_pellet:
                                min_dist_pellet = dist

        current_score -= num_pellets * 10
        if num_pellets > 0 and min_dist_pellet != float('inf'):
             current_score -= min_dist_pellet * 1.5

        # Power-up heuristic
        pac_powered_up = game_state.get('pacman', {}).get('powered_up', False)
        if 'pacman_powered_up' in game_state: # fallback for old key
            pac_powered_up = game_state['pacman_powered_up']

        if pac_powered_up:
            current_score += 200
            current_score += game_state.get('power_up_timer', 0) * 5

        # Ghost heuristics
        min_dist_active_ghost = float('inf')
        min_dist_frightened_ghost = float('inf')

        ghost_states_list = game_state.get('ghosts', [])
        # Fallback for old structure if 'ghosts' list is not present
        if not ghost_states_list and 'ghosts_pos' in game_state and 'ghosts_modes' in game_state:
            for i in range(len(game_state['ghosts_pos'])):
                ghost_states_list.append({
                    'row': game_state['ghosts_pos'][i][0],
                    'col': game_state['ghosts_pos'][i][1],
                    'mode': game_state['ghosts_modes'][i]
                })

        if pac_r is not None and pac_c is not None:
            for g_state in ghost_states_list:
                g_r, g_c = g_state['row'], g_state['col']
                dist = abs(pac_r - g_r) + abs(pac_c - g_c)
                if g_state['mode'] == 'FRIGHTENED':
                    if dist < min_dist_frightened_ghost:
                        min_dist_frightened_ghost = dist
                else: # CHASE or SCATTER
                    if dist < min_dist_active_ghost:
                        min_dist_active_ghost = dist

        if min_dist_active_ghost != float('inf'):
            if min_dist_active_ghost <= 1:
                current_score -= 500
            elif min_dist_active_ghost == 2:
                current_score -= 200
            elif min_dist_active_ghost < 5:
                current_score -= (100 / (min_dist_active_ghost + 0.01))

        if pac_powered_up and min_dist_frightened_ghost != float('inf'):
            current_score += 100
            current_score -= min_dist_frightened_ghost * 10

        # Lives bonus
        pac_lives_for_score = game_state.get('pacman', {}).get('lives', 0)
        if 'pacman_lives' in game_state: # fallback for old key
            pac_lives_for_score = game_state['pacman_lives']
        current_score += pac_lives_for_score * 100

        return current_score

        return score

if __name__ == '__main__':
    # This section is for basic testing of the AI structure,
    # but requires a functional Game class and its methods.
    # Example:
    # layout = [
    #     "WWWWWWWWWW",
    #     "W S  .PW",
    #     "W WW W.W W",
    #     "W  G . . W",
    #     "WWWWWWWWWW"
    # ]
    # game = Game(layout)
    # agent = MinimaxAgent(depth=2)

    # print("Initial game state for AI:")
    # initial_ai_state = game.get_state_for_ai()
    # for r in initial_ai_state['board']: print("".join(r))
    # print(f"Score: {initial_ai_state['pacman_score']}")
    # print(f"Eval: {agent.evaluate_state(initial_ai_state)}")

    # # Test get_possible_pacman_actions
    # possible_moves = agent.get_possible_pacman_actions(game)
    # print(f"Possible initial moves: {possible_moves}") # From (1,1) -> DOWN, RIGHT

    # # Test simulation (very basic, needs robust Game copy/state setting)
    # if 'RIGHT' in possible_moves:
    #     print("\nSimulating move RIGHT...")
    #     # Need a deepcopy mechanism for game, or state-based simulation
    #     import copy
    #     sim_game_for_right_move = agent._create_temp_game_from_state(game.get_state_for_ai(), game.game_board.board) # Pass current board as "original_layout" for now
    #     # Apply the move
    #     sim_game_for_right_move.handle_input('RIGHT')
    #     # Get the state
    #     state_after_right = sim_game_for_right_move.get_state_for_ai()

    #     print("State after simulated RIGHT move:")
    #     for r in state_after_right['board']: print("".join(r))
    #     print(f"Score: {state_after_right['pacman_score']}")
    #     print(f"Eval: {agent.evaluate_state(state_after_right)}")


    # This would be the main call:
    # best_move = agent.get_best_action(game)
    # print(f"Minimax suggested best action: {best_move}")
    pass
