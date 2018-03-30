import numpy as np
import random
import getopt
from enum import Enum

State = Enum('Susceptible', 'Infected', 'Resistant')

class Grid():
  def __init__(self, n, m, state):
    self.populated = False
    self.global_state 
    self.grid = np.array([[AbstractCell(state) for i in range(n)] for j in range(m)], dtype = object)
  def run(self):
    pass