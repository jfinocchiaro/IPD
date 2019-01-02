import time
# import numpy as np
import random
from copy import deepcopy
from deap import tools, base, creator
import itertools
import os
import pwd
import platform
import csv
from collections import defaultdict

import deapplaygame2 as dpg
import axelrodplayers2 as ap
import std_players as std
from globals import index as i
import ipd_types


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


# set the logging path for running on comet
logpath = ''
if 'comet' in platform.node():
    logpath += '/oasis/scratch/comet/'
    logpath += pwd.getpwuid(os.getuid())[0]
    logpath += '/temp_project/'


def main():

    # global-ish variables won't be changed
    IND_SIZE = 70
    pop_sizes = [120]
    NGEN = 100
    CXPB = 0.9

    NUM_EACH_TYPE = 1
    NUM_TYPES = 18

    BEST_EACH = True

    # change this depending on the desired trial
    # change to 'AX' for training against Axelrod, or 'POP' to train within population
    TRAINING_GROUP = 'AX'

    toolbox = ipd_types.make_types()

    toolbox.register("population", tools.initRepeat, list, toolbox.indv_multi)

    toolbox.register("evaluate", dpg.evaluate)
    toolbox.register("mate", dpg.cxOnePointGenome)
    # toolbox.register("mate", tools.cxUniform, indpb=0.2)
    toolbox.register("mutate", dpg.mutInternalFlipBit)
    toolbox.register("select", tools.selNSGA2)
    # toolbox.register("select", tools.selSPEA2)

    best_players = defaultdict(list)
    filename = str((os.getpid() * time.time()) % 4919) + '.png'

    # To hold the top players based on test results throughout the run
    # Each element is a list containing a member and the generation of the test
    num_best = 20
    best_tested = []
    
    for POP_SIZE in pop_sizes:
        run_info = [POP_SIZE, NGEN, TRAINING_GROUP]

        rseed = int(os.getpid() * (time.time() % 4919))
        random.seed(rseed)
        print("\n\nRandom seed: {}\n".format(rseed))

        #
        # axelrod population
        #
        axelrodPop = toolbox.population(n=((NUM_TYPES - 1) * NUM_EACH_TYPE))

        arod_counts = [NUM_EACH_TYPE] * NUM_TYPES
        arod_counts[len(arod_counts) - 1] = 0
        std.init_pop(axelrodPop, arod_counts)

        #
        # 4 evolving subpopulations
        #
        selfish_population = toolbox.population(n=POP_SIZE / 4)
        communal_population = toolbox.population(n=POP_SIZE / 4)
        cooperative_population = toolbox.population(n=POP_SIZE / 4)
        selfless_population = toolbox.population(n=POP_SIZE / 4)

        # assign ids and player type to the members
        n = POP_SIZE/4
        j = 0
        while j < n:
            selfish_population[j][i.id] = j
            selfish_population[j][i.type] = NUM_TYPES - 1
            communal_population[j][i.id] = n + j
            communal_population[j][i.type] = NUM_TYPES - 1
            cooperative_population[j][i.id] = 2 * n + j
            cooperative_population[j][i.type] = NUM_TYPES - 1
            selfless_population[j][i.id] = 3 * n + j
            selfless_population[j][i.type] = NUM_TYPES - 1
            j += 1


        # set an id variable to use for assigning ids to offspring
        memb_id = POP_SIZE

        # set objectives flag for members of each population
        selfish_population = dpg.uniformobjectivesSelfish(selfish_population)
        communal_population = dpg.uniformobjectivesCommunal(communal_population)
        cooperative_population = dpg.uniformobjectivesCoop(cooperative_population)
        selfless_population = dpg.uniformobjectivesSelfless(selfless_population)

        # conducts round-robin, depending on who's the training population
        if TRAINING_GROUP == 'POP':
            for pair in itertools.combinations(selfish_population + communal_population + cooperative_population +
                                               selfless_population, r=2):
                # dpg.setHistBits(pair[0])
                # dpg.setHistBits(pair[1])
                dpg.playMultiRounds(*pair)
        elif TRAINING_GROUP == 'AX':
            # axelrodPop = ap.initAxpop()
            # std.init_pop(axelrodPop, arod_counts)
            for population in [selfish_population, communal_population, cooperative_population, selfless_population]:
                for member in population:
                    for opponent in axelrodPop:
                        # dpg.setHistBits(member)
                        # ap.playAxelrodPop(member, opponent)
                        std.playMultiRounds(member, opponent)
        else:
            print 'Invalid training group- please fix.'
            quit()

        # Evaluate each population
        for population in [selfish_population, communal_population, cooperative_population, selfless_population]:
            fitnesses = list(map(toolbox.evaluate, population))
            for ind, fit in zip(population, fitnesses):
                ind.fitness.values = fit


        print("Starting evolution: \n")
        # Begin the evolution
        for g in range(NGEN):

            # SELFISH
            for member in selfish_population:
                dpg.resetPlayer(member)

            # create offspring
            offspring = toolbox.map(toolbox.clone, selfish_population)

            # shuffle offspring to ensure different pairings for crossover in each generation
            random.shuffle(offspring)

            for k in range(len(offspring)):
                offspring[k][i.id] = memb_id
                memb_id += 1

            # crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                # mates with probability 0.9
                if random.random() < CXPB:
                    toolbox.mate(child1[i.genome], child2[i.genome])
                    # del child1.fitness.values
                    # del child2.fitness.values

            # mutation
            for mutant in offspring:
                toolbox.mutate(mutant)
                del mutant.fitness.values


            # create combined population
            selfish_population.extend(offspring)
            selfish_population = toolbox.map(toolbox.clone, selfish_population)

            # COMMUNAL
            for member in communal_population:
                dpg.resetPlayer(member)


            # create offspring
            offspring = toolbox.map(toolbox.clone, communal_population)

            # shuffle offspring to ensure different pairings for crossover in each generation
            random.shuffle(offspring)

            for k in range(len(offspring)):
                offspring[k][i.id] = memb_id
                memb_id += 1

            # crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                # mates with probability 0.9
                if random.random() < CXPB:
                    toolbox.mate(child1[i.genome], child2[i.genome])
                    # del child1.fitness.values
                    # del child2.fitness.values

            # mutation
            for mutant in offspring:
                toolbox.mutate(mutant)
                del mutant.fitness.values


            # create combined population
            communal_population.extend(offspring)
            communal_population = toolbox.map(toolbox.clone, communal_population)


            # COOPERATIVE
            for member in cooperative_population:
                dpg.resetPlayer(member)


            # create offspring
            offspring = toolbox.map(toolbox.clone, cooperative_population)

            # shuffle offspring to ensure different pairings for crossover in each generation
            random.shuffle(offspring)

            for k in range(len(offspring)):
                offspring[k][i.id] = memb_id
                memb_id += 1

            # crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                # mates with probability 0.9
                if random.random() < CXPB:
                    toolbox.mate(child1[i.genome], child2[i.genome])
                    # del child1.fitness.values
                    # del child2.fitness.values

            # mutation
            for mutant in offspring:
                toolbox.mutate(mutant)
                del mutant.fitness.values


            # create combined population
            cooperative_population.extend(offspring)
            cooperative_population = toolbox.map(toolbox.clone, cooperative_population)


            # SELFLESS
            for member in selfless_population:
                dpg.resetPlayer(member)


            # create offspring
            offspring = toolbox.map(toolbox.clone, selfless_population)

            # shuffle offspring to ensure different pairings for crossover in each generation
            random.shuffle(offspring)

            for k in range(len(offspring)):
                offspring[k][i.id] = memb_id
                memb_id += 1

            # crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                # mates with probability 0.9
                if random.random() < CXPB:
                    toolbox.mate(child1[i.genome], child2[i.genome])
                    # del child1.fitness.values
                    # del child2.fitness.values

            # mutation
            for mutant in offspring:
                toolbox.mutate(mutant)
                del mutant.fitness.values


            # create combined population
            selfless_population.extend(offspring)
            selfless_population = toolbox.map(toolbox.clone, selfless_population)


            # conducts round-robin, depending on who's the training population
            if TRAINING_GROUP == 'POP':
                for pair in itertools.combinations(selfish_population + communal_population + cooperative_population +
                                                   selfless_population, r=2):
                    dpg.setHistBits(pair[0])
                    dpg.setHistBits(pair[1])
                    dpg.playMultiRounds(*pair)
            elif TRAINING_GROUP == 'AX':
                for opponent in axelrodPop:
                    dpg.resetPlayer(opponent)

                for population in [selfish_population, communal_population, cooperative_population, selfless_population]:
                    for member in population:
                        for opponent in axelrodPop:
                            dpg.setHistBits(member)
                            # ap.playAxelrodPop(member, opponent)
                            std.playMultiRounds(member, opponent)
            else:
                print 'Invalid training group- please fix.'
                quit()


            # SELFISH
            # evaluate how well players did
            fits = toolbox.map(toolbox.evaluate, selfish_population)
            for fit, ind in zip(fits, selfish_population):
                ind.fitness.values = fit

            # survival of the fittest- uses NSGA-II
            selfish_population = toolbox.select(selfish_population, POP_SIZE/4)
            selfish_population = toolbox.map(toolbox.clone, selfish_population)


            # COMMUNAL
            # evaluate how well players did
            fits = toolbox.map(toolbox.evaluate, communal_population)
            for fit, ind in zip(fits, communal_population):
                ind.fitness.values = fit

            # survival of the fittest- uses NSGA-II
            communal_population = toolbox.select(communal_population, POP_SIZE/4)
            communal_population = toolbox.map(toolbox.clone, communal_population)


            # COOPERATIVE
            # evaluate how well players did
            fits = toolbox.map(toolbox.evaluate, cooperative_population)
            for fit, ind in zip(fits, cooperative_population):
                ind.fitness.values = fit

            # survival of the fittest- uses NSGA-II
            cooperative_population = toolbox.select(cooperative_population, POP_SIZE/4)
            cooperative_population = toolbox.map(toolbox.clone, cooperative_population)


            # SELFLESS
            # evaluate how well players did
            fits = toolbox.map(toolbox.evaluate, selfless_population)
            for fit, ind in zip(fits, selfless_population):
                ind.fitness.values = fit

            # survival of the fittest- uses NSGA-II
            selfless_population = toolbox.select(selfless_population, POP_SIZE/4)
            selfless_population = toolbox.map(toolbox.clone, selfless_population)


            # for progress updates
            if g % 10 == 0 and g > 0:
                print("-- Generation %i --" % g)

                # best_player_current = sorted(selfish_population + cooperative_population + communal_population +
                #                              selfless_population, key=lambda member: member[1], reverse=True)[0]
                best_player_current = sorted(selfish_population + cooperative_population + communal_population +
                                             selfless_population, key=sort_key, reverse=True)[0]

                current_best_score = best_player_current[i.scores][i.self] / float(best_player_current[i.scores][i.games])
                best_players['Train'].append(current_best_score)

                all_ind = selfish_population + communal_population + cooperative_population + selfless_population
                
                test_pop = deepcopy(all_ind)

                # reset the scores for the test_pop
                for member in test_pop:
                    dpg.resetPlayer(member)

                # reset scores for axelrod pop
                for member in axelrodPop:
                    dpg.resetPlayer(member)

                # play against Axelrod -- 150 rounds for each member-opponent pair
                # axelrodPop = ap.initAxpop()
                for member in test_pop:
                    for opponent in axelrodPop:
                        dpg.setHistBits(member)
                        # ap.playAxelrodPop(member, opponent)
                        std.playMultiRounds(member, opponent)

                # sort the test_pop by decreasing value of self score
                # testing is single objective - self score only
                # to use cooperation as single objective: change member[1] to member[3]
                # sorted_test_self = sorted(test_pop, key=lambda member: member[1], reverse=True)
                sorted_test_self = sorted(test_pop, key=sort_key, reverse=True)

                current_best_score_test = sorted_test_self[0][i.scores][i.self] / float(sorted_test_self[0][i.scores][i.games])
                sorted_test_self = sorted_test_self[:num_best]
                for e in sorted_test_self:
                    best_tested.append([deepcopy(e), g])

                # in best_tested, the elements are a themselves lists of length 2
                # each of those lists consists of:
                #   0: a member of the population
                #   1: the generation
                #
                # thus, member[0][1] is the self-score field of the member
                # best_tested = sorted(best_tested, key=lambda member: member[0][1], reverse=True)
                best_tested = sorted(best_tested, key=sort_key_best, reverse=True)

                # best_tested = best_tested[:num_best]
                del best_tested[num_best:]
                # best_players['Test'].append(current_best_score_test)

                del test_pop
                del sorted_test_self

        print("-- End of evolution --\n")


        # print outcome of evolution
        print ("%s total individuals in each population" % len(selfish_population))
        #all_ind = tools.selBest(population, (len(population)))
        sorted_selfish = toolbox.select(selfish_population, POP_SIZE / 4)
        sorted_selfish = toolbox.map(toolbox.clone, sorted_selfish)
        sorted_communal = toolbox.select(communal_population, POP_SIZE / 4)
        sorted_communal = toolbox.map(toolbox.clone, sorted_communal)
        sorted_cooperative = toolbox.select(cooperative_population, POP_SIZE / 4)
        sorted_cooperative = toolbox.map(toolbox.clone, sorted_cooperative)
        sorted_selfless = toolbox.select(selfless_population, POP_SIZE / 4)
        sorted_selfless = toolbox.map(toolbox.clone, sorted_selfless)
        all_ind = sorted_selfish + sorted_communal + sorted_cooperative + sorted_selfless

        if BEST_EACH:
            best_each_pop = []
            best_each_pop.extend(sorted_selfish[:5])
            best_each_pop.extend(sorted_communal[:5])
            best_each_pop.extend(sorted_cooperative[:5])
            best_each_pop.extend(sorted_selfless[:5])

        for member in all_ind:
            print member

        # prints summary of objective outcomes
        selfish = 0
        cooperative = 0
        selfless = 0
        mutual = 0
        for x in range(len(all_ind)):
            objectives = all_ind[x][i.pair]
            if objectives == 0:
                selfish += 1
            elif objectives == 1:
                mutual += 1
            elif objectives == 2:
                cooperative += 1
            elif objectives == 3:
                selfless += 1


        print "Selfish:  " + str(selfish)
        print "Mutual well-being:  " + str(mutual)
        print "Mutual cooperation:  " + str(cooperative)
        print "Selfless:  " + str(selfless)


        # test_pop = []
        # test_pop.append(deepcopy(sorted_selfish[len(sorted_selfish)-1]))
        # test_pop.append(deepcopy(sorted_communal[len(sorted_communal)-1]))
        # test_pop.append(deepcopy(sorted_cooperative[len(sorted_cooperative)-1]))
        # test_pop.append(deepcopy(sorted_selfless[len(sorted_selfless)-1]))

        # test_pop will be used in the testing phase against Axelrod
        test_pop = deepcopy(all_ind)

        # reset the scores for the test_pop
        for member in test_pop:
            dpg.resetPlayer(member)

        # reset scores for axelrod pop
        for member in axelrodPop:
            dpg.resetPlayer(member)

        # play against Axelrod -- 150 rounds for each member-opponent pair
        # axelrodPop = ap.initAxpop()
        for member in test_pop:
            for opponent in axelrodPop:
                dpg.setHistBits(member)
                # ap.playAxelrodPop(member, opponent)
                std.playMultiRounds(member, opponent)

        # sort the test_pop by decreasing value of self score
        # testing is single objective - self score only
        # to use cooperation as single objective: change member[1] to member[3]
        sorted_test_self = sorted(test_pop, key=sort_key, reverse=True)

        sorted_test_opp = sorted(test_pop, key=lambda member: member[i.scores][i.opp], reverse=True)
        # sorted_test_opp = None
        sorted_test_coop = sorted(test_pop, key=lambda member: member[i.scores][i.coop], reverse=True)
        # sorted_test_coop = None

        # flags for which test objectives to log in csv file
        #     test_pops[0]: self score
        #     test_pops[1]: opppnent score
        #     test_pops[2]: cooperation
        # set position to None to exclude
        test_pops = [1, None, None]

        # labels to print for each of the tests
        test_labels = ["Self Score", "Opp Score", "Cooperation"]

        # number of members to display after testing
        m = 20

        # for the test objectives indicated in test_pops
        # grab just the top m test_pop members for writing to the csv file
        if test_pops[0] is not None:
            if len(sorted_test_self) > m:
                sorted_test_self = sorted_test_self[:m]
            test_pops[0] = sorted_test_self

        if test_pops[1] is not None:
            if len(sorted_test_opp) > m:
                sorted_test_opp = sorted_test_opp[:m]
            test_pops[1] = sorted_test_opp

        if test_pops[2] is not None:
            if len(sorted_test_coop) > m:
                sorted_test_coop = sorted_test_coop[:m]
            test_pops[2] = sorted_test_coop

        # write to csv file
        global logpath
        best_each_path = logpath
        if TRAINING_GROUP == 'POP':
            logpath += 'train_pop/'
        else:
            logpath += 'train_axelrod/'
        logpath += time.strftime("%Y%m%d-%H%M%S")
        logpath += '-{}'.format(os.getpid())
        logpath += '.csv'
        dpg.exportGenometoCSV(logpath, all_ind, run_info, test_pops, test_labels, best_tested)

        if BEST_EACH:
            best_each_path += 'best_each/'
            best_each_path += time.strftime("%Y%m%d-%H%M%S")
            best_each_path += '-{}'.format(os.getpid())
            best_each_path += '.csv'

            with open(best_each_path, 'wb') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)

                writer.writerow(["population: " + str(POP_SIZE)])
                writer.writerow(["generations: " + str(NGEN)])
                writer.writerow(["training: " + TRAINING_GROUP])
                writer.writerow("")
                for member in best_each_pop:
                    writer.writerow([''] + \
                                    member[i.genome] + \
                                    [float(member[i.scores][i.self]) / member[i.scores][i.games]] + \
                                    [float(member[i.scores][i.opp]) / member[i.scores][i.games]] + \
                                    # [ min(6* float(member[3])/member[4], COOPERATION_MAX)] +    \
                                    [float(member[i.scores][i.coop]) / member[i.scores][i.games]] + \
                                    [member[i.scores][i.games]] + \
                                    [member[i.pair]] + \
                                    [member[i.type]])

    # dpg.plotbestplayers(best_players, training_group=TRAINING_GROUP, filename=filename)

if __name__ == "__main__":
    main()
