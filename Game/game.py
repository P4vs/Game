import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions and grid size
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700
GRID_SIZE = 10
CELL_SIZE = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (0, 255, 255), (255, 0, 255)]

# Game settings
FONT = pygame.font.Font(None, 36)
LARGE_FONT = pygame.font.Font(None, 48)
BLOCKS = [
    [[1]],  # Single block
    [[1, 1]],  # Horizontal block
    [[1], [1]],  # Vertical block
    [[1, 1], [1, 1]],  # Square block
    [[1, 1, 1]],  # Long horizontal block
    [[1, 1, 1], [0, 1, 0]],  # T-shaped block
    [[1, 1, 0], [0, 1, 1]],  # Z-shaped block
    [[0, 1, 1], [1, 1, 0]],  # S-shaped block
    [[1, 0], [1, 0], [1, 1]],  # L-shaped block
    [[1, 0], [1, 0], [1, 0], [1]],  # Inverted L-shaped block
    [[0, 1, 0], [0, 1, 0], [1, 1, 0]],  # J-shaped block (mirror of L)
    [[1, 0], [1, 0], [0, 1], [0, 1]],  # Reverse S-shaped block
    [[0, 1, 1], [0, 1, 0], [1, 0, 0]],  # T-shape with an extension
]


# Create screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Block Puzzle Game")
clock = pygame.time.Clock()

# High score file path
HIGH_SCORE_FILE = "high_score.txt"

def read_high_score():
    """Reads the high score from the file."""
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            high_score = int(file.read())
        return high_score
    except (FileNotFoundError, ValueError):
        return 0

def write_high_score(score):
    """Writes the high score to the file."""
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))

def draw_grid(grid):
    """Draws the main grid."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = COLORS[grid[row][col] - 1] if grid[row][col] > 0 else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

def block_fits(grid, block, row, col):
    """Checks if a block can fit at a specific location on the grid."""
    for r, line in enumerate(block):
        for c, cell in enumerate(line):
            if cell:
                if (
                    row + r >= GRID_SIZE
                    or col + c >= GRID_SIZE
                    or grid[row + r][col + c] > 0
                ):
                    return False
    return True

def place_block(grid, block, row, col, block_color):
    """Places a block on the grid."""
    for r, line in enumerate(block):
        for c, cell in enumerate(line):
            if cell:
                grid[row + r][col + c] = block_color

def clear_rows_and_columns(grid):
    """Clears full rows and columns from the grid."""
    cleared = 0
    # Check rows
    for row in range(GRID_SIZE):
        if all(grid[row]):
            cleared += 1
            grid[row] = [0] * GRID_SIZE
    # Check columns
    for col in range(GRID_SIZE):
        if all(grid[row][col] for row in range(GRID_SIZE)):
            cleared += 1
            for row in range(GRID_SIZE):
                grid[row][col] = 0
    return cleared

def has_valid_moves(grid, block):
    """Checks if any of the available blocks can fit on the grid."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if block_fits(grid, block, row, col):
                return True
    return False

def draw_next_block(block, color):
    """Draws the upcoming block on the right sidebar."""
    x_offset = GRID_SIZE * CELL_SIZE + 20
    y_offset = 50
    for r, line in enumerate(block):
        for c, cell in enumerate(line):
            if cell:
                rect = pygame.Rect(
                    x_offset + c * (CELL_SIZE // 2),
                    y_offset + r * (CELL_SIZE // 2),
                    CELL_SIZE // 2,
                    CELL_SIZE // 2,
                )
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, GRAY, rect, 1)

    # Add label for the next block
    label = FONT.render("Next Block", True, BLACK)
    screen.blit(label, (x_offset, y_offset - 30))

def draw_leaderboard(score, high_score):
    """Displays the game over screen with the score and high score."""
    screen.fill(WHITE)
    text = LARGE_FONT.render("Game Over!", True, BLACK)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100))

    text = FONT.render(f"Your Score: {score}", True, BLACK)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200))

    text = FONT.render(f"High Score: {high_score}", True, BLACK)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250))

    pygame.display.flip()
    pygame.time.wait(3000)

def main():
    # Load the high score at the start of the game
    high_score = read_high_score()

    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    score = 0
    blocks = [random.choice(BLOCKS)]  # Start with one random block
    block_colors = [random.choice(COLORS)]  # Random color for the block
    dragging = False
    drag_start_x, drag_start_y = 0, 0  # Initial drag positions
    current_block = blocks[0]
    current_block_color = block_colors[0]
    current_block_row, current_block_col = 0, 0  # Initial position of the block
    initial_block_position = (current_block_row, current_block_col)  # Save initial position
    running = True
    block_placed = False

    while running:
        screen.fill(WHITE)
        draw_grid(grid)
        draw_next_block(current_block, current_block_color)

        # Display current score
        score_text = FONT.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, GRID_SIZE * CELL_SIZE + 10))

        # Display high score
        high_score_text = FONT.render(f"High Score: {high_score}", True, BLACK)
        screen.blit(high_score_text, (SCREEN_WIDTH - 200, GRID_SIZE * CELL_SIZE + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Check if the click is within the bounds of the grid
                if 0 <= x < GRID_SIZE * CELL_SIZE and 0 <= y < GRID_SIZE * CELL_SIZE:
                    dragging = True
                    drag_start_x, drag_start_y = x, y

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    x, y = event.pos
                    # Snap the block to the grid position only if it fits
                    col, row = x // CELL_SIZE, y // CELL_SIZE
                    if block_fits(grid, current_block, row, col):
                        # Place the block only if it fits
                        place_block(grid, current_block, row, col, COLORS.index(current_block_color) + 1)
                        score += clear_rows_and_columns(grid)
                        block_placed = True

                    # If it doesn't fit, don't change the block's position
                    # Reset the block's position if not placed
                    if not block_placed:
                        current_block_row, current_block_col = initial_block_position
                    dragging = False

                    # Check if there are valid moves for the next block
                    if not has_valid_moves(grid, current_block):
                        # Update high score if necessary
                        if score > high_score:
                            high_score = score
                            write_high_score(high_score)

                        # Show the Game Over screen
                        draw_leaderboard(score, high_score)
                        running = False
                    else:
                        # Prepare the next block only if it fits
                        if block_placed:
                            current_block = random.choice(BLOCKS)  # New block
                            current_block_color = random.choice(COLORS)  # New color
                            initial_block_position = (0, 0)  # Reset position
                            block_placed = False

            elif event.type == pygame.MOUSEMOTION and dragging:
                x, y = event.pos
                # Update the position of the block being dragged
                new_col = x // CELL_SIZE
                new_row = y // CELL_SIZE

                # Make sure it's within the grid
                if 0 <= new_col < GRID_SIZE and 0 <= new_row < GRID_SIZE:
                    screen.fill(WHITE)
                    draw_grid(grid)
                    draw_next_block(current_block, current_block_color)

                    # Draw the dragged block in the new position with its color (no shadow effect)
                    for r, line in enumerate(current_block):
                        for c, cell in enumerate(line):
                            if cell:
                                rect = pygame.Rect(
                                    new_col * CELL_SIZE + c * CELL_SIZE,
                                    new_row * CELL_SIZE + r * CELL_SIZE,
                                    CELL_SIZE,
                                    CELL_SIZE,
                                )
                                pygame.draw.rect(screen, current_block_color, rect)  # Use the block's color
                                pygame.draw.rect(screen, GRAY, rect, 1)  # Optional outline
                    pygame.display.flip()

        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
