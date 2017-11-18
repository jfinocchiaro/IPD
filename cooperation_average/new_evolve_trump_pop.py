import numpy as np
import random
from deap import tools, base, creator, algorithms
import deapplaygame
import itertools

def main():
    creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)


    IND_SIZE = 70
    POP_SIZE = 60


    toolbox = base.Toolbox()


    toolbox.register("attr_int", random.randint, 0 , 0)



    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.attr_int,toolbox.attr_int,toolbox.attr_int,toolbox.attr_int, toolbox.attr_int), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    population = toolbox.population(n=POP_SIZE)


    #make initial objectives of population uniformly distributed
    population = deapplaygame.uniformobjectives(population)

    toolbox.register("evaluate", deapplaygame.evaluate)
    #toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mate", deapplaygame.cxOnePointGenome)
    toolbox.register("mutate", deapplaygame.mutInternalFlipBitWHistory)
    toolbox.register("select", tools.selNSGA2)

    NGEN = 2500
    CXPB = (0.9)
    MUTPB = (0.01428571)
    frontfreeze = NGEN *0.01
    #freezevalue = NGEN * 0.8


    # Begin the evolution
    for g in range(1, NGEN):

        for member in population:
            member = deapplaygame.resetPlayer(member)

        for pair in itertools.combinations(population, r=2):
            deapplaygame.playMultiRounds(*pair)


        for member in population:
            for x in range(60):
                deapplaygame.playMultiRoundsTrump(member)






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


        for pair in itertools.combinations(population, r=2):
            deapplaygame.playMultiRounds(*pair)


        for member in population:
            for x in range(60):
                deapplaygame.playMultiRoundsTrump(member)


        fits = toolbox.map(toolbox.evaluate, population)
        for fit, ind in zip(fits, population):
            ind.fitness.values = fit


        # survival of the fittest
        population = toolbox.select(population, POP_SIZE)
        population = toolbox.map(toolbox.clone, population)



        if g % 100 == 0:
            print("-- Generation %i --" % g)




    print("-- End of evolution --")



    #print outcome of evolution
    print ("%s total individuals in population" % len(population))
    all_ind = tools.selBest(population, (len(population)))
    #all_ind = sorted(population, key=lambda member: abs(member.fitness.values[0]) + abs(member.fitness.values[1]) / 2)
    for member in all_ind:
        print member

    selfish = 0
    cooperative = 0
    selfless = 0
    mutual = 0


    for x in range(len(all_ind)):
        objectives = all_ind[x][5]
        if objectives == 0:
            selfish += 1
        elif objectives == 1:
            mutual += 1
        elif objectives == 2:
            cooperative += 1
        elif objectives == 3:
            selfless += 1
        #print("%s, %s" % (all_ind[x], all_ind[x].fitness.values))

    print "Selfish:  " + str(selfish)
    print "Mutual well-being:  " + str(mutual)
    print "Mutual cooperation:  " + str(cooperative)
    print "Selfless:  " + str(selfless)


    import time
    #timestr = 'newevolutionfreeobjs/'
    timestr = time.strftime("%Y%m%d-%H%M%S")
    timestr += '.csv'
    #timestr = 'additionaltrials/trainresettest.csv'
    deapplaygame.exportGenometoCSV(timestr, all_ind)


if __name__ == "__main__":
    main()
