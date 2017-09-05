#
# In this version, each member of the population represents a population of
# n countries (divided into two groups Annex I (wealthy) and non-Annex I (ppor).
#

import numpy as np
import random
from copy import deepcopy
from deap import tools, base, creator, algorithms
import play_game_evolve_pop
import itertools
import time

def main():
    # minimize personal cost, maximize personal benefit
    creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, 1.0))
    creator.create("Individual", list, fitness=creator.FitnessSingle)

    GENOME_SIZE = 100
    POP_SIZE = 100
    POP0_SIZE = 40
    POP1_SIZE = 60

    NGEN = 3000
    NROUNDS = 1
    TEST_CLR_HIST = False
    CXPB = 0.9
    MUTPB = 0.01428571

    toolbox = base.Toolbox()

    toolbox.register("attr_int", random.randint, 0, 0)

    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, GENOME_SIZE)

    # individual:
    #            [0]: genome
    #            [1]: benefit this generation
    #            [2]: pct type 0 abaters
    #            [3]: pct type 1 abaters
    #            [4]: cumulative benefit
    #            [5]: number of rounds
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.attr_int, toolbox.attr_int,
                                                                         toolbox.attr_int, toolbox.attr_int, toolbox.attr_int), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", play_game_evolve_pop.evaluate)
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

    # create the population
    population = toolbox.population(n=POP_SIZE)

    for member in population:
        print member
    print

    # play the first round and evaluate members
    play_game_evolve_pop.playround(population, POP0_SIZE, POP1_SIZE)

    # Begin the evolution
    for g in range(1, NGEN):

        # Evaluate the population
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # create offspring
        # offspring = toolbox.map(toolbox.clone, population)
        offspring = []

        # crossover
        # uses binary tournament to choose each parent
        while len(offspring) < POP_SIZE:
            child1 = deepcopy(tools.selTournament(population, 1, 2)[0])
            child2 = deepcopy(tools.selTournament(population, 1, 2)[0])
            if random.random() < CXPB:
                toolbox.mate(child1[0], child2[0])
                del child1.fitness.values
                del child2.fitness.values
                offspring.append(child1)
                offspring.append(child2)

        # mutation
        for mutant in offspring:
            toolbox.mutate(mutant[0])

            del mutant.fitness.values

        # play game with offspring so they can be evaluated
        play_game_evolve_pop.playround(offspring, POP0_SIZE, POP1_SIZE)


        # create combined populations
        population.extend(offspring)
        population = toolbox.map(toolbox.clone, population)

        fits = toolbox.map(toolbox.evaluate, population)
        for fit, ind in zip(fits, population):
            ind.fitness.values = fit

        # survival of the fittest
        population = toolbox.select(population, POP_SIZE)
        population = toolbox.map(toolbox.clone, population)

        # play the game with the new population
        play_game_evolve_pop.playround(population, POP0_SIZE, POP1_SIZE)


        if g % 100 == 0:
            print("-- Generation %i --" % g)

    print("-- End of evolution --")

    # print outcome of evolution
    print "Outcome of evolution:"
    print ("Pop 0 members: {0}  Pop 1 members: {1}".format(POP0_SIZE, POP1_SIZE))
    all_ind = tools.selBest(population, POP_SIZE)
    all_ind = sorted(all_ind, key=lambda member: abs(member.fitness.values[0]))
    for member in all_ind:
        print member

    print

    ################################################################
    #
    # Testing Phase
    #
    ################################################################

    play_game_evolve_pop.playround(population, POP0_SIZE, POP1_SIZE)

    # print outcome of evolution
    print "Testing Phase"
    print ("Pop 0 members: {0}  Pop 1 members: {1}".format(POP0_SIZE, POP1_SIZE))
    all_ind = tools.selBest(population, POP_SIZE)
    all_ind = sorted(all_ind, key=lambda member: abs(member.fitness.values[0]))

    for member in all_ind:
        print member
    print
    print ('Best member:')
    print('    Population 0 Pct Abate: {0}'.format(population[0][2] * 100))
    print('    Population 1 Pct Abate: {0}'.format(population[0][3] * 100))
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
