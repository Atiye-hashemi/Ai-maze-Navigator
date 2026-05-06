import pygame
import numpy as np
import time
from agent import RationalAgent
from display import init_display, render_maze, update_display

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

def start_project():
    start_pos = (0, 0)
    target_pos = (3, 3)
    
    screen = init_display(MAZE_LAYOUT.shape)
    agent = RationalAgent(start_pos, target_pos, MAZE_LAYOUT.shape)
    
    # Pre-populate memory to stop start-point circling
    agent.kb.tell_from_matrix(MAZE_LAYOUT)
    agent.kb.tell_visited(start_pos) 
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if agent.pos != target_pos:
            if not agent.think_and_act(MAZE_LAYOUT):
                print("Agent is physically trapped!")
                break

        render_maze(screen, MAZE_LAYOUT, agent.pos, steps_taken=len(agent.path_history)-1)
        update_display()

        if agent.pos == target_pos:
            print(f"Success! Target found in {len(agent.path_history)-1} steps.")
            time.sleep(3)
            break

        time.sleep(0.1)

    pygame.quit()

if __name__ == "__main__":
    start_project()