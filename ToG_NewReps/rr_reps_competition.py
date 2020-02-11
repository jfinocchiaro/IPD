#
# Implementation of an Evolutionary Competition that includes players of multiple
# represenations.  It begins with an equal number
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
import newreps_std_players as sp
from globals import index as idx
from globals import keys, REP, HIST3, HIST6, MULTI, TOTAL_TYPES
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

# change this to determine the round robin tournament to play
#   ALL: play rr among all players
#   AX: play rr of all evolved playes against all axelrod players
PLAY = 'ALL'

main_run = False


def run_rr(t_group=None, num_each=None, num_evolved=None, num_reps=None):

    # creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    # creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    # creator.create("Individual", list, fitness=creator.FitnessSingle)

    # global-ish variables won't be changed
    # IND_SIZE = 70

    # NUM_EVOLVED_TYPES = 16

    # eliminate the single objectives 2 & 3 from rr tournament
    #    obj 2: maximize cooperation
    #    obj 3: maximize opponent score
    #    player types: 51, 52, 55, 56, 59, 60, 63, 64, 67, 68, 71, 72, 75, 76, 79, 80
    elim_single_2_3 = True
    elim_types = [51, 52, 55, 56, 59, 60, 63, 64, 67, 68, 71, 72, 75, 76, 79, 80]
    
    if t_group is not None:
        TRAINING_GROUP = t_group
    else:
        TRAINING_GROUP = 'BOTH'

    if TRAINING_GROUP == 'AX':
        in_filenames = ['newreps_trained_axelrod/rep0_axelrod_no-noise_5k/rep0_axelrod_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep1_axelrod_no-noise_5k/rep1_axelrod_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep2_axelrod_no-noise_5k/rep2_axelrod_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep4_axelrod_no-noise_5k/rep4_axelrod_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep0_axelrod_single-obj_no-noise_5k/rep0_axelrod_single-obj_no-             noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep1_axelrod_single-obj_no-noise_5k/rep1_axelrod_single-obj_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep2_axelrod_single-obj_no-noise_5k/rep2_axelrod_single-obj_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep4_axelrod_single-obj_no-noise_5k/rep4_axelrod_single-obj_no-noise_5k_best-during_selfscore.csv']
    elif TRAINING_GROUP == 'POP':
        in_filenames = ['newreps_trained_pop/rep0_pop_no-noise_5k/rep0_pop_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep1_pop_no-noise_5k/rep1_pop_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep2_pop_no-noise_5k/rep2_pop_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep4_pop_no-noise_5k/rep4_pop_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep0_pop_single-obj_no-noise_5k/rep0_pop_single-obj_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep1_pop_single-obj_no-noise_5k/rep1_pop_single-obj_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep2_pop_single-obj_no-noise_5k/rep2_pop_single-obj_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep4_pop_single-obj_no-noise_5k/rep4_pop_single-obj_no-noise_5k_best-during_selfscore.csv']
    else:
        in_filenames = ['newreps_trained_axelrod/rep0_axelrod_no-noise_5k/rep0_axelrod_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep1_axelrod_no-noise_5k/rep1_axelrod_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep2_axelrod_no-noise_5k/rep2_axelrod_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_axelrod/rep4_axelrod_no-noise_5k/rep4_axelrod_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep0_pop_no-noise_5k/rep0_pop_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep1_pop_no-noise_5k/rep1_pop_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep2_pop_no-noise_5k/rep2_pop_no-noise_5k_best-during_selfscore.csv',
                        'newreps_trained_pop/rep4_pop_no-noise_5k/rep4_pop_no-noise_5k_best-during_selfscore.csv']

    # set the input file path for running on comet
    path = ''
    if 'comet' in platform.node():
        path += '/oasis/scratch/comet/'
        path += pwd.getpwuid(os.getuid())[0]
        path += '/temp_project/'

    # prepend path onto filenames:
    for j, f in enumerate(in_filenames):
        in_filenames[j] = path + f
        
    if num_each is not None:
        NUM_EACH_TYPE = num_each
    else:
        NUM_EACH_TYPE = 10

    if num_evolved is not None:
        NUM_EACH_EVOLVED = num_evolved
    else:
        NUM_EACH_EVOLVED = 10

#    if num_reps is not None:
#        NUM_REPS = num_reps
#    else:
#        NUM_REPS = 4
    
    POP_SIZE = NUM_EACH_TYPE * sp.NUM_STD_TYPES

    run_info = [TRAINING_GROUP, NUM_EACH_TYPE, 150]

    rseed = int(os.getpid() * (time.time() % 4919))
    random.seed(rseed)
    # print("\n\nRandom seed: {}\n".format(rseed))

    toolbox = ipd_types.make_types()

    toolbox.register("population", tools.initRepeat, list, toolbox.indv_single)

    population = toolbox.population(n=POP_SIZE)

    # place the fixed strategy players (standard players) in population
    type_counts = [NUM_EACH_TYPE] * sp.NUM_STD_TYPES
    sp.init_pop(population, type_counts)

    # player types in this run
    p_types = []
    evolved_candidates = []
    for in_file in in_filenames:        
        
        csvfile = open(in_file, 'r')
        reader = csv.reader(csvfile)

        # read evolved players from csv and put in population
        # evolved_candidates = []
        for row in reader:
            # remove blank cell at beginning of row and insert rep at beginning
            row.pop(0)
            p_type = int(row[-4])
            
            # this if statement allows us to skip adding single objectives 2 and 3 to
            # the list of candidate rr players
            if p_type not in elim_types or not elim_single_2_3:
                # check if player type for this row already in p_types
                # if not, add it
                if not p_type in p_types:
                    p_types.append(p_type)

                # cast the individual strings to numeric types
                n_line = [float(x) if '.' in x else int(x) for x in row]

                evolved_candidates.append(n_line)

        csvfile.close()

    ###
    ### added the representation as element 0 in each element in evolved candidates
    ### will need to change some indices below to deal with this
    ###
    
    # list of counts of number of individuals to add to population
    # for each (objective pair x representation) being tested added to population
    # evolved_obj_pairs = [0] * (4 * NUM_REPS)
    evolved_obj_pairs = [0] * TOTAL_TYPES


    # determine if the members begin with generation or genome
    # if former, must offest indices by 1
    # if int(evolved_candidates[0][1]) > 1:
    #     base = 1
    # else:
    #     base = 0

    done = False
    while not done:
        index = random.randint(0, len(evolved_candidates) - 1)
        # indiv = evolved_candidates.pop(index)
        indiv = evolved_candidates[index]
        rep = indiv[-3]
        
        # pair_indices below have been updated to allow for the representation
        # begin prepended to the entries in evolved_candidates
        if rep == 0 or rep == 3:
            pair_index = 78
            g_len = 70
        elif rep == 1 or rep == 2:
            pair_index = 19
            g_len = 11
        else:
            pair_index = 73
            g_len = 65
        
        pair = indiv[pair_index]
        # p_type = (indiv[pair_index + 1] + (4 * rep) + pair) if rep < 4 else (indiv[pair_index + 1] + (4 * (rep-1)) + pair)
        p_type = indiv[pair_index + 1]
        # print('pair: {}   type: {}'.format(pair, p_type))
        # subtract 17 because we need to shift the evolved player types to begin at 0 for
        # indexing into evolved_obj_pairs list
                                                                              
        # obj_pairs_index = p_type - 17
        obj_pairs_index = p_type
                                                                              
        if evolved_obj_pairs[obj_pairs_index] < NUM_EACH_EVOLVED:
            # elements to be added to the individuals
            # reps with history of 3 bits
            if rep == 1 or rep == 2:
                history = [0] * 3
            else:
                history = [0] * 6
            scores = [0] * 5
            stats = [0] * 3
            gradual = [0] * 6
            ident = 0
            state = 0

            # genome = indiv[1:g_len + 1]
            genome = indiv[:g_len]

            if history == []:
                print('history is empty: {}'.format(rep))
                
            # convert rep back to standard representation numbers to work with functions in 
            # deapplaygame2 and std_players
            # if rep > 4:
            #     rep = rep - 5 if rep < 8 else 4
                
            population.append(deepcopy([genome, history, scores, stats, pair, p_type, ident, gradual, state, rep]))
            evolved_obj_pairs[obj_pairs_index] += 1
            
            evolved_candidates.pop(index)
            
        # for each type represented in p_types, check if we have chosen NUM_EACH_EVOLVED members
        # done is True if all checks are True
        done_vector = [evolved_obj_pairs[e] >= NUM_EACH_EVOLVED for e in p_types]
        done = all(done_vector)
        
#        full = True
#        j = 0
#        while j < NUM_REPS * 4 and full:
#            full = (evolved_obj_pairs[j] == NUM_EACH_EVOLVED)
#            j += 1
#
#        done = full
    
    if PLAY == 'ALL':
        # play round robin against axelrod and evolved players
        for pair in itertools.combinations(population, r=2):
            if pair[0][idx.type] != pair[1][idx.type]:
                sp.playMultiRounds(*pair)
    else:
        # play round robin against axelros players only
        for pair in itertools.combinations(population, r=2):
            if (pair[0][idx.type] < 17 and pair[1][idx.type] >= 17) or (pair[0][idx.type] >= 17 and pair[1][idx.type] < 17):
                sp.playMultiRounds(*pair)
        
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
        logpath += 'rr_pop/'
    elif TRAINING_GROUP == 'AX':
        logpath += 'rr_axelrod/'
    else:
        logpath += 'rr_both/'
        
    logpath += 'rr-rep-all-'
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
                            member[idx.genome] + \
                            [float(member[idx.scores][idx.self]) / member[idx.scores][idx.games]] + \
                            [float(member[idx.scores][idx.opp]) / member[idx.scores][idx.games]] + \
                            # [ min(6* float(member[3])/member[4], COOPERATION_MAX)] +    \
                            [float(member[idx.scores][idx.coop]) / member[idx.scores][idx.games]] + \
                            [member[idx.scores][idx.games]] + \
                            [member[idx.pair]] + \
                            [member[idx.type]])

    return sorted_pop


if __name__ == "__main__":
    main_run = True
    run_rr()
