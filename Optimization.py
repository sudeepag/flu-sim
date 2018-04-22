import argparse
import random

import sys

from Constants import *
from Simulation import Simulation

parser = argparse.ArgumentParser()
parser.add_argument('--dim', metavar='dim', type=int, nargs=1, help='Size of n x n grid')
parser.add_argument('--time', metavar='time', type=int, nargs=1, help='Number of timesteps the simulation is run for')
args = parser.parse_args()

# Handle inputs
DIM = args.dim[0] if args.dim else 10
TIME = args.time[0] if args.time else 100

NUM_INFECTED = 0



MAX_ITERATIONS = 100

global logger
global curr_t

curr_t = 0


sim = Simulation(DIM, TIME, N_MASKS, N_DOSES, N_VACCINES)
sim.run()
print(sim.intervention_prob)
print(NUM_INFECTED)



def getNeighbor(vec):
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


def cost(vec):
    return MASK_COST * vec[0] + DOSE_COST * vec[1] + VACCINE_COST * vec[2]



def main():
    num_iteration = 0
    vec = (random.randint(0,100), random.randint(0,100), random.randint(0,100))
    best_vec = vec
    best_score = sys.maxint
    iterations_since_new_best = 0
    while num_iteration < MAX_ITERATIONS and iterations_since_new_best < 50:
        num_iteration += 1
        sim = Simulation(DIM, TIME, vec[0], vec[1], vec[2])
        cost_v = cost(vec)
        num_sick = sim.run()
        score = cost_v * num_sick
        print "Iteration #: %s, Score: %s, Cost: %s. Num sick: %s, Masks: %s, Doses: %s, Vaccines: %s" % (num_iteration, score, cost_v, num_sick, vec[0], vec[1], vec[2])
        if score < best_score:
            best_vec = vec
            best_score = score
            iterations_since_new_best = 0
        else:
            iterations_since_new_best += 1
        vec = getNeighbor(best_vec)
        num_iteration += 1
    print best_vec
    print best_score



if __name__ == '__main__':
    main()
