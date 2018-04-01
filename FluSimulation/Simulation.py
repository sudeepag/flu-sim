import random
from GridSimulation.AbstractCell import AbstractCell
from GridSimulation.SimulationGrid import SimulationGrid


class States:
    SUSCEPTIBLE = 1
    INFECTED = 2
    RESISTANT = 3


class FluCell(object, AbstractCell):
    def __init__(self, state, attributes):
        self.infected_time = 0
        super(FluCell, self).__init__(attributes=attributes, state=state)

    def update(self, histogram):
        if self.state is States.INFECTED:
            self.infected_time += 1
        if self.infected_time > 5:
            self.state = States.RESISTANT
        if self.state is States.SUSCEPTIBLE and histogram[States.INFECTED] > 3:
            self.state = States.INFECTED


rows, cols = DIMS = (100, 100)
grid = SimulationGrid(DIMS, global_state=None)

for row in range(rows):
    for col in range(cols):
        cell = FluCell(States.SUSCEPTIBLE, [])
        if random.random() < .05:
            cell.state = States.INFECTED
        grid.populate(location=(row, col), cell=cell)
grid.run(100)
