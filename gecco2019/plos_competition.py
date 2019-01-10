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
import itertools
import os
import pwd
import platform

import std_players
import ipd_types
from deap import tools, base, creator, algorithms
from globals import index as i
from globals import keys

from collections import defaultdict


# change this to determine the evaluation metric for testing
# SELF = 0    # self score
# WINS = 1    # number of wins
# WDL = 2     # 3 pts for win, 1 pt for draw, 0 pts for loss
# DRAWS = 3   # number of draws
# COOP = 4    # mutual cooperation score
# MUT = 5     # mutual benefit -- minimize difference between self and opp scores
# MATCH = 6   # score of most recent match
TESTING_METRIC = keys.MATCH


def run_plos():

    # creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    # creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    # creator.create("Individual", list, fitness=creator.FitnessSingle)

    # global-ish variables won't be changed
    # IND_SIZE = 70
    NUM_EACH_TYPE = 20
    NUM_EACH_EVOLVED = NUM_EACH_TYPE

    # in this competition, we count each objective pair as a separate type
    # thus, we have 21 types rather than 18
    NUM_TYPES = 21

    # at this point, we want population size to represent only the standard types
    POP_SIZE = NUM_EACH_TYPE * (NUM_TYPES - 4)
    COMPETITION_ROUNDS = 20

    TRAINING_GROUP = 'AX'

    run_info = [NUM_EACH_TYPE, NUM_TYPES, 150]

    rseed = os.getpid() * (time.time() % 4919)
    random.seed(rseed)
    print("\n\nRandom seed: {}\n".format(rseed))

    logpath = ''
    if 'comet' in platform.node():
        logpath += '/oasis/scratch/comet/'
        logpath += pwd.getpwuid(os.getuid())[0]
        logpath += '/temp_project/'

    if TRAINING_GROUP == 'POP':
        logpath += 'train_pop/'
    else:
        logpath += 'train_axelrod/'
    logpath += 'plos-'
    logpath += time.strftime("%Y%m%d-%H%M%S")
    logpath += '-{}'.format(os.getpid())
    logpath += '.log'

    fname = open(logpath, 'w')
    fname.write("\ntraining: {}\n".format(TRAINING_GROUP))
    fname.write("num of each standard type: {}\n".format(NUM_EACH_TYPE))
    fname.write("num of each evolved type: {}\n".format(NUM_EACH_EVOLVED))

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

    if TRAINING_GROUP == 'AX':
        csvfile = open('ax_during_self.csv', 'r')
    else:
        csvfile = open('pop_during_self.csv', 'r')
    reader = csv.reader(csvfile)

    # read evolved players from csv and put in population
    evolved_candidates = []
    for row in reader:
        evolved_candidates.append(row)

    # delete the preamble lines, if any
    while len(evolved_candidates[0]) < 70:
        del evolved_candidates[0]

    evolved_obj_pairs = [0] * 4
    done = False

    history = [0] * 6
    scores = [0] * 5
    stats = [0] * 3
    gradual = [0] * 6
    id = 0

    # determine if the members begin with generation or genome
    # if former, must offest indices by 1
    if int(evolved_candidates[0][1]) > 1:
        base = 1
    else:
        base = 0

    while not done:
        ind = random.randint(0, len(evolved_candidates) - 1)
        pair = int(evolved_candidates[ind][79 + base])
        p_type = int(evolved_candidates[ind][80 + base]) + pair
        if evolved_obj_pairs[pair] < NUM_EACH_EVOLVED:
            genome = []
            for k in range(70):
                genome.append(int(evolved_candidates[ind][k + 1 + base]))

            population.append(deepcopy([genome, history, scores, stats, pair, p_type, id, gradual]))
            evolved_obj_pairs[pair] += 1

        del evolved_candidates[ind]
        done = evolved_obj_pairs[0] == NUM_EACH_EVOLVED and evolved_obj_pairs[1] == NUM_EACH_EVOLVED and \
               evolved_obj_pairs[2] == NUM_EACH_EVOLVED and evolved_obj_pairs[3] == NUM_EACH_EVOLVED

    #
    # begin main loop for competition
    #
    types_remaining = NUM_TYPES
    rounds = 0
    all_equal = -1
    equal_types = []
    while types_remaining > 1:
        random.shuffle(population)
        print("Round: {}".format(rounds))
        fname.write("\nRound: {}\n".format(rounds))
        print "  ",
        fname.write("  ")
        print('{}\n'.format('{:3d}' * len(type_counts)).format(*type_counts))
        fname.write('{}\n\n'.format('{:3d}' * len(type_counts)).format(*type_counts))

        # num_evolved = type_counts[len(type_counts) - 1]

        # play round robin
        for pair in itertools.combinations(population, r=2):
            if pair[0][i.type] != pair[1][i.type]:
                std_players.playMultiRounds(*pair)

        type_counts = [0] * NUM_TYPES
        type_sum_score = [0] * NUM_TYPES

        # get count of each player type
        # and sum the scores for each type
        for m in population:
            type_counts[m[i.type]] += 1
            type_sum_score[m[i.type]] += m[i.scores][i.self]

        # check if scores for all remaining types are equal
        if len(set(type_sum_score)) <= 2:
            print("   All remaining types equal.\n")
            fname.write("   All remaining types equal.\n\n")
            if all_equal == -1:
                all_equal = rounds
                for j in range(len(type_sum_score)):
                    if type_sum_score[j] > 0:
                        equal_types.append(j)

        # # normalize the summed scores by number of members
        # for k in range(len(type_sum_score)):
        #     if type_counts[k] == 0:
        #         type_sum_score[k] = 0
        #     else:
        #         type_sum_score[k] = type_sum_score[k]/type_counts[k]

        # find the strategy with the lowest score
        index = -1
        for k in range(len(type_sum_score)):
            if index == -1:
                if type_counts[k] > 0:
                    index = k
            else:
                if type_counts[k] > 0 and type_sum_score[k] < type_sum_score[index]:
                    index = k

        k = 0
        while k < len(population):
            if population[k][i.type] == index:
                del population[k]
            else:
                k += 1

        exit_order.append(std_players.std_types[index])

        type_counts[index] = 0
        # type_counts = [0] * NUM_TYPES
        # for m in population:
        #     type_counts[m[i.type]] += 1

        types_remaining -= 1

        print "  ",
        print("{}\n".format(type_sum_score))
        fname.write("  ")
        fname.write("{}\n\n".format(type_sum_score))

        # reset scores
        for k in range(len(population)):
            std_players.reset_scores(population[k])

        rounds += 1

    #
    # end main loop
    #

    # timestr = 'logs/'
    # timestr += time.strftime("%Y%m%d-%H%M%S")
    # timestr += '-{}'.format(os.getpid())
    # timestr += '.csv'
    # deapplaygame.exportGenometoCSV(timestr, all_ind, run_info, test_pops, test_labels, best_tested)


    # deapplaygame.plotbestplayers(best_players, training_group=TRAINING_GROUP, filename=filename)

    csvfile.close()

    # for m in population:
    #     print m

    winner = type_counts.index(max(type_counts))
    print("\n\nEnd of run:\n")
    print("  Winner: {}: {}\n".format(winner, std_players.std_types[winner]))
    fname.write("\n  Winner: {}: {}\n\n".format(winner, std_players.std_types[winner]))
    print("  Type counts:")
    print "  ",
    fname.write("  Type counts:\n  ")
    print('{}\n'.format('{:3d}' * len(type_counts)).format(*type_counts))
    fname.write('{}\n\n'.format('{:3d}' * len(type_counts)).format(*type_counts))
    print('  Round when all equal: {}'.format(all_equal))
    print('  Types: {}\n'.format(equal_types))
    fname.write('  Round when all equal {}\n'.format(all_equal))
    fname.write('  Types: {}\n\n'.format(equal_types))
    print("  Order of elimination:")
    fname.write("  Order of elimination:\n")
    print("    {}\n".format(exit_order))
    fname.write("    {}\n\n".format(exit_order))
    print("  Objective pairs represented:")
    fname.write("  Objective pairs represented:\n")
    print("    {}\n".format(evolved_obj_pairs))
    fname.write("    {}\n\n".format(evolved_obj_pairs))

    fname.close()

if __name__ == "__main__":
    run_plos()
