#
# Implementation of an Evolutionary Competition.  It begins with an equal number
# of some number of each of Axelrod's players and our best players.  Play a round
# robin.  Then evaluate the success of each strategy.  For the next round, each
# strategy is assigned a number of members proportional to its success.  The strategy
# with the most members at the end is the winner.
#

import time
import random
import csv
from copy import deepcopy
from deap import tools, base, creator, algorithms
import os
import pwd
import platform

import std_players
import deapplaygame2 as dpg
from globals import index as i
from globals import keys
import ipd_types

# change this to determine the evaluation metric for testing
# SELF = 0    # self score
# WINS = 1    # number of wins
# WDL = 2     # 3 pts for win, 1 pt for draw, 0 pts for loss
# DRAWS = 3   # number of draws
# COOP = 4    # mutual cooperation score
# MUT = 5     # mutual benefit -- minimize difference between self and opp scores
# MATCH = 6   # score of most recent match
TESTING_METRIC = keys.MATCH

main_run = False


def run_bracket(t_group=None, num_each=None, num_evolved=None):

    # creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    # creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    # creator.create("Individual", list, fitness=creator.FitnessSingle)

    # global-ish variables won't be changed
    # IND_SIZE = 70
    if num_each is not None:
        NUM_EACH_TYPE = num_each
    else:
        NUM_EACH_TYPE = 1

    if num_evolved is not None:
        NUM_EACH_EVOLVED = num_evolved
    else:
        NUM_EACH_EVOLVED = 1

    NUM_TYPES = 21
    POP_SIZE = NUM_EACH_TYPE * (NUM_TYPES - 4)
    COMPETITION_ROUNDS = 20

    if t_group is not None:
        TRAINING_GROUP = t_group
    else:
        TRAINING_GROUP = 'POP'

    filename = str((os.getpid() * time.time()) % 4919) + '.png'

    run_info = [NUM_EACH_TYPE, NUM_TYPES, 150]

    rseed = int(os.getpid() * (time.time() % 4919))
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
    logpath += 'bracket-'
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

    # need 16 standard players so deleting COOP, DEFECT, RANDOM, CCD, DDC
    elim_list = ['COOP', 'DEFECT', 'RANDOM', 'CCD', 'DDC']
    j = 0
    while j < len(population):
        if std_players.std_types[population[j][i.type]] in elim_list:
            del population[j]
        else:
            j += 1

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

    # randomize the order of the players
    random.shuffle(population)
    # first 8 players get a first-round bye
    # winners = deepcopy(population[:8])
    # del population[:8]
    winners = []

    # list to be returned for writing to csv file
    bracket = []

    rnd = 1
    while len(population) > 1:
        if main_run:
            print('\nRound {}'.format(rnd))
            print('Number of players: {}\n'.format(len(population)))
        fname.write('\nRound {}\n'.format(rnd))
        fname.write('Number of players: {}\n'.format(len(population)))
        first = True
        while len(population) > 0:
            line = []
            if first:
                line.append(rnd)
                first = False
            else:
                line.append(None)
            j = 0
            p1 = deepcopy(population[j])
            p2 = deepcopy(population[j+1])
            # std_players.reset_scores(p1)
            # std_players.reset_scores(p2)
            del population[:2]

            std_players.playMultiRounds(p1, p2)

            score1 = dpg.sort_key(p1, TESTING_METRIC)
            score2 = dpg.sort_key(p2, TESTING_METRIC)
            if score1 > score2:
                winners.append(p1)
                lose = p2
            elif score2 > score1:
                winners.append(p2)
                lose = p1
            else:
                if random.randint(0, 1):
                    winners.append(p1)
                    lose = p2
                else:
                    winners.append(p2)
                    lose = p1

            if main_run:
                print("Player 1: {} {} {} vs Player 2: {} {} {}".format(p1[i.pair], p1[i.type], score1,
                                                                p2[i.pair], p2[i.type], score2))
                print("    Player {} {} eliminated".format(lose[i.pair], lose[i.type]))
            fname.write("Player 1: {} {} {} vs Player 2: {} {} {}\n".format(p1[i.pair], p1[i.type], score1,
                                                            p2[i.pair], p2[i.type], score2))
            fname.write("    Player {} {} eliminated\n".format(lose[i.pair], lose[i.type]))

            line.extend([p1[i.type], p1[i.pair], score1, p2[i.type], p2[i.pair], score2])
            bracket.append(line)

        bracket.append([])
        population = deepcopy(winners)
        random.shuffle(population)
        del winners
        winners = []
        rnd += 1

    if main_run:
        print('')
        print("Winner: Player {} {}\n".format(population[0][i.pair], population[0][i.type]))
    fname.write("\nWinner: Player {} {}\n\n".format(population[0][i.pair], population[0][i.type]))
    bracket.append([None, population[0][i.type], population[0][i.pair]])
    bracket.append([])

    # timestr = 'logs/'
    # timestr += time.strftime("%Y%m%d-%H%M%S")
    # timestr += '-{}'.format(os.getpid())
    # timestr += '.csv'
    # deapplaygame.exportGenometoCSV(timestr, all_ind, run_info, test_pops, test_labels, best_tested)


    # deapplaygame.plotbestplayers(best_players, training_group=TRAINING_GROUP, filename=filename)

    csvfile.close()
    fname.close()

    return bracket

if __name__ == "__main__":
    main_run = True
    run_bracket()
