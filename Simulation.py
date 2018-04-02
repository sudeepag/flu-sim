import random
# from scipy.stats import chi2
from AbstractCell import AbstractCell
from Intervention import Intervention
from SimulationGrid import SimulationGrid
from Helpers import Logger
import argparse
import numpy as np

RESISTANCE_THRESHOLD = 0.1
MASK_BENEFIT = 0.5
DOSE_BENEFIT = 2
VACCINE_BENEFIT = 0.5

BASE_SUSCEPTABILITY = 0.3
BASE_INFECTABILITY = 0.3
# INFECTABILITY_MEAN = 4
MAX_INFECTABILITY = 0.6

MASK_COST = 1.0
DOSE_COST = 57.0
VACCINE_COST = 40.0

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

global logger
logger = Logger(TIME)

class States:
    SUSCEPTIBLE = 1
    INFECTED = 2
    RESISTANT = 3

class InterventionType:
    MASK = 0
    DOSE = 1
    VACCINE = 2

class FluCell(AbstractCell):
    def __init__(self, suseptibility=None, infected_time=None, attributes=None, hasMask=None, hasDose=None, hasVaccine=None):
        if attributes is None:
            self.attributes = {"infected_time": infected_time,
                           "infectability": BASE_INFECTABILITY + (MAX_INFECTABILITY - BASE_INFECTABILITY) * (1 / infected_time),
                           "suseptibility": suseptibility}
            self.hasMask = False
            self.hasDose = False
            self.hasVaccine = False
        else:
            self.attributes = attributes
            self.hasMask = hasMask
            self.hasDose = hasDose
            self.hasVaccine = hasVaccine
        self.setState()


    def applyIntervention(self, intervention):
        if intervention.type == InterventionType.MASK and not self.hasMask:
            self.attributes["infectability"] *= MASK_BENEFIT
        elif intervention.type == InterventionType.DOSE and not self.hasDose:
            self.attributes["infected_time"] *= DOSE_BENEFIT
        elif intervention.type == InterventionType.VACCINE and not self.hasVaccine:
            self.attributes["suseptibility"] *= VACCINE_BENEFIT

    def update(self, neighbors):
        attributes = {"suseptibility": None,
                      "infectabiity": None,
                      "infected_time": None}
        for neighbor in neighbors:
            if random.random() < self.attributes["suseptibility"] * neighbor["infectability"]:
                attributes["suseptibility"] = 0
                attributes["infectability"] = BASE_INFECTABILITY
        attributes["infectability"] = BASE_INFECTABILITY + (MAX_INFECTABILITY - BASE_INFECTABILITY) * (1 / attributes["infected_time"])
        if self.hasMask:
            attributes["infectibility"] *= MASK_BENEFIT
        attributes["infected_time"] = attributes["infected_time"] + (1 if attributes["infectability"] > 0 else 0)
        return FluCell(attributes, self.hasMask, self.hasDose, self.hasVaccine)

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

        n_interventions = self.masks + self.doses + self.vaccines
        n_interventions_per_ts = int(n_interventions / n_iterations)
        n_cells = self.dim ** 2
        self.intervention_prob = n_interventions_per_ts / n_cells

        self.grid = SimulationGrid((dim, dim), global_state=None)
        for row in range(dim):
            for col in range(dim):
                cell = FluCell(States.SUSCEPTIBLE, [])
                if random.random() < .05:
                    cell = FluCell(suseptibility = 0, infected_time = 1)
                else:
                    cell = FluCell(suseptibility = np.random.uniform(low=BASE_SUSCEPTABILITY - 0.1, high=BASE_SUSCEPTABILITY + 0.1))
                self.grid.populate(location=(row, col), cell=cell)

        self.interventions = []
        for _ in range(self.masks):
            self.interventions.append(Intervention(InterventionType.MASK, MASK_COST))
        for _ in range(self.doses):
            self.interventions.append(Intervention(InterventionType.DOSE, DOSE_COST))
        for _ in range(self.vaccines):
            self.interventions.append(Intervention(InterventionType.VACCINE, VACCINE_COST))
        np.random.shuffle(self.interventions)

    def update(self):

        # Apply interventions probabilistically
        for row in range(self.rows):
            for col in range(self.cols):
                if len(self.interventions) > 0 and random.random() < self.intervention_prob:
                    cell =  self.grid[row][col]
                    intervention = self.interventions[-1]
                    if intervention.type == InterventionType.MASK:
                        self.masks_used += 1
                    elif intervention.type == InterventionType.DOSE:
                        self.doses_used += 1
                    elif intervention.type == InterventionType.VACCINE:
                        self.vaccines_used += 1
                    cell.applyIntervention(intervention)
                    self.interventions = self.interventions[:-1]

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
        for curr_t in range(self.n_iterations):
            logger.log(curr_t, 'TIMESTEP: %d' % curr_t)
            self.update()
            logger.print_log(curr_t)

sim = Simulation(DIM, TIME, N_MASKS, N_DOSES, N_VACCINES)
sim.run()