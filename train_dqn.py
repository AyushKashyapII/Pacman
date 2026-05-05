import pygame
from game import Game
from dqn import DQNAgent, preprocess_state, get_reward
from board import boards
import numpy as np
import argparse
import os
import random
import torch

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

def train_dqn(args=None):
    if args is None:
        args = parse_args()

    if not args.render:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)
        torch.manual_seed(args.seed)

    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    default_font = pygame.font.Font(None, 30) if args.render else None
    
    # Use the board from board.py
    board_data = boards  # boards is already the 2D board data
    layout = convert_board_format(board_data)
    
    # Calculate screen size
    game_rows = len(layout)
    game_cols = len(layout[0])
    screen_width = game_cols * 20  # CELL_SIZE
    screen_height = game_rows * 20 + 80  # GRID_OFFSET_Y
    
    screen = None
    if args.render:
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
    
    agent = DQNAgent(
        state_size,
        action_size,
        learning_rate=args.learning_rate,
        gamma=args.gamma,
        epsilon=args.epsilon,
        epsilon_min=args.epsilon_min,
        epsilon_decay=args.epsilon_decay,
        memory_size=args.memory_size,
    )
    if args.load:
        agent.load(args.load)
    
    # Training parameters
    episodes = args.episodes
    max_steps_per_episode = args.max_steps
    batch_size = args.batch_size
    global_step = 0
    
    for episode in range(episodes):
        # Create new game instance
        game = Game(layout, ai_agent=agent, screen=screen, font=default_font)
        
        total_reward = 0
        losses = []
        
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
            legal_actions = game.get_legal_action_indices()
            action_idx = agent.act(current_state, training=True, legal_actions=legal_actions)
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
            loss = agent.replay(batch_size)
            if loss is not None:
                losses.append(loss)
            global_step += 1

            if global_step % args.target_update_steps == 0:
                agent.update_target_network()
            
            # Update display
            if args.render:
                game.draw(screen)
                pygame.display.flip()
            
            if done:
                break
        
        agent.decay_epsilon()
        
        episode_num = episode + 1
        avg_loss = float(np.mean(losses)) if losses else 0.0
        print(
            f"Episode: {episode_num}, Reward: {total_reward:.2f}, "
            f"Score: {game.pacman.score}, Lives: {game.pacman.lives}, "
            f"Steps: {step + 1}, State: {game.game_state}, "
            f"Epsilon: {agent.epsilon:.3f}, Loss: {avg_loss:.4f}"
        )
        
        # Save model every 100 episodes
        if episode_num % args.save_every == 0:
            agent.save(f"{args.save_prefix}_episode_{episode_num}.pth")

    agent.save(f"{args.save_prefix}_final.pth")
    
    pygame.quit()

def parse_args():
    parser = argparse.ArgumentParser(description="Train the Pac-Man DQN agent.")
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--max-steps", type=int, default=1500)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--memory-size", type=int, default=50000)
    parser.add_argument("--learning-rate", type=float, default=0.0005)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--epsilon", type=float, default=1.0)
    parser.add_argument("--epsilon-min", type=float, default=0.05)
    parser.add_argument("--epsilon-decay", type=float, default=0.995)
    parser.add_argument("--target-update-steps", type=int, default=500)
    parser.add_argument("--save-every", type=int, default=100)
    parser.add_argument("--save-prefix", default="pacman_dqn")
    parser.add_argument("--load", default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--render", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    train_dqn() 
