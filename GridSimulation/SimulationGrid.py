from collections import defaultdict
import numpy as np

from AbstractCell import AbstractCell


class SimulationGrid:
    def __init__(self, dims, global_state):
        self.rows, self.cols = dims
        self.populated = False
        self.global_state = global_state
        self.grid = np.array([[AbstractCell(None, None) for _ in range(self.rows)] for __ in range(self.cols)],
                             dtype=object)

    def populate(self, location, cell):
        row, col = location
        self.grid[row][col] = cell

    def calculate_neighbors(self, row, col):
        neighbors = []
        left, right, up, down = False, False, False, False
        if col == 0:
            right = True
            neighbors.append(self.grid[row][col + 1].attributes)
        if row == 0:
            down = True
            neighbors.append(self.grid[row - 1][col].attributes)
        if col == self.rows - 1:
            left = True
            neighbors.append(self.grid[row][col - 1].attributes)
        if row == self.cols - 1:
            up = True
            neighbors.append(self.grid[row + 1][col].attributes)
        if right and down:
            neighbors.append(self.grid[row + 1][col + 1].attributes)
        if left and down:
            neighbors.append(self.grid[row + 1][col - 1].attributes)
        if right and up:
            neighbors.append(self.grid[row - 1][col + 1].attributes)
        if left and up:
            neighbors.append(self.grid[row - 1][col - 1].attributes)
        return neighbors

    def iterate(self):
        new_grid = np.array([[object() for _ in range(self.cols)] for __ in range(self.rows)],
                            dtype=object)
        for row in range(self.rows):
            for col in range(self.cols):
                neighboring_states = self.calculate_neighbors(row, col)
                new_grid[row][col] = self.grid[row][col].update(neighboring_states)
        self.grid = new_grid

    def run(self, iterations):
        for _ in range(iterations):
            self.iterate()
