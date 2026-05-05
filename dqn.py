import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import random
from collections import deque
import math

class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_size)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    def __init__(self, state_size, action_size, learning_rate=0.001, gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, memory_size=10000):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.memory = deque(maxlen=memory_size)
        
        # Neural Networks
        self.q_network = DQN(state_size, action_size)
        self.target_network = DQN(state_size, action_size)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Update target network
        self.update_target_network()
        
    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, state, training=True, legal_actions=None):
        if legal_actions is None:
            legal_actions = list(range(self.action_size))
        if not legal_actions:
            legal_actions = list(range(self.action_size))

        if training and np.random.random() <= self.epsilon:
            return random.choice(legal_actions)
        
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = self.q_network(state).squeeze(0)

        masked_q_values = torch.full_like(q_values, -float("inf"))
        masked_q_values[legal_actions] = q_values[legal_actions]
        return int(torch.argmax(masked_q_values).item())
        
    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
            
        batch = random.sample(self.memory, batch_size)
        states = torch.FloatTensor(np.array([experience[0] for experience in batch], dtype=np.float32))
        actions = torch.LongTensor([experience[1] for experience in batch])
        rewards = torch.FloatTensor([experience[2] for experience in batch])
        next_states = torch.FloatTensor(np.array([experience[3] for experience in batch], dtype=np.float32))
        dones = torch.BoolTensor([experience[4] for experience in batch])
        
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        with torch.no_grad():
            next_actions = self.q_network(next_states).argmax(1)
            next_q_values = self.target_network(next_states).gather(1, next_actions.unsqueeze(1)).squeeze(1)
        target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        loss = F.smooth_l1_loss(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            
    def save(self, filename):
        torch.save(self.q_network.state_dict(), filename)
        
    def load(self, filename):
        self.q_network.load_state_dict(torch.load(filename))
        self.update_target_network()

# State preprocessing functions
def preprocess_state(game_state):
    """
    Convert game state to a format suitable for DQN
    """
    # Extract relevant information from game state
    board = game_state['board']
    pacman_pos = game_state['pacman_pos']
    ghosts_pos = game_state['ghosts_pos']
    ghosts_modes = game_state['ghosts_modes']
    
    # Flatten the board. The agent must see remaining food; otherwise many
    # different board states collapse to the same wall-only observation.
    board_flat = []
    for row in board:
        for cell in row:
            if cell == 'W':
                board_flat.append(1.0)
            elif cell == '.':
                board_flat.append(0.5)
            elif cell == 'P':
                board_flat.append(0.75)
            else:
                board_flat.append(0.0)
    
    # Normalize positions
    rows, cols = len(board), len(board[0])
    pacman_normalized = [pacman_pos[0] / rows, pacman_pos[1] / cols]
    
    # Ghost positions (normalized)
    ghosts_normalized = []
    for ghost_pos in ghosts_pos:
        ghosts_normalized.extend([ghost_pos[0] / rows, ghost_pos[1] / cols])
    
    # Ghost modes (one-hot encoded)
    mode_encoding = {'CHASE': [1, 0, 0], 'SCATTER': [0, 1, 0], 'FRIGHTENED': [0, 0, 1]}
    ghost_modes_encoded = []
    for mode in ghosts_modes:
        ghost_modes_encoded.extend(mode_encoding.get(mode, [0, 0, 0]))
    
    # Combine all features
    state_vector = board_flat + pacman_normalized + ghosts_normalized + ghost_modes_encoded
    
    return np.array(state_vector, dtype=np.float32)

def get_reward(game_state, next_game_state, action):
    """
    Calculate reward based on game state changes
    """
    reward = -0.05
    
    # Reward for eating pellets
    pellets_diff = game_state['num_pellets_left'] - next_game_state['num_pellets_left']
    reward += pellets_diff * 10
    
    # Reward for eating power pellets (when pacman is powered up)
    if next_game_state['pacman_powered_up'] and not game_state['pacman_powered_up']:
        reward += 25
    
    # Reward for eating ghosts (when powered up)
    # This is tricky to track - we'll use score difference as proxy
    score_diff = next_game_state['pacman_score'] - game_state['pacman_score']
    if score_diff > 50:  # Ghost eating is worth more than a power pellet.
        reward += score_diff
    
    # Penalty for losing life
    lives_diff = next_game_state['pacman_lives'] - game_state['pacman_lives']
    if lives_diff < 0:
        reward += lives_diff * 200

    if game_state['pacman_pos'] == next_game_state['pacman_pos'] and next_game_state['game_state'] == 'PLAYING':
        reward -= 5

    before_food_distance = nearest_food_distance(game_state)
    after_food_distance = nearest_food_distance(next_game_state)
    if before_food_distance is not None and after_food_distance is not None:
        if after_food_distance < before_food_distance:
            reward += 0.5
        elif after_food_distance > before_food_distance:
            reward -= 0.25
    
    # Large reward for winning
    if next_game_state['game_state'] == 'WIN':
        reward += 1000
    
    # Large penalty for game over
    if next_game_state['game_state'] == 'GAME_OVER':
        reward -= 500
        
    return reward 

def nearest_food_distance(game_state):
    pacman_row, pacman_col = game_state['pacman_pos']
    best_distance = None
    for row_idx, row in enumerate(game_state['board']):
        for col_idx, cell in enumerate(row):
            if cell in ('.', 'P'):
                distance = abs(pacman_row - row_idx) + abs(pacman_col - col_idx)
                if best_distance is None or distance < best_distance:
                    best_distance = distance
    return best_distance
