import pygame
from pygame.locals import *
import time
import heapq

# Constants for ingame objects
PACMAN_COLOR = (255, 255, 0)
FOOD_COLOR = (255, 255, 255)
WALL_COLOR = (0, 0, 255)
RUNTIME = 100
MOVE_DELAY = 0.3

# Set up colors and fonts
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Node class
class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = 0
        self.h = 0

    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)

class Map:
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()
            
        contents = contents.splitlines()
        area = contents[0].split(' ')
        self.height = int(area[0])
        self.width = int(area[1])
        
        contents = contents[1:]

        pacman_position = contents[-1].split(' ')
        self.pacman = (int(pacman_position[0]), int(pacman_position[1]))

        contents = contents[:-1]
        
        new_contents = []
        for line in contents:
            new_contents.append(line.rstrip('\n').split(' '))
        contents = new_contents
        
        self.walls = []
        self.possibleMoves = []
    
        for i in range(self.height):
            row_wall = []
            row_move = []
            for j in range(self.width):
                try:
                    if contents[i][j] == '2':
                        self.food = (i, j)
                        row_move.append(False)
                        row_wall.append(False)
                    elif contents[i][j] == '0':
                        row_move.append(True)
                        row_wall.append(False)
                    elif contents[i][j] == '1':
                        row_move.append(False)
                        row_wall.append(True)
                    elif (i, j) == self.pac_man:
                        row_move.append(False)
                        row_wall.append(False)
                except IndexError:
                    row_move.append(False)
                    row_wall.append(False)
                    
            self.walls.append(row_wall)
            self.possibleMoves.append(row_move)
        self.solution = None

    def neighbor(self, state):
        row, col = state

        candidates = [
            ('up', (row - 1, col)),
            ('down', (row + 1, col)),
            ('left', (row, col - 1)),
            ('right', (row, col + 1))]
        results = []
        for action, (r, c) in candidates:
            try:
                if not self.walls[r][c]:
                    results.append((action, (r, c)))
            except IndexError:
                continue
        return results

    def solve_BFS(self):
        self.num_explored = 0
        start = Node(state=self.pacman, parent=None, action=None)

        self.explored = set()
        frontier = []

        heapq.heappush(frontier, start)

        while frontier:
            current = heapq.heappop(frontier)
            self.num_explored += 1

            if current.state == self.food:
                actions = []
                cells = []

                while current.parent is not None:
                    actions.append(current.action)
                    cells.append(current.state)
                    current = current.parent

                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
            self.explored.add(current.state)

            for action, state in self.neighbor(current.state):
                isExist = False
                for node in frontier:
                    if node.state == state:
                        isExist = True
                        break
                if not isExist and state not in self.explored:
                    child = Node(state=state, parent=current, action=action)
                    heapq.heappush(frontier, child)

    def solve_Astar(self):
        self.num_explored = 0
        start = Node(state=self.pacman, parent=None, action=None)

        self.explored = set()
        frontier = []
        heapq.heappush(frontier, start)

        while frontier:
            current = heapq.heappop(frontier)
            self.num_explored += 1

            if current.state == self.food:
                actions = []
                cells = []

                while current.parent is not None:
                    actions.append(current.action)
                    cells.append(current.state)
                    current = current.parent

                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
            self.explored.add(current.state)

            for action, state in self.neighbor(current.state):
                isExist = False
                for node in frontier:
                    if node.state == state:
                        isExist = True
                        break
                if not isExist and state not in self.explored:
                    child = Node(state=state, parent=current, action=action)
                    child.g = current.g + 1
                    child.h = abs(child.state[0] - self.food[0]) + abs(child.state[1] - self.food[1])
                    heapq.heappush(frontier, child)

    def solve_GBFS(self):
        self.num_explored = 0
        start = Node(state=self.pacman, parent=None, action=None)

        self.explored = set()
        frontier = []
        heapq.heappush(frontier, start)

        while frontier:
            current = heapq.heappop(frontier)
            self.num_explored += 1

            if current.state == self.food:
                actions = []
                cells = []

                while current.parent is not None:
                    actions.append(current.action)
                    cells.append(current.state)
                    current = current.parent

                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
            self.explored.add(current.state)

            for action, state in self.neighbor(current.state):
                isExist = False
                for node in frontier:
                    if node.state == state:
                        isExist = True
                        break
                if not isExist and state not in self.explored:
                    child = Node(state=state, parent=current, action=action)
                    child.h = abs(child.state[0] - self.food[0]) + abs(child.state[1] - self.food[1])
                    heapq.heappush(frontier, child)

# solve map
def solve_map(selected_option):
    # Create the display surface
    pygame.init()
    screen_menu = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Menu Algorithms")

    # Create font
    FONT = pygame.font.Font(None, 36)

    # Menu options
    options = ["BFS", "GBFS", "Astar"]

    # Position for menu items
    menu_rects = [FONT.render("   " + option, True, WHITE).
                  get_rect(center=(200, 100 + index * 50)) for index, option in enumerate(options)]

    # Game loop
    selected_algorithm = 0
    running_menu = True
    
    # Initialize map
    filename = f'../input/level1_map{selected_option + 1}.txt'
    gameplay = Map(filename)

    # Constants
    GRID_SIZE = 50
    WIDTH, HEIGHT = gameplay.width * 50, (gameplay.height + 2) * 50
    GRID_WIDTH, GRID_HEIGHT = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE

    # Initialize game screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Pac-Man Level 1 - Map {selected_option + 1}")
    
    # Initialize positions
    pacman_y, pacman_x = gameplay.pacman

    m = gameplay.width
    n = gameplay.height

    # Generate food coordinate
    food_y, food_x = gameplay.food

    # Generate walls
    walls = gameplay.walls     

    # Possible moves
    possibleMoves = gameplay.possibleMoves

    def draw_menu():
        screen_menu.fill((0, 0, 0))
        for index, rect in enumerate(menu_rects):
            color = YELLOW if index == selected_algorithm else WHITE
            text = FONT.render(
                "-> " + options[index] if index == selected_algorithm else "   " + options[index], True, color)
            screen_menu.blit(text, rect)

    while running_menu:
        for event in pygame.event.get():
            if event.type == QUIT:
                running_menu = False

            if event.type == MOUSEBUTTONDOWN:
                for index, rect in enumerate(menu_rects):
                    if rect.collidepoint(event.pos):
                        selected_algorithm = index

            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_algorithm = (
                        selected_algorithm - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_algorithm = (
                        selected_algorithm + 1) % len(options)
                elif event.key == K_RETURN:
                    # Save path
                    path = []
                    ticks = 0
                    visited_cells = set()

                    # Main game loop
                    running = True
                    path_calculated = False
                    path_traced = False
                    game_over = False
                    win_message_displayed = False
                    lose_message_displayed = False

                    score_map = 0

                    path_length = 0
                    def drawScore(score_map):
                        text_font = pygame.font.SysFont("Arial", 36)
                        surface = pygame.Surface((n * GRID_SIZE, 1 * GRID_SIZE))
                        surface.fill((255, 255, 255))
                        screen.blit(surface, ((m * GRID_SIZE, n * GRID_SIZE)))
                        score = text_font.render(f'Score: {score_map}', True, (255, 255, 255))
                        screen.blit(score, (GRID_SIZE, n * GRID_SIZE))
                    def drawPathLength(path_length):
                        text_font = pygame.font.SysFont("Arial", 36)
                        surface = pygame.Surface((n * GRID_SIZE, 1 * GRID_SIZE))
                        surface.fill((255, 255, 255))
                        screen.blit(surface, ((m * GRID_SIZE, n * GRID_SIZE)))
                        score = text_font.render(f'Explored Node: {path_length}', True, (255, 255, 255))
                        screen.blit(score, (GRID_SIZE, (n + 1) * GRID_SIZE))

                    while running:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                        if not game_over:
                            if not path_calculated:
                                if selected_algorithm == 0:
                                    gameplay.solve_BFS()
                                elif selected_algorithm == 1:
                                    gameplay.solve_GBFS()
                                elif selected_algorithm == 2:
                                    gameplay.solve_Astar()

                                path = gameplay.solution[1]
                                path_length = gameplay.num_explored
                                path_calculated = True

                            if path and ticks < RUNTIME:
                                pacman_y, pacman_x = path[0]
                                visited_cells.add((pacman_x, pacman_y))
                                path = path[1:]
                                score_map -= 1
                                ticks += 1
                                time.sleep(MOVE_DELAY)

                            if (pacman_x, pacman_y) == (food_x, food_y):
                                score_map += 20
                                game_over = True
                                win_message_displayed = True

                            if not path and not game_over and not path_traced:
                                game_over = True
                                lose_message_displayed = True

                        screen.fill((0, 0, 0))

                        for x in range(m):
                            for y in range(n):
                                pygame.draw.rect(screen, (255, 255, 255),
                                                 (x * GRID_SIZE, y * GRID_SIZE,
                                                  GRID_SIZE, GRID_SIZE), 1)

                        for y, row in enumerate(walls):
                            for x, col in enumerate(row):
                                if col:  # Draw walls
                                    wall_x, wall_y = x * GRID_SIZE, y * GRID_SIZE
                                    # Draw the wall using custom texture
                                    pygame.draw.rect(screen, WALL_COLOR,
                                                     (wall_x, wall_y, GRID_SIZE, GRID_SIZE), 1)

                                    # Draw diagonal lines on the wall
                                    pygame.draw.line(screen, WALL_COLOR, (wall_x, wall_y),
                                                     (wall_x + GRID_SIZE, wall_y + GRID_SIZE), 2)
                                    pygame.draw.line(screen, WALL_COLOR, (wall_x + GRID_SIZE, wall_y),
                                                     (wall_x, wall_y + GRID_SIZE), 2)
                                elif possibleMoves[y][x] and (x, y) not in visited_cells:
                                    space_x, space_y = x * GRID_SIZE, y * GRID_SIZE
                                    pygame.draw.circle(screen, FOOD_COLOR,
                                                     (space_x + GRID_SIZE // 2, 
                                                      space_y + GRID_SIZE // 2), 
                                                     GRID_SIZE // 6)
                                    

                        pygame.draw.circle(screen, FOOD_COLOR,
                                           (food_x * GRID_SIZE + GRID_SIZE // 2,
                                            food_y * GRID_SIZE + GRID_SIZE // 2),
                                           GRID_SIZE // 3)
                        pygame.draw.circle(screen, PACMAN_COLOR,
                                           (pacman_x * GRID_SIZE + GRID_SIZE // 2,
                                            pacman_y * GRID_SIZE + GRID_SIZE // 2),
                                           GRID_SIZE // 3)

                        drawScore(score_map)

                        if path_traced:
                            for cell in visited_cells:
                                pygame.draw.rect(screen, (0, 255, 0),
                                                 (cell[0] * GRID_SIZE, cell[1] * GRID_SIZE,
                                                  GRID_SIZE, GRID_SIZE))

                        if not path and not path_traced:
                            path_traced = True

                        if game_over:
                            if win_message_displayed:
                                FONT = pygame.font.Font(None, 36)
                                text = FONT.render(
                                    "You Win!", True, (0, 255, 0))
                                text_rect = text.get_rect(
                                    center=(WIDTH // 2, HEIGHT // 2))
                                screen.blit(text, text_rect)
                                drawPathLength(path_length)
                            elif lose_message_displayed:
                                FONT = pygame.font.Font(None, 36)
                                text = FONT.render(
                                    "You Lose!", True, (255, 0, 0))
                                text_rect = text.get_rect(
                                    center=(WIDTH // 2, HEIGHT // 2))
                                screen.blit(text, text_rect)
                                drawPathLength(path_length)

                        pygame.display.flip()

        draw_menu()
        pygame.display.flip()


# Main function for Level 1
def main():
    # Create menu maps
    pygame.init()

    # Create the display surface
    screen_menu = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Menu Maps")

    # Create font
    FONT = pygame.font.Font(None, 36)

    # Menu options
    options = ["Map 1", "Map 2", "Map 3"]

    # Position for menu items
    menu_rects = [FONT.render("   " + option, True, WHITE).
                  get_rect(center=(200, 100 + index * 50)) for index, option in enumerate(options)]

    # Game loop
    selected_map = 0
    running_menu = True

    def draw_menu():
        screen_menu.fill((0, 0, 0))
        for index, rect in enumerate(menu_rects):
            color = YELLOW if index == selected_map else WHITE
            text = FONT.render(
                "-> " + options[index] if index == selected_map else "   " + options[index], True, color)
            screen_menu.blit(text, rect)

    while running_menu:
        for event in pygame.event.get():
            if event.type == QUIT:
                running_menu = False

            if event.type == MOUSEBUTTONDOWN:
                for index, rect in enumerate(menu_rects):
                    if rect.collidepoint(event.pos):
                        selected_map = index

            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_map = (selected_map - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_map = (selected_map + 1) % len(options)
                elif event.key == K_RETURN:
                    if selected_map == 0:   # Start Map 1
                        solve_map(selected_map)
                    elif selected_map == 1: # Start Map 2
                        solve_map(selected_map)
                    elif selected_map == 2: # Start Map 3
                        solve_map(selected_map)

        draw_menu()
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
