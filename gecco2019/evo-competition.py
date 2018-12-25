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
import ipd_types

from collections import defaultdict


def main():

    # creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    # creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    # creator.create("Individual", list, fitness=creator.FitnessSingle)

    # global-ish variables won't be changed
    # IND_SIZE = 70
    NUM_EACH_TYPE = 40
    NUM_TYPES = 18
    POP_SIZE = NUM_EACH_TYPE * NUM_TYPES
    COMPETITION_ROUNDS = 20

    filename = str((os.getpid() * time.time()) % 4919) + '.png'

    run_info = [NUM_EACH_TYPE, NUM_TYPES, 150]

    rseed = os.getpid() * (time.time() % 4919)
    random.seed(rseed)
    print("\n\nRandom seed: {}\n".format(rseed))

    # toolbox = base.Toolbox()
    # toolbox.register("attr_int", random.randint, 0, 0)
    # toolbox.register("bit", random.randint, 0, 1)
    # toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)
    #
    # # history bits:
    # #   xyxyxy
    # #   each xy is: opp_decision self_decision
    # #   left pair is oldest, right is most recent
    # toolbox.register("history", tools.initRepeat, list, toolbox.bit, 6)
    #
    # # fields in scores:
    # #   0: self score
    # #   1: opponent score
    # #   2: cooperation score
    # #   3: number of games
    # #   4: score this match (each match is some number of games)
    # toolbox.register("scores", tools.initRepeat, list, toolbox.attr_int, 5)
    #
    # # fields in stats:
    # #   0: matches won
    # #   1: matches drawn
    # #   2: matches lost
    # toolbox.register("stats", tools.initRepeat, list, toolbox.attr_int, 3)
    #
    # # fields for gradual players:
    # #   0: opponent last play
    # #   1: opponent defects
    # #   2: defect flag
    # #   3: self consecutive defects
    # #   4: coop flag
    # #   5: coop count
    # toolbox.register("gradual", tools.initRepeat, list, toolbox.attr_int, 6)
    #
    # # fields in individual:
    # #   0: genome
    # #   1: history (last 3 moves -- history in genome is only for start of game)
    # #   2: scores
    # #   3: stats
    # #   4: objective pair
    # #   5: player type
    # #   6: id
    # #   7: gradual fields (for gradual players only)
    # toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.history,
    #                                 toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int,
    #                                 toolbox.attr_int, toolbox.gradual), n=1)

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
        i = 0
        genome = []
        for i in range(70):
            genome.append(int(evolved_candidates[ind][i+1]))

        index = (NUM_TYPES - 1) * NUM_EACH_TYPE + j
        population[index][i.genome] = deepcopy(genome)
        population[index][i.type] = NUM_TYPES - 1
        evolved_obj_pairs[int(evolved_candidates[ind][75])] += 1
        del evolved_candidates[ind]
        j += 1

    #
    # begin main loop for competition
    #
    types_remaining = NUM_TYPES
    rounds = 0
    while types_remaining > 1:
        random.shuffle(population)
        print("Round: {}".format(rounds))
        print "  ",
        print('{}\n'.format('{:4d}' * len(type_counts)).format(*type_counts))

        # num_evolved = type_counts[len(type_counts) - 1]

        # play round robin
        for pair in itertools.combinations(population, r=2):
            if pair[0][i.type] != pair[1][i.type]:
                if pair[0][i.type] == 16:
                    std_players.reset_gradual(pair[0])
                if pair[1][i.type] == 16:
                    std_players.reset_gradual(pair[1])
                std_players.playMultiRounds(*pair)

        type_counts = [0] * NUM_TYPES
        type_sum_score = [0] * NUM_TYPES

        # get count of each player type
        # and sum the scores for each type
        for m in population:
            type_counts[m[i.type]] += 1
            type_sum_score[m[i.type]] += m[i.scores][i.self]

        # normalize the summed scores by number of members
        for i in range(len(type_sum_score)):
            if type_counts[i] == 0:
                type_sum_score[i] = 0
            else:
                type_sum_score[i] = type_sum_score[i]/type_counts[i]

        # find the strategy with the lowest score
        index = -1
        for i in range(len(type_sum_score)):
            if index == -1:
                if type_counts[i] > 0:
                    index = i
            else:
                if type_counts[i] > 0 and type_sum_score[i] < type_sum_score[index]:
                    index = i

        i = 0
        while i < len(population):
            if population[i][i.type] == index:
                del population[i]
            else:
                i += 1

        exit_order.append(std_players.std_types[index])

        # type_counts[index] = 0
        type_counts = [0] * NUM_TYPES
        for m in population:
            type_counts[m[i.type]] += 1

        types_remaining -= 1

        print("    ")
        print("{}\n".format(type_sum_score))

        # reset scores
        for i in range(len(population)):
            std_players.reset_scores(population[i])

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

    winner = std_players.std_types[type_counts.index(max(type_counts))]
    print("\n\nEnd of run:\n")
    print("  Winner: {}\n".format(winner))
    print("  Type counts:")
    print "  ",
    print('{}\n'.format('{:4d}' * len(type_counts)).format(*type_counts))
    print("  Order of elimination:")
    print("    {}\n".format(exit_order))
    print("  Objective pairs represented:")
    print("    {}\n".format(evolved_obj_pairs))


if __name__ == "__main__":
    main()
