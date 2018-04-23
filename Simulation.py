import random
# from scipy.stats import chi2
from AbstractCell import AbstractCell
from Intervention import Intervention, InterventionType
from SimulationGrid import SimulationGrid
from Helpers import logger
import argparse
import numpy as np
from Constants import *
import math

# import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.animation as animation





parser = argparse.ArgumentParser()
parser.add_argument('--dim', metavar='dim', type=int, nargs=1, help='Size of n x n grid')
parser.add_argument('--time', metavar='time', type=int, nargs=1, help='Number of timesteps the simulation is run for')
parser.add_argument('--masks', metavar='masks', type=int, nargs=1, help='Number of masks handed out in the simulation')
parser.add_argument('--doses', metavar='pickers', type=int, nargs=1,
                    help='Number of doses of medicine handed out in the simulation')
parser.add_argument('--vaccines', metavar='pickerqcap', type=int, nargs=1,
                    help='Number of vaccines administered in the simulation')
args = parser.parse_args()

# Handle inputs
DIM = args.dim[0] if args.dim else 100
TIME = args.time[0] if args.time else 100
N_MASKS = args.masks[0] if args.masks else 100
N_DOSES = args.doses[0] if args.doses else 10
N_VACCINES = args.vaccines[0] if args.vaccines else 10

NUM_INFECTED = 0


global logger
global curr_t

curr_t = 0


class States:
    SUSCEPTIBLE = 1
    INFECTED = 2
    RESISTANT = 3


class FluCell(AbstractCell):
    def __init__(self, position, suseptibility=None, infected_time=None, attributes=None, hasMask=None, hasDose=None,
                 hasVaccine=None):
        self.position = position
        if attributes is None:
            self.attributes = {"infected_time": infected_time,
                               "infectability": (BASE_INFECTABILITY + (MAX_INFECTABILITY - BASE_INFECTABILITY) * (
                                   1 / infected_time) if infected_time is not 0 else 0),
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

    def __repr__(self):
        return str(self.position)

    def applyIntervention(self, intervention):
        if intervention.type == InterventionType.MASK and not self.hasMask:
            self.attributes["infectability"] *= MASK_BENEFIT
        elif intervention.type == InterventionType.DOSE and not self.hasDose:
            self.attributes["infected_time"] *= DOSE_BENEFIT
        elif intervention.type == InterventionType.VACCINE and not self.hasVaccine:
            self.attributes["suseptibility"] *= VACCINE_BENEFIT

    def update(self, neighbors):
        global NUM_INFECTED
        attributes = {"suseptibility": self.attributes["suseptibility"],
                      "infectability": self.attributes["infectability"],
                      "infected_time": self.attributes["infected_time"]}
        for neighbor in neighbors:
            if attributes["infectability"] == 0 and random.random() * 10 < self.attributes["suseptibility"] * neighbor["infectability"]:
                attributes["suseptibility"] = 0
                attributes["infectability"] = BASE_INFECTABILITY
                NUM_INFECTED += 1
        if attributes["infectability"] > 0:
            attributes["infected_time"] = attributes["infected_time"] + 1
            attributes["infectability"] = BASE_INFECTABILITY + (MAX_INFECTABILITY - BASE_INFECTABILITY) * (
                1 / attributes["infected_time"])
            if self.hasMask:
                attributes["infectibility"] *= MASK_BENEFIT
            attributes["infected_time"] = attributes["infected_time"] + 1
        else:
            attributes["infectability"] = 0
            attributes["infected_time"] = 0

        return FluCell(position=self.position, attributes=attributes, hasMask=self.hasMask, hasDose=self.hasDose,
                       hasVaccine=self.hasVaccine)

    def setState(self):
        if self.attributes["infected_time"] > LENGTH_OF_DISEASE:
            self.state = States.RESISTANT
        elif self.attributes["infectability"] != 0:
            self.state = States.INFECTED
        elif self.attributes["suseptibility"] < RESISTANCE_THRESHOLD:
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
        self.ms = []
        self.float_grid = np.array([[0 for _ in range(DIM)] for __ in range(DIM)],
                              dtype=float)

        n_interventions = float(self.masks + self.doses + self.vaccines)
        n_interventions_per_ts = math.ceil(n_interventions / n_iterations)
        n_cells = self.dim ** 2
        self.intervention_prob = n_interventions_per_ts / n_cells
        if VERBOSE:
            print(self.intervention_prob)
        global grid
        self.grid = SimulationGrid((dim, dim), global_state=None)

        for row in range(dim):
            for col in range(dim):
                if random.random() < .05:
                    cell = FluCell(position=(row, col), suseptibility=0, infected_time=1)
                else:
                    cell = FluCell(position=(row, col), suseptibility=np.random.uniform(low=BASE_SUSCEPTABILITY - 0.1,
                                                                                        high=BASE_SUSCEPTABILITY + 0.1),
                                   infected_time=0)
                self.grid.populate(location=(row, col), cell=cell)

        self.interventions = []
        for _ in range(self.masks):
            self.interventions.append(Intervention(InterventionType.MASK, MASK_COST))
        for _ in range(self.doses):
            self.interventions.append(Intervention(InterventionType.DOSE, DOSE_COST))
        for _ in range(self.vaccines):
            self.interventions.append(Intervention(InterventionType.VACCINE, VACCINE_COST))
        np.random.shuffle(self.interventions)

    def update(self, _):
        global curr_t
        # Apply interventions probabilistically
        infected = 0
        newly_infected = 0
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                if len(self.interventions) > 0 and random.random() < self.intervention_prob:
                    cell = self.grid.grid[row][col]
                    intervention = self.interventions[-1]
                    if VERBOSE:
                        print 'Applying intervention %s to Cell %s' % (intervention, cell.position)
                    if intervention.type == InterventionType.MASK:
                        self.masks_used += 1
                    elif intervention.type == InterventionType.DOSE:
                        self.doses_used += 1
                    elif intervention.type == InterventionType.VACCINE:
                        self.vaccines_used += 1
                    cell.applyIntervention(intervention)
                    self.interventions = self.interventions[:-1]

        # Propagate neighbor states
        new_grid = SimulationGrid((self.grid.rows, self.grid.rows), global_state=None)
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                cell = self.grid.grid[row][col]
                neighbors = self.grid.get_neighbors(row, col)
                new_grid.grid[row][col] = cell.update(neighbors)
                if new_grid.grid[row][col].state == States.INFECTED:
                    infected += 1
                    if self.grid.grid[row][col].state != States.INFECTED:
                        newly_infected += 1

        self.grid = new_grid
        if VERBOSE:
            print(infected)
            print(newly_infected)
        # self.fgrid()
        return newly_infected

    # def fgrid(self):
    #     for i in range(DIM):
    #         for j in range(DIM):
    #             self.float_grid[i][j] = self.grid.grid[i][j].state - 2
    #     mat.set_array(self.float_grid)

    def run(self):
        global curr_t
        num_infected = 0
        for _ in range(self.n_iterations):
            if VERBOSE:
                print '\nTIMESTEP: %d' % curr_t
            num_infected += self.update(curr_t)

            state_matrix = [[self.grid.grid[r][c].state-2 for c in range(len(self.grid.grid[r])) ] for r in range(len(self.grid.grid))]
            self.ms.append(state_matrix)

            if VERBOSE:
                logger.print_log(curr_t)
            curr_t += 1
        return num_infected/float(self.n_iterations)

    def animate(self, i):
        print(i)
        mat.set_data(self.ms[i])
        return [mat]


if __name__ == '__main__':
    sim = Simulation(DIM, TIME, N_MASKS, N_DOSES, N_VACCINES)
    sim.run()
    print(sim.intervention_prob)
    print(NUM_INFECTED)

    fig, ax = plt.subplots()
    mat = ax.matshow(sim.ms[0])
    ani = animation.FuncAnimation(fig, sim.animate, frames=range(1,sim.n_iterations), interval=1)
    plt.show()
