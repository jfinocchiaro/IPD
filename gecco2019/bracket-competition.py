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
import std_players
from globals import index as i
import ipd_types

# change this to determine the evaluation metric for testing
SELF = 0    # self score
WINS = 1    # number of wins
WDL = 2     # 3 pts for win, 1 pt for draw, 0 pts for loss
DRAWS = 3   # number of draws
COOP = 4    # mutual cooperation score
MUT = 5     # mutual benefit -- minimize difference between self and opp scores
MATCH = 6   # match score
TESTING_METRIC = MATCH

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
    elif TESTING_METRIC == COOP:
        return member[i.scores][i.coop]
    elif TESTING_METRIC == MUT:
        return -1 * abs(member[i.scores][i.self] - member[i.scores][i.opp])
    elif TESTING_METRIC == MATCH:
        return member[i.scores][i.match]

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
    elif TESTING_METRIC == COOP:
        return member[i.scores][i.coop]
    elif TESTING_METRIC == MUT:
        return -1 * abs(member[i.scores][i.self] - member[i.scores][i.opp])
    elif TESTING_METRIC == MATCH:
        return member[i.scores][i.match]

def main():

    # creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    # creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    # creator.create("Individual", list, fitness=creator.FitnessSingle)

    # global-ish variables won't be changed
    # IND_SIZE = 70
    NUM_EACH_TYPE = 1
    NUM_EACH_EVOLVED = 2
    NUM_TYPES = 18
    POP_SIZE = NUM_EACH_TYPE * (NUM_TYPES - 1)
    COMPETITION_ROUNDS = 20

    TRAINING_GROUP = 'POP'

    filename = str((os.getpid() * time.time()) % 4919) + '.png'

    run_info = [NUM_EACH_TYPE, NUM_TYPES, 150]

    rseed = int(os.getpid() * (time.time() % 4919))
    random.seed(rseed)
    print("\n\nRandom seed: {}\n".format(rseed))

    toolbox = ipd_types.make_types()

    toolbox.register("population", tools.initRepeat, list, toolbox.indv_single)

    population = toolbox.population(n=POP_SIZE)

    # place the fixed strategy players (standard players) in population
    type_counts = [NUM_EACH_TYPE] * NUM_TYPES
    std_players.init_pop(population, type_counts)

    # need 16 standard players so deleting DEFECT
    del population[1]

    # keep track of the order in which strategies exit the competition
    # and the score for each strategy type
    exit_order = []
    type_sum_score = []

    if TRAINING_GROUP == 'AX':
        csvfile = open('best-players-ax.csv', 'r')
    else:
        csvfile = open('best-players-pop.csv', 'r')
    reader = csv.reader(csvfile)

    # read evolved players from csv and put in population
    evolved_candidates = []
    for row in reader:
        evolved_candidates.append(row)

    evolved_obj_pairs = [0] * 4
    done = False

    history = [0] * 6
    scores = [0] * 5
    stats = [0] * 3
    gradual = [0] * 6
    id = 0

    logpath = ''
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

    while not done:
        ind = random.randint(0, len(evolved_candidates) - 1)
        pair = int(evolved_candidates[ind][75])
        type = int(evolved_candidates[ind][76])
        if evolved_obj_pairs[pair] < NUM_EACH_EVOLVED:
            genome = []
            for k in range(70):
                genome.append(int(evolved_candidates[ind][k + 1]))

            population.append([genome, history, scores, stats, pair, type, id, gradual])
            evolved_obj_pairs[pair] += 1

        del evolved_candidates[ind]
        done = evolved_obj_pairs[0] == NUM_EACH_EVOLVED and evolved_obj_pairs[1] == NUM_EACH_EVOLVED and \
               evolved_obj_pairs[2] == NUM_EACH_EVOLVED and evolved_obj_pairs[3] == NUM_EACH_EVOLVED

    random.shuffle(population)
    winners = deepcopy(population[:8])
    del population[:8]

    k = 1
    while len(population) > 1:
        print('\nRound {}'.format(k))
        fname.write('\nRound {}\n'.format(k))
        print('Number of players: {}\n'.format(len(population)))
        fname.write('Number of players: {}\n'.format(len(population)))
        while len(population) > 0:
            j = 0
            p1 = deepcopy(population[j])
            p2 = deepcopy(population[j+1])
            # std_players.reset_scores(p1)
            # std_players.reset_scores(p2)
            del population[:2]

            std_players.playMultiRounds(p1, p2)

            score1 = sort_key(p1)
            score2 = sort_key(p2)
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

            print("Player 1: {} {} {} vs Player 2: {} {} {}".format(p1[i.pair], p1[i.type], score1,
                                                            p2[i.pair], p2[i.type], score2))
            fname.write("Player 1: {} {} {} vs Player 2: {} {} {}\n".format(p1[i.pair], p1[i.type], score1,
                                                            p2[i.pair], p2[i.type], score2))
            print("    Player {} {} eliminated".format(lose[i.pair], lose[i.type]))
            fname.write("    Player {} {} eliminated\n".format(lose[i.pair], lose[i.type]))

        population = deepcopy(winners)
        random.shuffle(population)
        del winners
        winners = []
        k += 1

    print('')
    print("Winner: Player {} {}\n".format(population[0][i.pair], population[0][i.type]))
    fname.write("\nWinner: Player {} {}\n\n".format(population[0][i.pair], population[0][i.type]))

    # timestr = 'logs/'
    # timestr += time.strftime("%Y%m%d-%H%M%S")
    # timestr += '-{}'.format(os.getpid())
    # timestr += '.csv'
    # deapplaygame.exportGenometoCSV(timestr, all_ind, run_info, test_pops, test_labels, best_tested)


    # deapplaygame.plotbestplayers(best_players, training_group=TRAINING_GROUP, filename=filename)

    csvfile.close()
    fname.close()


if __name__ == "__main__":
    main()
