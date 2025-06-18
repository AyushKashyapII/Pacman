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
        
    def act(self, state, training=True):
        if training and np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.q_network(state)
        return np.argmax(q_values.detach().numpy())
        
    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
            
        batch = random.sample(self.memory, batch_size)
        states = torch.FloatTensor([experience[0] for experience in batch])
        actions = torch.LongTensor([experience[1] for experience in batch])
        rewards = torch.FloatTensor([experience[2] for experience in batch])
        next_states = torch.FloatTensor([experience[3] for experience in batch])
        dones = torch.BoolTensor([experience[4] for experience in batch])
        
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
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
    
    # Flatten the board
    board_flat = []
    for row in board:
        board_flat.extend([1 if cell == 'W' else 0 for cell in row])
    
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
    reward = 0
    
    # Reward for eating pellets
    pellets_diff = game_state['num_pellets_left'] - next_game_state['num_pellets_left']
    reward += pellets_diff * 10
    
    # Reward for eating power pellets (when pacman is powered up)
    if next_game_state['pacman_powered_up'] and not game_state['pacman_powered_up']:
        reward += 50
    
    # Reward for eating ghosts (when powered up)
    # This is tricky to track - we'll use score difference as proxy
    score_diff = next_game_state['pacman_score'] - game_state['pacman_score']
    if score_diff > 10:  # More than just pellet eating
        reward += score_diff
    
    # Penalty for losing life
    lives_diff = next_game_state['pacman_lives'] - game_state['pacman_lives']
    reward += lives_diff * -100
    
    # Small penalty for each action to encourage efficiency
    reward -= 1
    
    # Large reward for winning
    if next_game_state['game_state'] == 'WIN':
        reward += 1000
    
    # Large penalty for game over
    if next_game_state['game_state'] == 'GAME_OVER':
        reward -= 1000
        
    return reward 