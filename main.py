import pygame
import numpy as np
from agent import RationalAgent
from display import init_display, render_maze

MAZE_LAYOUT = np.array([
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 2, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
])

def get_random_target(maze, start_pos):
    """Find a random valid target position (not a wall, not start)."""
    valid_positions = []
    for r in range(maze.shape[0]):
        for c in range(maze.shape[1]):
            if maze[r, c] != 1 and (r, c) != start_pos:  # Not a wall and not start
                valid_positions.append((r, c))
    return np.random.choice(len(valid_positions)), valid_positions

def start_project():
    start_pos = (0, 0)
    _, valid_targets = get_random_target(MAZE_LAYOUT, start_pos)
    target_pos = valid_targets[np.random.randint(0, len(valid_targets))]
    
    screen, clock = init_display(MAZE_LAYOUT.shape)
    agent = RationalAgent(start_pos, target_pos, MAZE_LAYOUT.shape)
    
    agent.kb.tell_from_matrix(MAZE_LAYOUT)
    agent.kb.tell_visited(start_pos) 
    
    running = True
    finished = False
    started  = False 

    while running:
        result = render_maze(screen, clock, MAZE_LAYOUT, agent,
                            start_pos, target_pos, fps=6)

        if result == "quit":
            running = False
        elif result == "start":
            started = True          # ← agent begins stepping
        elif result == "reset":
            agent = RationalAgent(start_pos, target_pos, MAZE_LAYOUT.shape)
            agent.kb.tell_from_matrix(MAZE_LAYOUT)
            agent.kb.tell_visited(start_pos)
            finished = False
            started  = False        # ← goes back to Start button

        if started and not finished:
            if agent.pos != target_pos:
                if not agent.think_and_act(MAZE_LAYOUT):
                    finished = True
            else:
                finished = True

    pygame.quit()


if __name__ == "__main__":
    start_project()