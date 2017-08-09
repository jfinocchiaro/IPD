import numpy as np
import random
from copy import deepcopy
from deap import tools, base, creator, algorithms
import play_pollution_game
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
    GREEN_THRESHOLD = 0.8

    NGEN = 3000
    NROUNDS = 1000
    CXPB = 0.9
    MUTPB = 0.01428571

    toolbox = base.Toolbox()

    toolbox.register("attr_int", random.randint, 0, 0)

    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, GENOME_SIZE)
    toolbox.register("history", tools.initRepeat, list, toolbox.bit, HIST_SIZE)

    # individual:
    #            [0]: genome
    #            [1]: history
    #            [2]: personal cost
    #            [3]: personal benefit
    #            [4]: cumulative cost
    #            [5]: cumulative benefit
    #            [6]: number of rounds
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.history, toolbox.attr_int, toolbox.attr_int,
                                                                         toolbox.attr_int, toolbox.attr_int, toolbox.attr_int), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", play_pollution_game.evaluate)
    toolbox.register("mate", tools.cxUniform, indpb=0.5)
    # toolbox.register("mate", play_pollution_game.cxOnePointGenome)
    toolbox.register("mutate", tools.mutFlipBit, indpb=MUTPB)
    # toolbox.register("mutate", play_pollution_game.mutInternalFlipBit)
    toolbox.register("select", tools.selBest)

    # create the population
    population = toolbox.population(n=POP_SIZE)

    # percentage of population that must go green in order for
    # entire population to realize a reward
    # increases with generations
    green_threshold = 0.1

   # play the first round and evaluate members
    play_pollution_game.playMultiRounds(population, green_threshold, NROUNDS)

    # Begin the evolution
    for g in range(1, NGEN):

        green_threshold = play_pollution_game.calculate_threshold(green_threshold, g)

        # Evaluate the population
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # create offspring
        # offspring = toolbox.map(toolbox.clone, population)
        offspring = []

        # crossover
        # for child1, child2 in zip(offspring[::2], offspring[1::2]):
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
            # customfunctions.memberReset(mutant)

        # play game with offspring so they can be evaluated
        play_pollution_game.playMultiRounds(offspring, green_threshold, NROUNDS)


        # create combined population
        population.extend(offspring)
        population = toolbox.map(toolbox.clone, population)

        fits = toolbox.map(toolbox.evaluate, population)
        for fit, ind in zip(fits, population):
            ind.fitness.values = fit

        # survival of the fittest
        population = toolbox.select(population, POP_SIZE)
        population = toolbox.map(toolbox.clone, population)

        # play the game with the new population
        play_pollution_game.playMultiRounds(population, green_threshold, NROUNDS)


        if g % 100 == 0:
            print("-- Generation %i --" % g)

    print("-- End of evolution --")

    # print outcome of evolution
    print ("%s total individuals in population" % len(population))
    all_ind = tools.selBest(population, (len(population)))
    #all_ind = sorted(population, key=lambda member: abs(member.fitness.values[0]) + abs(member.fitness.values[1]) / 2)
    for member in all_ind:
        print member

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
