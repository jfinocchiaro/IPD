import numpy as np
import random
from deap import tools, base, creator, algorithms
import play_pollution_game
import itertools

def main():
    # minimize personal cost, maximize personal benefit
    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, 1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    IND_SIZE = 70
    POP_SIZE = 60
    GREEN_THRESHOLD = 0.8

    toolbox = base.Toolbox()

    toolbox.register("attr_int", random.randint, 0, 0)

    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)

    # individual:
    #            [0]: genome
    #            [1]: personal cost
    #            [2]: personal benefit
    #            [3]: cumulative pop cost
    #            [4]: number of rounds
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.attr_int, toolbox.attr_int,
                                                                         toolbox.attr_int, toolbox.attr_int), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", play_pollution_game.evaluate)
    # toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mate", play_pollution_game.cxOnePointGenome)
    toolbox.register("mutate", play_pollution_game.mutInternalFlipBit)
    toolbox.register("select", tools.selNSGA2)

    NGEN = 500
    CXPB = 0.9
    MUTPB = 0.01428571
    # frontfreeze = NGEN * 0.01
    # freezevalue = NGEN * 0.8

    # create the population
    population = toolbox.population(n=POP_SIZE)

    # play the first round and evaluate members
    play_pollution_game.playMultiRounds(population, 50)

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    # Begin the evolution
    for g in range(1, NGEN):

        # for pair in itertools.combinations(population, r=2):
        play_pollution_game.playMultiRounds(population, 50)

        # create offspring
        offspring = toolbox.map(toolbox.clone, population)

        # crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1[0], child2[0])
                del child1.fitness.values
                # customfunctions.memberReset(child1)
                del child2.fitness.values
                # customfunctions.memberReset(child2)

        # mutation
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
                # customfunctions.memberReset(mutant)

        # create combined population
        population.extend(offspring)
        population = toolbox.map(toolbox.clone, population)

        fits = toolbox.map(toolbox.evaluate, population)
        for fit, ind in zip(fits, population):
            ind.fitness.values = fit

        # survival of the fittest
        population = toolbox.select(population, POP_SIZE)
        population = toolbox.map(toolbox.clone, population)

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
