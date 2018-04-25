"""
Defines the Cellular Automata grid and provides utilities for finding the neighborhood and populating the grid.
"""

from collections import defaultdict
import numpy as np

from Constants import VERBOSE
from Helpers import logger

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
        if VERBOSE:
            print ('Populating grid at location (%s, %s)' % (row, col))
        self.grid[row][col] = cell

    #Check all 8 neighbors of each cell and append their attributes to array, accounting for cells on the edge of grid   
    def get_neighbors(self, row, col):
        neighbors = []
        left, right, up, down = False, False, False, False
        if col > 0:
            left = True
            neighbors.append(self.grid[row][col - 1].attributes)
        if row > 0:
            up = True
            neighbors.append(self.grid[row - 1][col].attributes)
        if col < self.rows - 1:
            right = True
            neighbors.append(self.grid[row][col + 1].attributes)
        if row < self.cols - 1:
            down = True
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