import math
import copy
import pygame
import sys
import time
one_block_size = 30 #pixel
SCREEN_HEIGHT = 20 * one_block_size
SCREEN_WIDTH = SCREEN_HEIGHT * 2

# SOME VARIABLE
GAME_NAME = 'Pacman'
FPS = 30
running = True

# SET COLORS
WALL_COLOR = (3, 64, 214)
GHOST_COLOR = (255, 0, 0) #red
PACMAN_COLOR = (255,255,0)
FOODS_COLOR = (255, 255, 255)
BLACK = (0, 0, 0)

# CheckFinish
WIN = 0
LOSE = 1
CONTINUE = 2


def readFile(path):
    global pacmanX, pacmanY
    f = open(path, 'r')

    size = [int(x) for x in f.readline().strip().split(' ')]
    Ncol = size[0]
    Nrow = size[1]


    adjacencyMatrix = []
    for i in range(Ncol):
        adjacencyMatrix.append(f.readline().rstrip('\n').split())

    pos = [int(x) for x in f.readline().strip().split(' ')]
    pacmanX = pos[0]
    pacmanY = pos[1]

    f.close()
    for x in range(len(adjacencyMatrix)):
        for y in range(len(adjacencyMatrix[x])):
            adjacencyMatrix[x][y] = int(adjacencyMatrix[x][y])

    return adjacencyMatrix


# Hàm lấy vị trí quái và số lượng thức ăn từ map
def getInfo(map):
    monsters = []
    numOfFood = 0
    for x in range(len(map)):
        for y in range(len(map[x])):
            if map[x][y] == 3:
                map[x][y] = 0
                monsters.append((x, y))
            elif map[x][y] == 2:
                numOfFood += 1
    return (monsters, numOfFood)


# Hàm cho monster di chuyển
def monstersMove(map, monsterPos, pacman):
    if monsterPos[0] == pacman[0] and monsterPos[1] == pacman[1]:
        return (monsterPos[0], monsterPos[1])

    option = []
    # tThêm các ô lân cận nếu không phải tường
    if int(map[monsterPos[0] - 1][monsterPos[1]]) != 1:
        option.append((monsterPos[0] - 1, monsterPos[1]))
    if int(map[monsterPos[0]][monsterPos[1] + 1]) != 1:
        option.append((monsterPos[0], monsterPos[1] + 1))
    if int(map[monsterPos[0] + 1][monsterPos[1]]) != 1:
        option.append((monsterPos[0] + 1, monsterPos[1]))
    if int(map[monsterPos[0]][monsterPos[1] - 1]) != 1:
        option.append((monsterPos[0], monsterPos[1] - 1))

    if not option:
        return (monsterPos[0], monsterPos[1])

    distance = []
    for x in option:
        distance.append(((x[0] - pacman[0]) ** 2 + (x[1] - pacman[1]) ** 2))

    shortest = distance.index(min(distance))

    return option[shortest]


# Hàm kiểm tra va cham voi quai vat
def isCollide(pacman, monsters):
    for m in monsters:
        if m[0] == pacman[0] and m[1] == pacman[1]:
            return True
    return False


# Ham ap dung thuat toan GBFS cho phep pacman di chuyen tim thuc an
def pacmanMove_GBFS(map, currentPos, lastPos, monsters, numOfFood, score, trace):
    trace2 = copy.deepcopy(trace)
    trace2.append(currentPos)

    if isCollide(currentPos, monsters) or len(trace) > 20:
        return (score, trace2, "collide")

    if map[currentPos[0]][currentPos[1]] == 2:
        numOfFood -= 1
        score += 1
        map[currentPos[0]][currentPos[1]] = 0
        return (score, trace2, "found 1 food")

    if numOfFood == 0:
        return (score, trace2, "out of food")

    option = []
    for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        newX, newY = currentPos[0] + dx, currentPos[1] + dy
        if 0 <= newX < len(map) and 0 <= newY < len(map[0]) and map[newX][newY] != 1:
            option.append((newX, newY))

    if not option:
        return (score, trace2, "no option")

    # Calculate heuristic values using Manhattan distance to the nearest food
    heuristic_values = []
    for x in option:
        min_distance = float('inf')
        for food in trace:
            distance = abs(x[0] - food[0]) + abs(x[1] - food[1])
            min_distance = min(min_distance, distance)
        heuristic_values.append(min_distance)

    # Sort options based on heuristic values (GBFS)
    sorted_options = [x for _, x in sorted(zip(heuristic_values, option))]

    result = (-math.inf, [])
    for x in sorted_options:
        output = pacmanMoveExplored(copy.deepcopy(map), x, currentPos, copy.deepcopy(monsters), numOfFood, score, trace2)
        if output[0] > result[0]:
            result = output
        elif output[0] == result[0] and len(output[1]) < len(result[1]):
            result = output

    return result


def pacmanMoveExplored(map, currentPos, lastPos, monsters, numOfFood, score, trace):
    trace2 = copy.deepcopy(trace)

    for i in range(len(monsters)):  # Cập nhật lại vị trí mới của quái vật trong mảng monster
        monsters[i] = monstersMove(map, monsters[i], currentPos)

    result = pacmanMove_GBFS(copy.deepcopy(map), currentPos, lastPos, copy.deepcopy(monsters), numOfFood, score, trace2)
    return result


# hàm level 4 handle
def level4(map, numOfFood, monsters, pacman):
    map_copy = copy.deepcopy(map)
    monstersPos = copy.deepcopy(monsters)  # Không làm ảnh hưởng mảng gốc

    # Khởi tạo mảng để lưu bước đi của monster
    monstersMoveList = []
    if monsters:
        for i in range(len(monsters)):
            monstersMoveList.append([])
            monstersMoveList[i].append(monsters[i])
    pacmanMoveList = [pacman]
    numEaten = 0
    while numOfFood > 0:
        output = pacmanMove_GBFS(map_copy, pacmanMoveList[-1], pacmanMoveList[-1], monstersPos, numOfFood, 0, [])

        if not output[1]:
            print("stop by break")
            break

        numOfFood -= output[0]
        numEaten += output[0]
        temp = output[1].pop(0)
        pacmanMoveList = pacmanMoveList + output[1]

        for p in output[1]:
            for m in range(len(monstersMoveList)):
                monstersMoveList[m].append(monstersMove(map, monstersMoveList[m][-1], p))
        for y in range(len(monstersMoveList)):
            monstersPos[y] = monstersMoveList[y][-1]

        map_copy = copy.deepcopy(map)
        for x in pacmanMoveList:
            map_copy[x[0]][x[1]] = 0

        if output[2] == "collide":
            break

        if output[2] == "no option":
            pacmanMoveList = pacmanMoveList + [temp]
            for m in range(len(monstersMoveList)):
                monstersMoveList[m].append(monstersMove(map, monstersMoveList[m][-1], temp))
            break

    return (numEaten, pacmanMoveList, monstersMoveList, output[2])


def initGameScreen():
    pygame.init()
    pygame.display.set_caption(GAME_NAME)
    pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(BLACK)
    clock = pygame.time.Clock()

    return screen, clock


class sprite:
    def __init__(self, position) -> None:
        self.currentPosition = position
        self.surface = pygame.Surface((one_block_size, one_block_size))
        self.surface.fill(BLACK)

    def changePosition(self, newPosition):
        self.currentPosition = newPosition

    def draw(self):
        screen.blit(self.surface, (self.currentPosition[1] * one_block_size, self.currentPosition[0] * one_block_size))


class Wall(sprite):
    def __init__(self, position) -> None:
        super().__init__(position)
        pygame.draw.rect(self.surface, (0, 0, 255), (0, 0, 30, 30))
        pygame.draw.rect(self.surface, (255, 255, 255), (0, 0, 30, 30), 1)
        # pygame.draw.line(self.surface, (0, 0, 0), (position[1] * 30, position[0] * 30), (position[1] * 30 + 30, position[0] * 30 + 30), 3)
        # pygame.draw.line(self.surface, (0, 0, 0), (position[1] * 30, position[0] * 30 + 30), (position[1] * 30 + 30, position[0] * 30), 3)
        self.draw()


class Ghost(sprite):
    def __init__(self, position) -> None:
        super().__init__(position)
        pygame.draw.circle(self.surface, GHOST_COLOR, ((one_block_size) / 2, (one_block_size) / 2), one_block_size / 2,
                           0)
        self.draw()


class Pacman(sprite):
    DEAD = False

    def __init__(self, position) -> None:
        super().__init__(position)
        pygame.draw.circle(self.surface, PACMAN_COLOR, ((one_block_size) / 2, (one_block_size) / 2), one_block_size / 2,
                           0)
        self.draw()


class Food(sprite):
    def __init__(self, position) -> None:
        super().__init__(position)
        pygame.draw.circle(self.surface, FOODS_COLOR, ((one_block_size) / 2, (one_block_size) / 2), one_block_size / 4,
                           0)
        self.draw()


class Game:
    Foods = []
    Ghosts = []
    Player = -1
    Point = 0

    def __init__(self, Matrix, pacman) -> None:
        self.Player = Pacman(pacman)
        for row in range(len(Matrix)):
            for column in range(len(Matrix[row])):
                if Matrix[row][column] == 1:
                    temp = Wall((row, column))
                elif Matrix[row][column] == 2:
                    temp = Food((row, column))
                    self.Foods.append(temp)
                elif Matrix[row][column] == 3:
                    temp = Ghost((row, column))
                    self.Ghosts.append(temp)

    def checkGameFinish(self):
        isFinish = False
        if self.Player.DEAD:
            isFinish = True
            return isFinish, LOSE
        if len(self.Foods) == 0:
            isFinish = True
            return isFinish, WIN
        return isFinish, CONTINUE

    def ghostMove(self, position, idx):
       self.Ghosts[idx].changePosition(position)

    def pacmanMove(self, position):
        newPosition = position

        self.Player.changePosition(newPosition)

        isPacmanEatFood, foodIndex = self.checkEatFood()
        if isPacmanEatFood:
            self.Point += 20
            self.Foods.pop(foodIndex)

        self.Point -= 1

    def checkColision(self):

        for ghost in self.Ghosts:
            if ghost.currentPosition[0] == self.Player.currentPosition[0] and ghost.currentPosition[1] == \
                    self.Player.currentPosition[1]:
                return True
        return False

    def checkEatFood(self):
        for food in self.Foods:
            if food.currentPosition[0] == self.Player.currentPosition[0] and food.currentPosition[1] == \
                    self.Player.currentPosition[1]:
                return True, self.Foods.index(food)
        return False, -1

    def clearAnimation(self):
        temp = sprite(self.Player.currentPosition)
        temp.draw()
        for ghost in self.Ghosts:
            temp.currentPosition = ghost.currentPosition
            temp.draw()


def drawScore():
    text_font = pygame.font.SysFont("Arial", 36)
    surface = pygame.Surface((10 * one_block_size, 2 * one_block_size))
    surface.fill(BLACK)
    screen.blit(surface, ((3 * one_block_size, m * one_block_size)))
    score = text_font.render(f'Score: {game.Point}', True, (255, 255, 255))
    screen.blit(score, (one_block_size, m * one_block_size))


def handle_input():
    map_name = "../input/level4_map1.txt"

    file = open(map_name, 'r')
    # count number of line
    cnt_line = len(file.readlines())
    file.close()

    file = open(map_name, 'r')
    MAP = []
    idx = 0
    for line in file:
        if idx == 0:
            size = line.split()
        elif idx == cnt_line - 1:
            position = line.split()
        else:
            MAP.append([int(x) for x in line.split()])
        idx += 1
    file.close()

    size_x = int(size[1])
    size_y = int(size[0])

    x = int(position[0])
    y = int(position[1])
    pos = [x, y]

    return size_x, size_y, MAP, pos, map_name


def menu():
    n, m, matrix, pacman, map_name = handle_input()
    path_ghost = None
    point = 0
    path_file = str(map_name)
    map = readFile(path_file)
    inf = getInfo(map)
    output = level4(map, inf[1], inf[0], pacman)
    point = output[0]
    path = output[1]
    path_ghost = output[2]
    # Trả về kích thước x, y, vị trí pacman, điểm, path_ghost, level
    return n, m, matrix, pacman, point, path, path_ghost


def drawFinish(state):
    text_font = pygame.font.SysFont("Arial", 36)
    if state == WIN:
        text = text_font.render("WIN", True, PACMAN_COLOR)
    else:
        text = text_font.render("LOSE", True, GHOST_COLOR)

    screen.blit(text, ((n / 2 - 1) * one_block_size, m * one_block_size))


if __name__ == "__main__":
    n, m, matrix, pacman, point, path, path_ghost = menu()

    SCREEN_HEIGHT = (m + 2) * one_block_size
    SCREEN_WIDTH = n * one_block_size
    screen, clock = initGameScreen()
    game = Game(matrix, pacman)
    game.Player.draw()
    drawScore()
    pygame.display.update()
    ghostmove = 0
    idx = 0
    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                sys.exit(0)
        for food in game.Foods:
            food.draw()
        game.clearAnimation()
        game.pacmanMove(path[idx])
        game.Player.draw()

        game.Player.DEAD = game.checkColision()
        if game.checkColision():
            for ghost in game.Ghosts:
                ghost.draw()
            break
        for path_idx in range(len(game.Ghosts)):
            path_ = path_ghost[path_idx]
            game.ghostMove(path_[idx], path_idx)
            game.Ghosts[path_idx].draw()
        game.Player.DEAD = game.checkColision()
        if game.checkColision():
            print(game.Player.DEAD)
            break

        drawScore()

        pygame.display.update()
        idx += 1

        if (idx == len(path)):
            game.Player.DEAD = game.checkColision()
            isFinsihed, state = game.checkGameFinish()
            break

        isFinsihed, state = game.checkGameFinish()
        if isFinsihed == True:
            break
        time.sleep(0.1)
        clock.tick(30)

    drawFinish(state)
    pygame.display.update()
    time.sleep(5)
    pygame.quit()
