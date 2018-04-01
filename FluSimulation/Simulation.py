import random
from GridSimulation.AbstractCell import AbstractCell
from GridSimulation.SimulationGrid import SimulationGrid
import argparse

class States:
    SUSCEPTIBLE = 1
    INFECTED = 2
    RESISTANT = 3

class InterventionType:
    MASK = 0
    DOSE = 1
    VACCINE = 2

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

class Simulation:

    def __init__(self, dim, n_iterations, masks, doses, vaccines):
        self.dim = dim
        self.n_iterations = n_iterations
        self.masks = masks
        self.doses = doses
        self.vaccines = vaccines

        self.grid = SimulationGrid((dim, dim), global_state=None)
        for row in range(dim):
            for col in range(dim):
                cell = FluCell(States.SUSCEPTIBLE, [])
                if random.random() < .05:
                    cell.state = States.INFECTED
                self.grid.populate(location=(row, col), cell=cell)

        self.interventions = []

    def update(self):
        # Propagate neighbor states

        # new_grid = np.array([[object() for _ in range(self.cols)] for __ in range(self.rows)],
        #                     dtype=object)
        # for row in range(self.rows):
        #     for col in range(self.cols):
        #         neighboring_states = self.calculate_neighbors(row, col)
        #         new_grid[row][col] = self.grid[row][col].update(neighboring_states)
        # self.grid = new_grid

        # Update interventions list

    def run(self):
        for _ in range(self.n_iterations):
            self.update()

parser = argparse.ArgumentParser()
parser.add_argument('--dim', metavar='dim', type=int, nargs=1, help='Size of n x n grid')
parser.add_argument('--time', metavar='time', type=int, nargs=1, help='Number of timesteps the simulation is run for')
parser.add_argument('--masks', metavar='masks', type=int, nargs=1, help='Number of masks handed out in the simulation')
parser.add_argument('--doses', metavar='pickers', type=int, nargs=1, help='Number of doses of medicine handed out in the simulation')
parser.add_argument('--vaccines', metavar='pickerqcap', type=int, nargs=1, help='Number of vaccines administered in the simulation')
args = parser.parse_args()

# Handle inputs
DIM = args.dim[0] if args.dim else 100
TIME = args.time[0] if args.time else 100
N_MASKS = args.masks[0] if args.masks else 20
N_DOSES = args.doses[0] if args.doses else 20
N_VACCINES = args.vaccines[0] if args.vaccines else 20

sim = Simulation(DIM, TIME, N_MASKS, N_DOSES, N_VACCINES)
sim.run()