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

    GENOME_SIZE = 128
    HIST_SIZE = 6
    POP_SIZE = 100
    PCT_TRUMPS = 0

    NGEN = 3000
    NROUNDS = 250
    TEST_CLR_HIST = False
    CXPB = 0.9
    MUTPB = 0.01428571

    toolbox = base.Toolbox()

    toolbox.register("attr_int", random.randint, 0, 0)

    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, GENOME_SIZE)

    toolbox.register("evolve", play_pollution_game.set_type, "evolve")

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
    #            [7]: member type (evolve, trump, etc)
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.history, toolbox.attr_int, toolbox.attr_int,
                                                                         toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.evolve), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", play_pollution_game.evaluate)
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

   # play the first round and evaluate members
    play_pollution_game.playMultiRounds(population, NROUNDS)

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
        play_pollution_game.playMultiRounds(offspring, NROUNDS)


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
        play_pollution_game.playMultiRounds(population, NROUNDS)


        if g % 100 == 0:
            print("-- Generation %i --" % g)

    print("-- End of evolution --")

    # print outcome of evolution
    print "Outcome of evolution:"
    print ("%s total individuals in population" % len(population))
    all_ind = tools.selBest(population, (len(population)))
    #all_ind = sorted(population, key=lambda member: abs(member.fitness.values[0]) + abs(member.fitness.values[1]) / 2)
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
        for member in population:
            member[1] = toolbox.history()

    if PCT_TRUMPS > 0:
        # Insert some Trumps into population and test evolved population
        population = population[0:int(POP_SIZE * (1 - PCT_TRUMPS))]

        trump_pop = toolbox.population(n=int(PCT_TRUMPS * POP_SIZE))
        for trump in trump_pop:
            trump[7] = "trump"

        population.extend(trump_pop)
        random.shuffle(population)

    play_pollution_game.playMultiRounds(population, NROUNDS)

    # print outcome of evolution
    print "Outcome of testing with Trumps"
    print ("%s total individuals in population" % len(population))
    print ("%s Trumps in population" % (PCT_TRUMPS * POP_SIZE))
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
