import numpy as np
import random
from copy import deepcopy
from deap import tools, base, creator, algorithms
import play_nuclear_game
import itertools
import time

def main():
    # minimize personal cost, maximize personal benefit
    creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    GENOME_SIZE = 256
    HIST_SIZE = 8
    POP_SIZE = 30

    NGEN = 1000
    NROUNDS = 50

    CXPB = 0.9
    MUTPB = 0.01428571
    XO_ETA = 0.5

    toolbox = base.Toolbox()

    toolbox.register("attr_int", random.randint, 0, 0)
    toolbox.register("genome_int", random.randint, 0, 100)
    toolbox.register("bit", random.randint, 0, 1)

    toolbox.register("genome", tools.initRepeat, list, toolbox.genome_int, GENOME_SIZE)

    # history:
    #          wxyzwxyz where:
    #          each wxyz 4-tuple represents one of the last two rounds, oldest to newest
    #          each wx pair indicates quartile of player's decision
    #          each yz pair is the player's result: 00 = win
    #                                               01 = draw
    #                                               10 = loss
    #                                               11 = armageddon
    toolbox.register("history", tools.initRepeat, list, toolbox.bit, HIST_SIZE)

    # individual:
    #            [0]: genome
    #            [1]: history
    #            [2]: personal score
    #            [3]: personal wins
    #            [4]: opponent score
    #            [5]: opponent wins
    #            [6]: armageddon events
    #            [7]: generation born
    #            [8]: cooperation score
    #            [9]: id
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.history, toolbox.attr_int,
                                                                         toolbox.attr_int, toolbox.attr_int, toolbox.attr_int,
                                                                         toolbox.attr_int, toolbox.attr_int, toolbox.attr_int,
                                                                         toolbox.attr_int), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", play_nuclear_game.evaluate)
    # toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mate", tools.cxSimulatedBinaryBounded, eta=XO_ETA, low=0, up=100)
    toolbox.register("mutate", play_nuclear_game.mutate, prob=MUTPB)
    toolbox.register("select", tools.selNSGA2)

    # create the population
    population = toolbox.population(n=POP_SIZE)

    # assign ids to members
    for i in range(POP_SIZE):
        population[i][9] = i

    # set id for use when new members created
    id = POP_SIZE

    # play round robin and evaluate members
    for pair in itertools.combinations(population, r=2):
        play_nuclear_game.playMultiRounds(*pair, rounds=NROUNDS)

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
            # [0] in following 2 lines because selTournament returns a tuple
            child1 = deepcopy(tools.selTournament(population, 1, 2)[0])
            child2 = deepcopy(tools.selTournament(population, 1, 2)[0])
            if random.random() < CXPB:
                toolbox.mate(child1[0], child2[0])
                for i in range(GENOME_SIZE):
                    child1[0][i] = int(child1[0][i])
                    child2[0][i] = int(child2[0][i])
                del child1.fitness.values
                del child2.fitness.values
                child1[7] = g
                child2[7] = g
                child1[9] = id
                id += 1
                child2[9] = id
                id += 1
                offspring.append(deepcopy(child1))
                offspring.append(deepcopy(child2))

        # mutation
        for mutant in offspring:
            toolbox.mutate(mutant[0])

            del mutant.fitness.values

        # clear scores of offspring before playing game
        play_nuclear_game.reset_pop_scores(offspring)

        # play game with offspring so they can be evaluated
        for pair in itertools.combinations(offspring, r=2):
            play_nuclear_game.playMultiRounds(*pair, rounds=NROUNDS)

        # create combined population
        population.extend(offspring)
        population = toolbox.map(toolbox.clone, population)

        # calculate fitness scores
        fits = toolbox.map(toolbox.evaluate, population)
        for fit, ind in zip(fits, population):
            ind.fitness.values = fit

        # survival of the fittest
        population = toolbox.select(population, POP_SIZE)
        population = toolbox.map(toolbox.clone, population)

        # clear scores of population
        play_nuclear_game.reset_pop_scores(population)

        # play the game with the new population
        for pair in itertools.combinations(population, r=2):
            play_nuclear_game.playMultiRounds(*pair, rounds=NROUNDS)

        if g % 10 == 0:
            print("-- Generation %i --" % g)
            print ("%s total individuals in population: \n" % len(population))
            # all_ind = tools.selBest(population, (len(population)))
            all_ind = sorted(population, key=lambda member: (member[2]), reverse=True)
            print("{0:>8s} {1:>8s} {2:>8s} {3:>8s} {4:>8s} {5:>8s} {6:>8s} {7:>8s}".format("ID", "Score", "Wins", "O Score",
                                                                                     "O Wins", "Booms", "Gen", "Coop"))
            for member in all_ind:
                print("{0:8d} {1:8d} {2:8d} {3:8d} {4:8d} {5:8d} {6:8d} {7:8d}".format(member[9], member[2], member[3], member[4],
                                                                                member[5], member[6], member[7], member[8]))
            print

    print("-- End of evolution --\n\n")

    # print outcome of evolution
    print ("%s total individuals in population: \n" % len(population))
    # all_ind = tools.selBest(population, (len(population)))
    all_ind = sorted(population, key=lambda member: (member[2]), reverse=True)
    print("{0:8s} {1:8s} {2:8s} {3:8s} {4:8s} {5:8s} {6:8s} {7:8s}".format("ID", "Score", "Wins", "O Score",
                                                                           "O Wins", "Booms", "Gen", "Coop"))
    for member in all_ind:
        print("{0:8d} {1:8d} {2:8d} {3:8d} {4:8d} {5:8d} {6:8d} {7:8d}".format(member[9], member[2], member[3], member[4],
                                                                        member[5], member[6], member[7], member[8]))
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
