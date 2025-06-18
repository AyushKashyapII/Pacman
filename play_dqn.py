import pygame
from game import Game
from dqn import DQNAgent, preprocess_state
from board import boards

def convert_board_format(board_data):
    rows = len(board_data)
    cols = len(board_data[0])
    converted_board = []
    pacman_start = (23, 13)
    ghost_starts = [(11, 13), (11, 14), (11, 15), (11, 16)]
    for row in range(rows):
        new_row = []
        for col in range(cols):
            cell = board_data[row][col]
            if (row, col) == pacman_start:
                new_row.append('S')
            elif (row, col) in ghost_starts:
                new_row.append('G')
            elif cell == 0:
                new_row.append(' ')
            elif cell == 1:
                new_row.append('.')
            elif cell == 2:
                new_row.append('P')
            elif cell in [3, 4, 5, 6, 7, 8, 9]:
                new_row.append('W')
            else:
                new_row.append(' ')
        converted_board.append(''.join(new_row))
    return converted_board

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    default_font = pygame.font.Font(None, 30)
    board_data = boards
    layout = convert_board_format(board_data)
    game_rows = len(layout)
    game_cols = len(layout[0])
    screen_width = game_cols * 20
    screen_height = game_rows * 20 + 80
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pac-Man DQN Play")

    # Use the same state size as in training
    board_size = game_rows * game_cols
    pacman_features = 2
    ghost_features = 2 * 4
    ghost_mode_features = 3 * 4
    state_size = board_size + pacman_features + ghost_features + ghost_mode_features
    action_size = 4

    agent = DQNAgent(state_size, action_size)
    # Load the model trained for 100 episodes (change to 1000 when ready)
    agent.load("pacman_dqn_episode_0.pth")  # Change to 'pacman_dqn_episode_1000.pth' after more training

    game = Game(layout, ai_agent=agent, screen=screen, font=default_font)
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game.is_game_over():
            state = game.get_state_for_dqn()
            action_idx = agent.act(state, training=False)  # Greedy action
            actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
            action = actions[action_idx]
            game.handle_input(action)

        game.draw(screen)
        pygame.display.flip()
        clock.tick(10)  # Adjust speed as needed

    pygame.quit()