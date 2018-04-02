import random
from scipy.stats import chi2
from GridSimulation.AbstractCell import AbstractCell
from GridSimulation.Intervention import Intervention
from GridSimulation.SimulationGrid import SimulationGrid
import argparse


RESISTANCE_THRESHOLD = 0.1
MASK_BENEFIT = 0.5
DOSE_BENEFIT = 2
VACCINE_BENEFIT = 0.5

BASE_INFECTABILITY = 0.3
INFECTABILITY_MEAN = 4

MASK_COST = 1.0
DOSE_COST = 57.0
VACCINE_COST = 40.0

class States:
    SUSCEPTIBLE = 1
    INFECTED = 2
    RESISTANT = 3

class InterventionType:
    MASK = 0
    DOSE = 1
    VACCINE = 2

class FluCell(object, AbstractCell):
    def __init__(self, infectibility, suseptibility):
        self.attributes = {"infected_time": 0,
                           "infectability": infectibility,
                           "suseptibility": suseptibility}
        self.hasMask = False
        self.hasDose = False
        self.hasVaccine = False
        self.setState()

    def applyIntervention(self, type):
        if type == InterventionType.MASK and not self.hasMask:
            self.attributes["infectability"] *= MASK_BENEFIT
        elif type == InterventionType.DOSE and not self.hasDose:
            self.attributes["infected_time"] *= DOSE_BENEFIT
        elif type == InterventionType.VACCINE and not self.hasVaccine:
            self.attributes["suseptibility"] *= VACCINE_BENEFIT

    def update(self, neighbors):
        for neighbor in neighbors:
            if random.random() < self.attributes["suseptibility"] * neighbor["infectability"]:
                self.attributes["suseptibility"] = 0
                self.attributes["infectability"] = BASE_INFECTABILITY
        self.attributes["infectability"] = BASE_INFECTABILITY + chi2.cdf(self.attributes["infected_time"], INFECTABILITY_MEAN)
        self.setState()

    def setState(self):
        if self.attributes["infectability"] != 0:
            self.state = States.INFECTED
        elif self.attributes["suseptibility"] < 0.2:
            self.state = States.RESISTANT
        else:
            self.state = States.SUSCEPTIBLE



class Simulation:

    def __init__(self, dim, n_iterations, masks, doses, vaccines):
        self.dim = dim
        self.n_iterations = n_iterations
        self.masks = masks
        self.doses = doses
        self.vaccines = vaccines
        self.masks_used = 0
        self.doses_used = 0
        self.vaccines_used = 0

        self.grid = SimulationGrid((dim, dim), global_state=None)
        for row in range(dim):
            for col in range(dim):
                cell = FluCell(States.SUSCEPTIBLE, [])
                if random.random() < .05:
                    cell.state = States.INFECTED
                self.grid.populate(location=(row, col), cell=cell)

        self.interventions = []

    def update(self):

        # Add interventions probabilistically
        if self.masks_used < self.masks and random.random() > 0.5:
            self.interventions.append(Intervention(InterventionType.MASK, MASK_COST))
            self.masks_used += 1
        if self.doses_used < self.doses and random.random() > 0.5:
            self.interventions.append(Intervention(InterventionType.DOSE, DOSE_COST))
            self.doses_used += 1
        if self.vaccines_used < self.vaccines and random.random() > 0.5:
            self.interventions.append(Intervention(InterventionType.VACCINE, VACCINE_COST))
            self.vaccines_used += 1

        # Apply interventions at random
        for interventions in self.interventions:
            pass

        # Propagate neighbor states
        new_grid = np.array([[object() for _ in range(self.cols)] for __ in range(self.rows)],
                            dtype=object)
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]
                neighbors = self.grid.get_neighbors(cell)
                new_grid[row][col] = cell.update(neighbors)
        self.grid = new_grid

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