import numpy as np
from AbstractCell import AbstractCell


class Grid():
    def __init__(self, n, m, state, global_state):
        self.populated = False
        self.global_state = global_state
        self.grid = np.array([[AbstractCell(state) for i in range(n)] for j in range(m)], dtype=object)

    def run(self):
        pass
