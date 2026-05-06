import numpy as np

class KnowledgeBase:
    def __init__(self, maze_rows, maze_cols):
        self.maze_rows = maze_rows
        self.maze_cols = maze_cols
        self.walls = set()
        self.visited = set()
        self.target = None

    def tell_from_matrix(self, matrix):
        for row in range(len(matrix)):
            for col in range(len(matrix[row])):
                if matrix[row][col] == 1:
                    self.walls.add((row, col))
                elif matrix[row][col] == 2:
                    self.target = (row, col)

    def tell_visited(self, coord):
        self.visited.add(coord)

    def is_within_bounds(self, coord):
        row, col = coord
        return 0 <= row < self.maze_rows and 0 <= col < self.maze_cols

    def is_safe(self, coord):
        return self.is_within_bounds(coord) and coord not in self.walls

    def is_visited(self, coord):
        return coord in self.visited

    def get_neighbors(self, coord):
        row, col = coord
        return {
            "North": (row - 1, col), "South": (row + 1, col),
            "East":  (row, col + 1), "West":  (row, col - 1)
        }

    def infer_safe_moves(self, coord):
        return [(d, c) for d, c in self.get_neighbors(coord).items() if self.is_safe(c)]

    def infer_unvisited_safe_moves(self, coord):
        return [m for m in self.infer_safe_moves(coord) if not self.is_visited(m[1])]