#
# Implementation of an Evolutionary Competition.  It begins with an equal number
# of some number of each of Axelrod's players and our best players.  Play a round
# robin.  Then evaluate the success of each strategy.  For the next round, each
# strategy is assigned a number of members proportional to its success.  The strategy
# with the most members at the end is the winner.
#

import time
# import numpy as np
import random
import csv
from copy import deepcopy
import itertools
import os
import platform
import pwd
from collections import defaultdict

from deap import tools, base, creator, algorithms
import deapplaygame2 as dpg
import std_players
from globals import index as i
from globals import keys, REP, HIST3, HIST6
import ipd_types

# change this to determine the evaluation metric for testing
# SELF = 0    # self score
# WINS = 1    # number of wins
# WDL = 2     # 3 pts for win, 1 pt for draw, 0 pts for loss
# DRAWS = 3   # number of draws
# COOP = 4    # mutual cooperation score
# MUT = 5     # mutual benefit -- minimize difference between self and opp scores
# MATCH = 6   # score of most recent match
TESTING_METRIC = keys.SELF

main_run = False


def run_rr(t_group=None, num_each=None, num_evolved=None):

    # creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    # creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    # creator.create("Individual", list, fitness=creator.FitnessSingle)

    # global-ish variables won't be changed
    # IND_SIZE = 70

    if t_group is not None:
        TRAINING_GROUP = t_group
    else:
        TRAINING_GROUP = 'POP'

    if TRAINING_GROUP == 'AX':
        in_filename = 'newreps_trained_axelrod/rep3_axelrod_no-noise_5k/rep3_axelrod_no-noise_5k_best-during_selfscore.csv'
    else:
        in_filename = 'newreps_trained_pop/rep1_pop_no-noise_5k/rep1_pop_no-noise_5k_best-during_selfscore.csv'

    if num_each is not None:
        NUM_EACH_TYPE = num_each
    else:
        NUM_EACH_TYPE = 10

    if num_evolved is not None:
        NUM_EACH_EVOLVED = num_evolved
    else:
        NUM_EACH_EVOLVED = 10

    NUM_TYPES = 21
    POP_SIZE = NUM_EACH_TYPE * (NUM_TYPES - 4)

    run_info = [NUM_EACH_TYPE, NUM_TYPES, 150]

    rseed = int(os.getpid() * (time.time() % 4919))
    random.seed(rseed)
    # print("\n\nRandom seed: {}\n".format(rseed))

    toolbox = ipd_types.make_types()

    toolbox.register("population", tools.initRepeat, list, toolbox.indv_single)

    population = toolbox.population(n=POP_SIZE)

    # place the fixed strategy players (standard players) in population
    type_counts = [NUM_EACH_TYPE] * NUM_TYPES
    std_players.init_pop(population, type_counts)

    csvfile = open(in_filename, 'r')
    reader = csv.reader(csvfile)

    # read evolved players from csv and put in population
    evolved_candidates = []
    for row in reader:
        # remove blank cell at beginning of row
        row.pop(0)
        # cast the individual strings to numeric types
        n_line = [float(x) if '.' in x else int(x) for x in row]

        evolved_candidates.append(n_line)

    csvfile.close()

    # list of counts of number of each objective pair added to population
    evolved_obj_pairs = [0] * 4

    # elements to be added to the individuals
    if REP in HIST3:
        history = [0] * 3
    else:
        history = [0] * 6
    scores = [0] * 5
    stats = [0] * 3
    gradual = [0] * 6
    ident = 0
    state = 0

    # determine if the members begin with generation or genome
    # if former, must offest indices by 1
    # if int(evolved_candidates[0][1]) > 1:
    #     base = 1
    # else:
    #     base = 0

    if REP == 0 or REP == 3:
        pair_index = 78
        g_len = 70
    elif REP == 1 or REP == 2:
        pair_index = 19
        g_len = 11
    else:
        pair_index = 73
        g_len = 65
        
    done = False
    while not done:
        index = random.randint(0, len(evolved_candidates) - 1)
        indiv = evolved_candidates.pop(index)
        pair = indiv[pair_index]
        p_type = indiv[pair_index + 1] + pair
        # print('pair: {}   type: {}'.format(pair, p_type))
        if evolved_obj_pairs[pair] < NUM_EACH_EVOLVED:
            genome = indiv[0:g_len]
            # for k in range(70):
            #     genome.append(int(evolved_candidates[ind][k + 1 + base]))

            population.append(deepcopy([genome, history, scores, stats, pair, p_type, ident, gradual, state]))
            evolved_obj_pairs[pair] += 1

        done = evolved_obj_pairs[0] == NUM_EACH_EVOLVED and evolved_obj_pairs[1] == NUM_EACH_EVOLVED and \
               evolved_obj_pairs[2] == NUM_EACH_EVOLVED and evolved_obj_pairs[3] == NUM_EACH_EVOLVED

    # play round robin
    for pair in itertools.combinations(population, r=2):
        if pair[0][i.type] != pair[1][i.type]:
            std_players.playMultiRounds(*pair)

    sorted_pop = sorted(population, key=lambda m: dpg.sort_key(m, TESTING_METRIC), reverse=True)

    # print("\n\nEnd of run:\n")

    if main_run:
        print("Evolved member pairs: {}\n".format(evolved_obj_pairs))
        for member in sorted_pop:
            print("{}\n".format(member))

    logpath = ''
    if 'comet' in platform.node():
        logpath += '/oasis/scratch/comet/'
        logpath += pwd.getpwuid(os.getuid())[0]
        logpath += '/temp_project/'

    if TRAINING_GROUP == 'POP':
        logpath += 'train_pop/'
    else:
        logpath += 'train_axelrod/'
    logpath += 'rr-rep{}-'.format(REP)
    logpath += time.strftime("%Y%m%d-%H%M%S")
    logpath += '-{}'.format(os.getpid())
    logpath += '.csv'

    with open(logpath, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["training: " + TRAINING_GROUP])
        writer.writerow(["population: " + str(POP_SIZE)])
        writer.writerow(["number each pair: "])
        writer.writerow(["  " + str(x) for x in evolved_obj_pairs])
        writer.writerow("")

        for member in sorted_pop:
            writer.writerow([''] + \
                            member[i.genome] + \
                            [float(member[i.scores][i.self]) / member[i.scores][i.games]] + \
                            [float(member[i.scores][i.opp]) / member[i.scores][i.games]] + \
                            # [ min(6* float(member[3])/member[4], COOPERATION_MAX)] +    \
                            [float(member[i.scores][i.coop]) / member[i.scores][i.games]] + \
                            [member[i.scores][i.games]] + \
                            [member[i.pair]] + \
                            [member[i.type]])

    return sorted_pop


if __name__ == "__main__":
    main_run = True
    run_rr()
