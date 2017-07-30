import numpy as np
import random
from deap import tools, base, creator, algorithms
import deapplaygame
import itertools


def main():
    creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    IND_SIZE = 70
    POP_SIZE = 60
    NUM_SPECIES = 3

    toolbox = base.Toolbox()

    toolbox.register("attr_int", random.randint, 0, 0)

    toolbox.register("attribute", random.random)
    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)
    toolbox.register("individual", tools.initCycle, creator.Individual, (
    toolbox.genome, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    species = [toolbox.population(n = POP_SIZE/NUM_SPECIES) for _ in range(NUM_SPECIES)]


    target_set = []

    for x in range(len(species)):
        for member in species[x]:
            member[5] = x


    species_index = [0,1,2]
    last_index_added = species_index[-1]

    # Init with random a representative for each species
    representatives = [random.choice(species[i]) for i in range(NUM_SPECIES)]

    for specie in species:
        for member in specie:
            for rep in representatives:
                deapplaygame.playMultiRounds(member, rep)

    toolbox.register("evaluate", deapplaygame.evaluate)
    toolbox.register("mate", deapplaygame.cxOnePointGenome)
    toolbox.register("mutate", deapplaygame.mutInternalFlipBit)
    toolbox.register("select", tools.selNSGA2)

    NGEN = 5000
    CXPB = (0.9)
    MUTPB = (0.01428571)
    IMPROVEMENT_LENGTH = 5
    best_fitness_history = [None] * IMPROVEMENT_LENGTH
    next_repr = []

    for g in range(0, NGEN):
        # Initialize a container for the next generation representatives

        for specie in species:
            for member in specie:
                deapplaygame.playMultiRounds(member, representatives[0])
                deapplaygame.playMultiRounds(member, representatives[1])
                deapplaygame.playMultiRounds(member, representatives[2])
                #deapplaygame.playMultiRounds(member, representatives[3])

        for (i, s), j in zip(enumerate(species), species_index):
            # Vary the species individuals
            # create offspring
            offspring = toolbox.map(toolbox.clone, s)

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
            s.extend(offspring)
            s = toolbox.map(toolbox.clone, s)

            # Get the representatives excluding the current species
            r = representatives[:i] + representatives[i + 1:]
            fits = toolbox.map(toolbox.evaluate, s)
            for fit, ind in zip(fits, s):
                ind.fitness.values = fit


            s = toolbox.select(s, len(s) / 2)
            s = toolbox.map(toolbox.clone, s)


            # Select the individuals
            species[i] = toolbox.select(s, len(s))  # Tournament selection
            next_repr.append(tools.selBest(s, 1)[0])  # Best selection


        #next generation's test members are best of each subpopulation
        representatives = next_repr
        fits = toolbox.map(toolbox.evaluate, representatives)
        for fit, ind in zip(fits, representatives):
            ind.fitness.values = fit

        # Keep representatives fitness for stagnation detection
        best_fitness_history.pop(0)
        best_fitness_history.append(representatives[0].fitness.values[0])

        if g % 100 == 0:
            print "Generation " + str(g)


    masterlist = species[0]+species[1]+species[2]
    #masterlist = sorted(masterlist, key=lambda member: abs(member.fitness.values[0]) + abs(member.fitness.values[1]) / 2)
    masterlist = tools.selBest(masterlist, len(masterlist))
    import time
    timestr = 'coevolution/coevolution_wo_selfless_results/'
    timestr += time.strftime("%Y%m%d-%H%M%S")
    timestr += '.csv'
    deapplaygame.exportGenometoCSV(timestr, masterlist)


#call main
if __name__ == "__main__":
    main()
