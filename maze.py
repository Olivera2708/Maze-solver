import numpy as np
from PIL import Image
from collections import deque


class Maze:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.data = np.full((height, width), '', dtype=str)
        self.teleports = []
        self.enterences = []

    def load(self, image):
        for i in range(self.height):
            for j in range(self.width):
                if image[i, j, 0] == 0:
                    self.data[i, j] = 'b'
                else:
                    self.data[i, j] = 'w'

    def load_teleports(self, teleports):
        self.teleports = teleports
        for teleport in teleports:
            self.data[teleport[0], teleport[1]] = 't'

    def find_enterences(self):
        start1 = None
        start2 = None
        for i in range(self.width):
            if self.data[0, i] == 'w' and start1 is None:
                start1 = (0, i)
            elif self.data[0, i] == 'b' and start1 is not None:
                self.enterences.append([start1, (0, i-1)])
                start1 = None
            elif start1 is not None and i == self.width-1:
                self.enterences.append([start1, (0, i)])
            
            if self.data[self.height-1, i] == 'w' and start2 is None:
                start2 = (self.height-1, i)
            elif self.data[self.height-1, i] == 'b' and start2 is not None:
                self.enterences.append([start2, (self.height-1, i-1)])
                start2 = None
            elif start2 is not None and i == self.width-1:
                self.enterences.append([start2, (self.height-1, i)])

        start1 = None
        start2 = None
        for i in range(self.height):
            if self.data[i, 0] == 'w' and start1 is None:
                start1 = (i, 0)
            elif self.data[i, 0] == 'b' and start1 is not None:
                self.enterences.append([start1, (i-1, 0)])
                start1 = None
            elif start1 is not None and i == self.height-1:
                self.enterences.append([start1, (i, 0)])

            if self.data[i, self.width-1] == 'w' and start2 is None:
                start2 = (i, self.width-1)
            elif self.data[i, self.width-1] == 'b' and start2 is not None:
                self.enterences.append([start2, (i-1, self.width-1)])
                start2 = None
            elif start2 is not None and i == self.height-1:
                self.enterences.append([start2, (i, self.width-1)])

    def manhattan_distance(self, current, goal):
        return abs(current[0] - goal[0]) + abs(current[1] - goal[1])
    
    def legal_position(self, new_a, new_b):
        return 0 <= new_a < self.height and 0 <= new_b < self.width and self.data[new_a, new_b] != 'b'
    
    def get_legal_positions(self, current_position):
        actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        positions = []
        for a, b in actions:
            new_a = current_position[0] + a
            new_b = current_position[1] + b
            if self.legal_position(new_a, new_b):
                positions.append(tuple([new_a, new_b]))
        return positions
    
    def is_between(self, point, start, end):
        x1, y1 = start
        x2, y2 = end
        x, y = point
        return min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2)
    
    def is_end(self, position, start):
        for enterence in self.enterences:
            if self.is_between(position, enterence[0], enterence[1]) and not self.is_between(start, enterence[0], enterence[1]):
                return True
        return False
    
    def search(self, enterence, include_teleports):
        start_between = [(x, y) for x in range(enterence[0][0], enterence[1][0] + 1) for y in range(enterence[0][1], enterence[1][1] + 1)]
        start = enterence[0]
        frontier = deque([start])
        processed = np.zeros((height, width), dtype=bool)
        distances = np.full((self.height, self.width), -1, dtype=int)
        distances[start] = 1

        while len(frontier) > 0:
            current_position = frontier.popleft()
            processed[current_position] = True

            if include_teleports and list(current_position) in self.teleports:
                return distances[current_position]
            
            if not include_teleports and self.is_end(current_position, start):
                return distances[current_position]

            for new_position in self.get_legal_positions(current_position):
                if new_position in start_between:
                    if new_position in frontier:
                        distances[new_position] = 1
                    elif not processed[new_position]:
                        frontier.append(new_position)
                        distances[new_position] = 1
                else:
                    if new_position in frontier:
                        if distances[current_position] + 1 < distances[new_position]:
                            distances[new_position] = distances[current_position] + 1
                    elif not processed[new_position]:
                        frontier.append(new_position)
                        distances[new_position] = distances[current_position] + 1
        return -1
    

def load_teleports():
    teleports = []
    n = int(input())
    for _ in range(n):
        coordinates = input().split(" ")
        coordinates = [int(c) for c in coordinates]
        teleports.append(coordinates)
    return teleports

if __name__ == "__main__":
    image_path = input()
    image = np.array(Image.open(image_path))
    teleports = load_teleports()

    height, width, _ = image.shape
    maze = Maze(height, width)
    maze.load(image)

    #A
    maze.find_enterences()
    print(len(maze.enterences))

    #B
    shortest_path = float('inf')
    for i in range(int(len(maze.enterences))-1):
        new_path = maze.search(maze.enterences[i], False)
        if new_path != -1:
            shortest_path = min(shortest_path, new_path)
    
    if shortest_path == float('inf'):
        shortest_path = -1
    print(shortest_path)

    #C
    teleport_distances = []
    if len(teleports) > 1:
        maze.load_teleports(teleports)
        shortest_path_teleports = float('inf')
        for i in range(int(len(maze.enterences))):
            teleport_distances.append(maze.search(maze.enterences[i], True))
        teleport_distances = [x for x in teleport_distances if x != -1]
        teleport_distances.sort()
        if len(teleport_distances) > 1 and teleport_distances[0] + teleport_distances[1] < shortest_path:
            print(teleport_distances[0] + teleport_distances[1])
        else:
            print(shortest_path)
    else:
        print(shortest_path)