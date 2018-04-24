import random
# from scipy.stats import chi2
import time

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
N_DOSES = args.doses[0] if args.doses else 100
N_VACCINES = args.vaccines[0] if args.vaccines else 100

NUM_INFECTED = 0


global logger
global curr_t

curr_t = 0


class States:
    SUSCEPTIBLE = 1
    INFECTED = 2
    RESISTANT = 3


class FluCell(AbstractCell):

    """
    FlueCell.__init__
    initializer for the FlueCell class. Has two sets of parameters based on its usage
    paramse:
        position        location of the cell in the grid
        suseptibility   how susceptible the cell is
        infected_time   how long a cell ahs been infected
        attributes      dictionary containing all of the FlueCell's attributes
        hasMask         whether the FlueCell has a mask
        hasDose         whether the FlueCell has a dose of medicine
        hasVaccine      whether the FlueCell has a vaccine
    """
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

    """
    FlueCell.applyIntervention
    Changes the attributes of the flue cell based on the intervention type
    params: 
        intervention    type of intervention to be applied to the cell
    """
    def applyIntervention(self, intervention):
        if intervention.type == InterventionType.MASK and not self.hasMask:
            self.attributes["infectability"] *= MASK_BENEFIT
            self.hasMask = True
        elif intervention.type == InterventionType.DOSE and not self.hasDose:
            self.attributes["infected_time"] += DOSE_BENEFIT
            self.hasDose = True
        elif intervention.type == InterventionType.VACCINE and not self.hasVaccine:
            self.attributes["suseptibility"] *= VACCINE_BENEFIT
            self.hasVaccine = True

    """
    FlueCell.Update:
    calculates the new values of the attributes and generates a new cell based on these values
    params: 
        neighbors   array of cells neighboring the Fluecell to be updated
    returns     new FlueCell representing the updates 
    """
    def update(self, neighbors):
        global NUM_INFECTED
        attributes = {"suseptibility": self.attributes["suseptibility"],
                      "infectability": self.attributes["infectability"],
                      "infected_time": self.attributes["infected_time"]}
        for neighbor in neighbors:
            if attributes["infectability"] == 0 and 0.13 < self.attributes["suseptibility"] * neighbor["infectability"]:
                attributes["suseptibility"] = 0
                attributes["infectability"] = BASE_INFECTABILITY
                NUM_INFECTED += 1
        if attributes["infectability"] > 0:
            attributes["infected_time"] = attributes["infected_time"] + 1
            attributes["infectability"] = MAX_INFECTABILITY - MAX_INFECTABILITY/float(LENGTH_OF_DISEASE) * attributes["infected_time"]
            if self.hasMask:
                attributes["infectability"] *= MASK_BENEFIT
        else:
            attributes["infectability"] = 0
            attributes["infected_time"] = 0

        return FluCell(position=self.position, attributes=attributes, hasMask=self.hasMask, hasDose=self.hasDose,
                       hasVaccine=self.hasVaccine)

    """
    FlueCell.setState:
    updates the cells state based on its attributes
    """
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

        # Set inputs
        self.dim = dim
        self.n_iterations = n_iterations
        self.masks = masks
        self.doses = doses
        self.vaccines = vaccines

        # Create variables to track intervention measures handed out
        self.masks_used = 0
        self.doses_used = 0
        self.vaccines_used = 0

        # Stores all the state matrices for the animation
        self.ms = []

        # Calculate the probability of apply an intervention
        n_interventions = float(self.masks + self.doses + self.vaccines)
        n_interventions_per_ts = math.ceil(n_interventions / n_iterations)
        n_cells = self.dim ** 2
        self.intervention_prob = n_interventions_per_ts / n_cells
        if VERBOSE:
            print(self.intervention_prob)
        
        # Randomly populate the grid initially
        global grid
        self.grid = SimulationGrid((dim, dim), global_state=None)
        for row in range(dim):
            for col in range(dim):
                if random.random() < .003:
                    cell = FluCell(position=(row, col), suseptibility=0, infected_time=1)
                else:
                    cell = FluCell(position=(row, col), suseptibility=np.random.uniform(low=BASE_SUSCEPTABILITY - 0.05,
                                                                                        high=BASE_SUSCEPTABILITY + 0.05),
                                   infected_time=0)
                self.grid.populate(location=(row, col), cell=cell)

        # Populate list of intervention measures to be applied during simulation
        self.interventions = []
        for _ in range(self.masks):
            self.interventions.append(Intervention(InterventionType.MASK, MASK_COST))
        for _ in range(self.doses):
            self.interventions.append(Intervention(InterventionType.DOSE, DOSE_COST))
        for _ in range(self.vaccines):
            self.interventions.append(Intervention(InterventionType.VACCINE, VACCINE_COST))
        np.random.seed(42)
        np.random.shuffle(self.interventions)

    """ Simulation.Update
    Update the simulation for a timestep by applying interventions and propagating cell states
    returns: number of people infected in this time step
    """
    def update(self, _):

        global curr_t

        # Apply interventions probabilistically
        infected = 0
        newly_infected = 0
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                if len(self.interventions) > 0 and random.random() < 0.4:
                    cell = self.grid.grid[row][col]
                    intervention = self.interventions[-1]
                    if VERBOSE:
                        print 'Applying intervention %s to Cell %s' % (intervention, cell.position)
                    if intervention.type == InterventionType.MASK and not cell.hasMask:
                        self.masks_used += 1
                        cell.applyIntervention(intervention)
                        self.interventions = self.interventions[:-1]
                    elif intervention.type == InterventionType.DOSE and not cell.hasDose:
                        self.doses_used += 1
                        cell.applyIntervention(intervention)
                        self.interventions = self.interventions[:-1]
                    elif intervention.type == InterventionType.VACCINE and cell.state == States.SUSCEPTIBLE and not cell.hasVaccine:
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

        # Update the grid to the new grid
        self.grid = new_grid
        if VERBOSE:
            print(infected)
            print(newly_infected)

        return newly_infected

    """ Simulation.Run
        Runs the simulation and generates the state matrix at each time step
        returns: score for this simulation
    """
    def run(self):
        global curr_t
        num_infected = 0
        for _ in range(self.n_iterations):
            if VERBOSE:
                print '\nTIMESTEP: %d' % curr_t
            num_infected += self.update(curr_t)

            state_matrix = [[self.grid.grid[r][c].state for c in range(len(self.grid.grid[r])) ] for r in range(len(self.grid.grid))]
            self.ms.append(state_matrix)

            if VERBOSE:
                logger.print_log(curr_t)
            curr_t += 1
        return num_infected/float(self.n_iterations)

    """ Simulation.animate
        Returns the state matrix for the given index
        params: 
            i    index of the animation
        returns: state matrix for given index
    """
    def animate(self, i):
        print(i)
        mat.set_data(self.ms[i])
        time.sleep(0.1)
        return [mat]


if __name__ == '__main__':

    # Create and run the simulation
    sim = Simulation(DIM, TIME, N_MASKS, N_DOSES, N_VACCINES)
    sim.run()
    print(sim.intervention_prob)
    print(NUM_INFECTED)
    print "masks used: %s Doses used: %s Vaccines used: %s" % (sim.masks_used, sim.doses_used, sim.vaccines_used)

    # Create the animation for the visualization
    fig, ax = plt.subplots()
    mat = ax.matshow(sim.ms[0])
    ani = animation.FuncAnimation(fig, sim.animate, frames=range(1,sim.n_iterations), blit=True)
    plt.show()
