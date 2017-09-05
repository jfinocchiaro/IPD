import numpy as np
import random
from copy import deepcopy
from deap import tools, base, creator, algorithms
import play_game_two_pop
import itertools
import time

def main():
    # minimize personal cost, maximize personal benefit
    creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, 1.0))
    creator.create("Individual", list, fitness=creator.FitnessSingle)

    GENOME_SIZE = 64
    HIST_SIZE = 6
    POP_SIZE = 100
    POP_SIZES = [40, 60]

    NGEN = 3000
    NROUNDS = 50
    TEST_CLR_HIST = False
    CXPB = 0.9
    MUTPB = 0.01428571

    toolbox = base.Toolbox()

    toolbox.register("attr_int", random.randint, 0, 0)

    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, GENOME_SIZE)

    # history:
    #          xyxyxy where:
    #          each xy pair represents one of the last three rounds, oldest to newest
    #          each x value is the trend value for that round (number of abaters increased or decreased)
    #          each y value is the player's decision for that round (0 = abate, 1 = pollute)
    toolbox.register("history", tools.initRepeat, list, toolbox.bit, HIST_SIZE)

    # individual:
    #            [0]: genome
    #            [1]: history
    #            [2]: personal cost
    #            [3]: personal benefit
    #            [4]: cumulative cost
    #            [5]: cumulative benefit
    #            [6]: number of rounds
    #            [7]: population: 0 = wealthy nation, 1 = poorer nation
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.history, toolbox.attr_int, toolbox.attr_int,
                                                                         toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", play_game_two_pop.evaluate)
    # toolbox.register("mate", tools.cxUniform, indpb=0.5)
    toolbox.register("mate", tools.cxTwoPoint)
    # toolbox.register("mate", play_pollution_game.cxOnePointGenome)
    toolbox.register("mutate", tools.mutFlipBit, indpb=MUTPB)
    # toolbox.register("mutate", play_pollution_game.mutInternalFlipBit)
    toolbox.register("select", tools.selBest)

    ###################################################################
    #
    # Learning Phase
    #
    ###################################################################

    # create the populations
    # pop0 contains the more wealthy nations
    # pop1 contains the less wealthy nations
    pops = [toolbox.population(n=POP_SIZES[0]), toolbox.population(n=POP_SIZES[1])]
    # pop0 = toolbox.population(n=POP0_SIZE)
    #
    # pop1 = toolbox.population(n=POP1_SIZE)
    for m in pops[1]:
        m[7] = 1

    # play the first round and evaluate members
    play_game_two_pop.playMultiRounds(pops, 0, NROUNDS)

    # Begin the evolution
    for g in range(1, NGEN):

        fitnesses = [[], []]
        # Evaluate the populations
        for i in range(len(fitnesses)):
            fitnesses[i] = list(map(toolbox.evaluate, pops[i]))
            for ind, fit in zip(pops[i], fitnesses[i]):
                ind.fitness.values = fit

        # fitnesses1 = list(map(toolbox.evaluate, pop1))
        # for ind, fit in zip(pop1, fitnesses1):
        #     ind.fitness.values = fit

        # create offspring
        # offspring = toolbox.map(toolbox.clone, population)
        offsprings = [[], []]

        # crossover
        # uses binary tournament to choose each parent
        for o, size in zip(offsprings, POP_SIZES):
            i = 0
            while len(o) < size:
                child1 = deepcopy(tools.selTournament(pops[i], 1, 2)[0])
                child2 = deepcopy(tools.selTournament(pops[i], 1, 2)[0])
                if random.random() < CXPB:
                    toolbox.mate(child1[0], child2[0])
                    del child1.fitness.values
                    del child2.fitness.values
                    o.append(child1)
                    o.append(child2)

        # mutation
        for o in offsprings:
            for mutant in o:
                toolbox.mutate(mutant[0])

                del mutant.fitness.values

        # play game with offspring so they can be evaluated
        play_game_two_pop.playMultiRounds(offsprings, g, NROUNDS)


        # create combined populations
        for i in range(len(pops)):
            pops[i].extend(offsprings[i])
            pops[i] = toolbox.map(toolbox.clone, pops[i])

        # evaluate combined populations
        for p in pops:
            fits = toolbox.map(toolbox.evaluate, p)
            for fit, ind in zip(fits, p):
                ind.fitness.values = fit

        # survival of the fittest
        for i in range(len(pops)):
            pops[i] = toolbox.select(pops[i], POP_SIZES[i])
            pops[i] = toolbox.map(toolbox.clone, pops[i])

        # play the game with the new population
        play_game_two_pop.playMultiRounds(pops, g, NROUNDS)


        if g % 100 == 0:
            print("-- Generation %i --" % g)

    print("-- End of evolution --")

    # print outcome of evolution
    print "Outcome of evolution:"
    print ("Pop 0 members: {0}  Pop 1 members: {1}".format(POP_SIZES[0], POP_SIZES[1]))
    for i in range(len(pops)):
        all_ind = tools.selBest(pops[i], POP_SIZES[i])
        all_ind = sorted(all_ind, key=lambda member: abs(member.fitness.values[0]))
        for member in all_ind:
            print member

        print

    ################################################################
    #
    # Testing Phase
    #
    ################################################################

    # randomize the history bits of the population
    if TEST_CLR_HIST:
        for p in pops:
            for i in range(len(p)):
                p[i][1] = toolbox.history()

    play_game_two_pop.playMultiRounds(pops, -1, NROUNDS)

    pct_abate = [0, 0]

    # print outcome of evolution
    print
    print ("Pop 0 members: {0}  Pop 1 members: {1}".format(POP_SIZES[0], POP_SIZES[1]))
    for i in range(len(pops)):
        all_ind = tools.selBest(pops[i], POP_SIZES[i])
        all_ind = sorted(all_ind, key=lambda member: abs(member.fitness.values[0]))
        for member in all_ind:
            pct_abate[i] += 1 - member[1][5]
            print member

        print

    for i, val in enumerate(pct_abate):
        print('Population {0} Pct Abate: {1}'.format(i, (val/float(POP_SIZES[i]))*100))
        print
    print


    '''
    import time
    #timestr = 'newevolutionfreeobjs/'
    timestr = time.strftime("%Y%m%d-%H%M%S")
    timestr += '.csv'
    #timestr = 'additionaltrials/trainresettest.csv'
    play_pollution_game.exportGenometoCSV(timestr, all_ind)
    '''

if __name__ == "__main__":
    main()
