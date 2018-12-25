#
# Implementation of an Evolutionary Competition.  It begins with an equal number
# of some number of each of Axelrod's players and our best players.  Play a round
# robin.  Then evaluate the success of each strategy.  For the next round, each
# strategy is assigned a number of members proportional to its success.  The strategy
# with the most members at the end is the winner.
#

import time
import numpy as np
import random
import csv
from copy import deepcopy
from deap import tools, base, creator, algorithms
import deapplaygame2 as dpg
import itertools
import os
import std_players
from globals import index as i
import ipd_types
from collections import defaultdict

# change this to determine the evaluation metric for testing
SELF = 0    # self score
WINS = 1    # number of wins
WDL = 2     # 3 pts for win, 1 pt for draw, 0 pts for loss
DRAWS = 3   # number of draws
TESTING_METRIC = SELF

# used in calls to sorted to get the sort key (rather than use a lambda function)
def sort_key(member):
    if TESTING_METRIC == SELF:
        return member[i.scores][i.self]
    elif TESTING_METRIC == WINS:
        return member[i.stats][i.win]
    elif TESTING_METRIC == WDL:
        return 3 * member[i.stats][i.win] + member[i.stats][i.draw]
    elif TESTING_METRIC == DRAWS:
        return member[i.stats][i.draw]

# used in calls to sorted to get the sort key (rather than use a lambda function)
# In this version, the member is a list containing a member of the
# population and the generation in which the member was added to
# the best_tested list.  That's the reason for the additional [0]
# index at the front of the accessors
def sort_key_best(member):
    if TESTING_METRIC == SELF:
        return member[0][i.scores][i.self]
    elif TESTING_METRIC == WINS:
        return member[0][i.stats][i.win]
    elif TESTING_METRIC == WDL:
        return 3 * member[0][i.stats][i.win] + member[0][i.stats][i.draw]
    elif TESTING_METRIC == DRAWS:
        return member[0][i.stats][i.draw]

def main():

    # creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    # creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    # creator.create("Individual", list, fitness=creator.FitnessSingle)

    # global-ish variables won't be changed
    # IND_SIZE = 70
    NUM_EACH_TYPE = 10
    NUM_TYPES = 18
    POP_SIZE = NUM_EACH_TYPE * NUM_TYPES
    COMPETITION_ROUNDS = 20

    filename = str((os.getpid() * time.time()) % 4919) + '.png'

    run_info = [NUM_EACH_TYPE, NUM_TYPES, 150]

    rseed = os.getpid() * (time.time() % 4919)
    random.seed(rseed)
    print("\n\nRandom seed: {}\n".format(rseed))

    toolbox = ipd_types.make_types()

    toolbox.register("population", tools.initRepeat, list, toolbox.indv_single)

    population = toolbox.population(n=POP_SIZE)

    # place the fixed strategy players (standard players) in population
    type_counts = [NUM_EACH_TYPE] * NUM_TYPES
    std_players.init_pop(population, type_counts)

    # keep track of the order in which strategies exit the competition
    # and the score for each strategy type
    exit_order = []
    type_sum_score = []

    csvfile = open('best-players-notrump.csv', 'r')
    reader = csv.reader(csvfile)

    # read evolved players from csv and put in population
    evolved_candidates = []
    for row in reader:
        evolved_candidates.append(row)

    evolved_obj_pairs = [0] * 4
    j = 0
    while j < NUM_EACH_TYPE:
        ind = random.randint(0, len(evolved_candidates) - 1)
        genome = []
        for k in range(70):
            genome.append(int(evolved_candidates[ind][k+1]))

        index = (NUM_TYPES - 1) * NUM_EACH_TYPE + j
        population[index][i.genome] = deepcopy(genome)
        population[index][i.type] = NUM_TYPES - 1
        population[index][i.pair] = int(evolved_candidates[ind][75])
        evolved_obj_pairs[int(evolved_candidates[ind][75])] += 1
        del evolved_candidates[ind]
        j += 1

    # play round robin
    for pair in itertools.combinations(population, r=2):
       std_players.playMultiRounds(*pair)

    sorted_pop = sorted(population, key=sort_key, reverse=True)


    # timestr = 'logs/'
    # timestr += time.strftime("%Y%m%d-%H%M%S")
    # timestr += '-{}'.format(os.getpid())
    # timestr += '.csv'
    # deapplaygame.exportGenometoCSV(timestr, all_ind, run_info, test_pops, test_labels, best_tested)


    # deapplaygame.plotbestplayers(best_players, training_group=TRAINING_GROUP, filename=filename)

    csvfile.close()

    # for m in population:
    #     print m

    print("\n\nEnd of run:\n")

    print("Evolved member pairs: {}\n".format(evolved_obj_pairs))
    for member in sorted_pop:
        print("{}\n".format(member))


if __name__ == "__main__":
    main()
