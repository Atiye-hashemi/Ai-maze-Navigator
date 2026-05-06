import pygame
import numpy as np


# ---------------------------------------------------------------------------
# Constants  (tweak CELL_SIZE to scale the whole grid up or down)
# ---------------------------------------------------------------------------

CELL_SIZE = 50          # pixels per cell — grid is fully scalable from here

# Colour palette  (matches the contract: 1→Black, 0→White, 2→Gold, 3→Blue)
COLOUR_PATH   = (255, 255, 255)   # 0 – open path    → White
COLOUR_WALL   = (0,   0,   0)    # 1 – wall          → Black
COLOUR_TARGET = (212, 175, 55)   # 2 – target        → Gold
COLOUR_AGENT  = (30,  80,  160)  # 3 – agent/robot   → Blue
COLOUR_GRID   = (200, 200, 200)  # thin grid lines   → Light grey
COLOUR_BG     = (245, 245, 245)  # window background → Off-white
COLOUR_TEXT   = (30,  30,  30)   # overlay text      → Dark grey

# Text overlay settings
FONT_SIZE     = 18
OVERLAY_PAD   = 10    # pixels of padding for the Steps Taken overlay


# ---------------------------------------------------------------------------
# Helper: one-time setup
# ---------------------------------------------------------------------------

def init_display(maze_shape: tuple) -> pygame.Surface:
    """
    Initialise pygame and create a window sized to fit the maze.

    Call this ONCE at the start of main.py before the game loop.

    Parameters
    ----------
    maze_shape : (rows, cols)  — use  maze.shape  directly

    Returns
    -------
    pygame.Surface  –  pass this to  render_maze()  every frame
    """
    pygame.init()
    rows, cols = maze_shape
    width  = cols * CELL_SIZE
    height = rows * CELL_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Maze AI — Genetic Algorithm Pathfinder")
    return screen


def update_display():
    """
    Flip the pygame display buffer so the new frame becomes visible.
    Call this ONCE per frame, right after render_maze().
    """
    pygame.display.flip()


# ---------------------------------------------------------------------------
# Public API  (name is fixed by the Maze Contract – do not rename)
# ---------------------------------------------------------------------------

def render_maze(screen: pygame.Surface, matrix: np.ndarray,
                agent_pos: tuple, steps_taken: int = 0):
    """
    Draw the full maze grid onto `screen` for one frame.

    Cell colour mapping (Maze Contract):
        0  →  White   (open path)
        1  →  Black   (wall)
        2  →  Gold    (target)
        3  →  Blue    (agent current position)

    A "Steps Taken: N" text overlay is drawn in the top-left corner.

    Parameters
    ----------
    screen      : pygame.Surface returned by init_display()
    matrix      : 2-D numpy array representing the current maze state
    agent_pos   : (row, col) tuple — the agent's current position
                  (the cell at this position is highlighted as the agent)
    steps_taken : integer counter shown in the "Steps Taken" overlay
    """
    screen.fill(COLOUR_BG)   # clear the frame

    rows, cols = matrix.shape

    # ── 1. Draw every cell ────────────────────────────────────────────────
    for row in range(rows):
        for col in range(cols):

            # Pixel position of the top-left corner of this cell
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            # Pick the fill colour from the matrix value
            cell_value = int(matrix[row, col])

            if (row, col) == agent_pos:
                # Agent always renders as Blue, even if the matrix cell
                # value hasn't been updated yet (defensive drawing)
                fill_colour = COLOUR_AGENT
            elif cell_value == 1:
                fill_colour = COLOUR_WALL
            elif cell_value == 2:
                fill_colour = COLOUR_TARGET
            elif cell_value == 3:
                fill_colour = COLOUR_AGENT
            else:
                fill_colour = COLOUR_PATH   # 0 or any unknown value

            # Fill the cell
            pygame.draw.rect(screen, fill_colour,
                             (x, y, CELL_SIZE, CELL_SIZE))

            # Draw the grid line border (thin, subtle)
            pygame.draw.rect(screen, COLOUR_GRID,
                             (x, y, CELL_SIZE, CELL_SIZE), width=1)

    # ── 2. "Steps Taken" text overlay ─────────────────────────────────────
    font = pygame.font.SysFont("monospace", FONT_SIZE, bold=True)
    label = font.render(f"Steps Taken: {steps_taken}", True, COLOUR_TEXT)

    # Semi-transparent background pill behind the text for readability
    pad = OVERLAY_PAD
    pill_rect = pygame.Rect(
        pad - 4,
        pad - 4,
        label.get_width()  + 12,
        label.get_height() + 8
    )
    pill_surface = pygame.Surface(
        (pill_rect.width, pill_rect.height), pygame.SRCALPHA
    )
    pill_surface.fill((255, 255, 255, 190))   # white, 75 % opaque
    screen.blit(pill_surface, (pill_rect.x, pill_rect.y))
    screen.blit(label, (pad, pad))
