import argparse
import random

import sys

from Constants import *
from Simulation import Simulation

global logger
global curr_t

curr_t = 0

class Optimizer():

    def __init__(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('--dim', metavar='dim', type=int, nargs=1, help='Size of n x n grid')
        parser.add_argument('--time', metavar='time', type=int, nargs=1, help='Number of timesteps the simulation is run for')
        args = parser.parse_args()

        # Handle inputs
        self.DIM = args.dim[0] if args.dim else 10
        self.TIME = args.time[0] if args.time else 100
        self.NUM_INFECTED = 0
        self.MAX_ITERATIONS = 100
        

    # sim = Simulation(DIM, TIME, N_MASKS, N_DOSES, N_VACCINES)
    # sim.run()
    # print(sim.intervention_prob)
    # print(NUM_INFECTED)
    """
    Optimizer.getNeighbor
    neighbor function for the random hill climb optimizer
    params:
        vec    A vector representing the number of each intervention measure to search around
    returns:
        neighbor vector with the new number of each intervention measure
    """
    def getNeighbor(self, vec):
        random.seed()
        masks = vec[0]
        masks += random.randint(0, 2 * NEIGHBORHOOD_SIZE) - NEIGHBORHOOD_SIZE
        if masks < 0:
            masks = 0
        dose = vec[1]
        dose += random.randint(0, 2 * NEIGHBORHOOD_SIZE) - NEIGHBORHOOD_SIZE
        if dose < 0:
            dose = 0
        vaccine = vec[2]
        vaccine += random.randint(0, 2 * NEIGHBORHOOD_SIZE) - NEIGHBORHOOD_SIZE
        if vaccine < 0:
            vaccine = 0
        return (masks, dose, vaccine)


    """
    Optimizer.cost
    The monetary cost of the combination of intervention measures
    params: 
        vec    Number of intervention measures to be evaluated
    returns:
        float cost of the given combination of intervention measures
    """
    def cost(self, vec):
        return MASK_COST * vec[0] + DOSE_COST * vec[1] + VACCINE_COST * vec[2]


    """
    Optimizer.optimize
    params:
        dim    the size of the grid to optimize against
    returns:
        a tuple of the best number of intervention measures and the overall score
    """
    def optimize(self, dim=None):
        num_iteration = 0
        random.seed()
        if not dim: dim = self.DIM
        vec = (random.randint(0,10*self.DIM), random.randint(0,10*self.DIM), random.randint(0,10*self.DIM))
        best_vec = vec
        best_score = sys.maxint
        iterations_since_new_best = 0
        while num_iteration < self.MAX_ITERATIONS and iterations_since_new_best < 50:
            num_iteration += 1
            sim = Simulation(self.DIM, self.TIME, vec[0], vec[1], vec[2])
            cost_v = self.cost(vec)
            num_sick = sim.run()
            score = cost_v * num_sick
            # print "Iteration #: %s, Score: %s, Cost: %s. Num sick: %s, Masks: %s, Doses: %s, Vaccines: %s" % (num_iteration, score, cost_v, num_sick, vec[0], vec[1], vec[2])
            if score < best_score:
                best_vec = vec
                best_score = score
                iterations_since_new_best = 0
            else:
                iterations_since_new_best += 1
            vec = self.getNeighbor(best_vec)
            num_iteration += 1
        print best_vec
        print best_score
        return (best_vec, best_score)


    """
    Optimizer.run
    runs a single test of the simulation
    params:
        masks    number of masks to be used
        doses    number of doses of medicine to be used
        vaccines number of vaccines to be used
    """
    def run(self, masks=10, doses=10, vaccines=10):
        random.seed()
        sim = Simulation(self.DIM, self.TIME, masks, doses, vaccines)
        cost_v = self.cost((masks, doses, vaccines))
        num_sick = sim.run()
        score = cost_v * num_sick
        # print "Score: %s, Cost: %s. Num sick: %s, Masks: %s, Doses: %s, Vaccines: %s" % (score, cost_v, num_sick, masks, doses, vaccines)
        # print "masks used: %s Doses used: %s Vaccines used: %s" % (sim.masks_used, sim.doses_used, sim.vaccines_used)
        return num_sick

if __name__ == '__main__':
    # Optimizer().optimize()
    Optimizer().run()
