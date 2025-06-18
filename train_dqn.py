import pygame
from game import Game
from dqn import DQNAgent, preprocess_state, get_reward
from board import boards
import numpy as np

def convert_board_format(board_data):
    """
    Convert the board.py format to the game format
    board.py uses: 0=empty, 1=dot, 2=big dot, 3=vertical line, 4=horizontal line, etc.
    game.py uses: ' '=empty, '.'=pellet, 'P'=power pellet, 'W'=wall, 'S'=Pac-Man start, 'G'=Ghost start
    """
    rows = len(board_data)
    cols = len(board_data[0])
    converted_board = []
    
    # Define Pac-Man and Ghost starting positions (classic Pac-Man positions)
    pacman_start = (23, 13)  # Bottom center
    ghost_starts = [(11, 13), (11, 14), (11, 15), (11, 16)]  # Ghost pen
    
    for row in range(rows):
        new_row = []
        for col in range(cols):
            cell = board_data[row][col]
            
            if (row, col) == pacman_start:
                new_row.append('S')  # Pac-Man start
            elif (row, col) in ghost_starts:
                new_row.append('G')  # Ghost start
            elif cell == 0:
                new_row.append(' ')  # Empty space
            elif cell == 1:
                new_row.append('.')  # Regular pellet
            elif cell == 2:
                new_row.append('P')  # Power pellet
            elif cell in [3, 4, 5, 6, 7, 8, 9]:  # All wall types
                new_row.append('W')  # Wall
            else:
                new_row.append(' ')  # Default to empty
                
        converted_board.append(''.join(new_row))
    
    return converted_board

def train_dqn():
    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    default_font = pygame.font.Font(None, 30)
    
    # Use the board from board.py
    board_data = boards  # boards is already the 2D board data
    layout = convert_board_format(board_data)
    
    # Calculate screen size
    game_rows = len(layout)
    game_cols = len(layout[0])
    screen_width = game_cols * 20  # CELL_SIZE
    screen_height = game_rows * 20 + 80  # GRID_OFFSET_Y
    
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pac-Man DQN Training")
    
    # Initialize DQN agent
    # Calculate state size based on the layout
    board_size = game_rows * game_cols
    pacman_features = 2  # normalized x, y
    ghost_features = 2 * 4  # 4 ghosts, 2 features each (x, y)
    ghost_mode_features = 3 * 4  # 4 ghosts, 3 mode features each
    state_size = board_size + pacman_features + ghost_features + ghost_mode_features
    action_size = 4  # UP, DOWN, LEFT, RIGHT
    
    agent = DQNAgent(state_size, action_size)
    
    # Training parameters
    episodes = 1000
    max_steps_per_episode = 200
    batch_size = 32
    
    for episode in range(episodes):
        # Create new game instance
        game = Game(layout, ai_agent=agent, screen=screen, font=default_font)
        
        total_reward = 0
        
        for step in range(max_steps_per_episode):
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Get current state
            current_state = game.get_state_for_dqn()
            game_state_before = game.get_state_for_ai()  # Save before action
            
            # Get action from agent
            action_idx = agent.act(current_state, training=True)
            actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
            action = actions[action_idx]
            
            # Take action
            game.handle_input(action)
            
            # Get next state
            next_state = game.get_state_for_dqn()
            game_state_after = game.get_state_for_ai()  # Save after action
            
            # Calculate reward using before and after states
            reward = get_reward(game_state_before, game_state_after, action)
            total_reward += reward
            
            # Check if episode is done
            done = game.is_game_over()
            
            # Store experience
            agent.remember(current_state, action_idx, reward, next_state, done)
            
            # Train the agent
            agent.replay(batch_size)
            
            # Update display
            game.draw(screen)
            pygame.display.flip()
            
            if done:
                break
        
        # Update target network every 10 episodes
        if episode % 10 == 0:
            agent.update_target_network()
        
        print(f"Episode: {episode + 1}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.3f}")
        
        # Save model every 100 episodes
        if episode % 100 == 0:
            agent.save(f"pacman_dqn_episode_{episode}.pth")
    
    pygame.quit()

if __name__ == "__main__":
    train_dqn() 