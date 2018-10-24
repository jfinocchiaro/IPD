import time
import numpy as np
import random
from deap import tools, base, creator, algorithms
import deapplaygame
import itertools
import os
import axelrodplayers

def main():

    creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    #change this depending on the desired trial
    TRAINING_GROUP = 'POP' #change to 'AX' for training against Axelrod, or 'POP' to train within population

    #global-iah variables won't be changed
    IND_SIZE = 70
    POP_SIZE = 60
    NGEN = 250
    CXPB = 0.9

    rseed = os.getpid() * (time.time() % 4919)
    random.seed(rseed)
    print("Random seed: {}\n".format(rseed))
    
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
    toolbox.register("mate", deapplaygame.cxOnePointGenome)
    toolbox.register("mutate", deapplaygame.mutInternalFlipBitWHistory)
    toolbox.register("select", tools.selNSGA2)


    #conducts round-robin, depending on who's the training population
    if TRAINING_GROUP == 'POP':
        for pair in itertools.combinations(population, r=2):
            deapplaygame.playMultiRounds(*pair)
    elif TRAINING_GROUP == 'AX':
        axelrodPop = axelrodplayers.initAxpop()
        for member in population:
            for opponent in axelrodPop:
                axelrodplayers.playAxelrodPop(member, opponent)
    else:
        print 'Invalid training group- please fix.'
        quit()


    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    prevgen = population

    # Begin the evolution
    for g in range(1, NGEN):
        for member in population:
            member = deapplaygame.resetPlayer(member)

        #conducts round-robin, depending on who's the training population
        if TRAINING_GROUP == 'POP':
            for pair in itertools.combinations(population, r=2):
                deapplaygame.playMultiRounds(*pair)
        elif TRAINING_GROUP == 'AX':
            for member in population:
                for opponent in axelrodPop:
                    axelrodplayers.playAxelrodPop(member, opponent)
        else:
            print 'Invalid training group- please fix.'
            quit()


        # create offspring
        offspring = toolbox.map(toolbox.clone, population)

        # crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            #mates with probability 0.9
            if random.random() < CXPB:
                toolbox.mate(child1[0], child2[0])
                del child1.fitness.values
                del child2.fitness.values
        # mutation
        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values


        # create combined population
        population.extend(offspring)
        population = toolbox.map(toolbox.clone, population)


        #conducts round-robin, depending on who's the training population
        if TRAINING_GROUP == 'POP':
            for pair in itertools.combinations(population, r=2):
                deapplaygame.playMultiRounds(*pair)
        elif TRAINING_GROUP == 'AX':
            for member in population:
                for opponent in axelrodPop:
                    axelrodplayers.playAxelrodPop(member, opponent)
        else:
            print 'Invalid training group- please fix.'
            quit()



        #evaluate how well players did
        fits = toolbox.map(toolbox.evaluate, population)
        for fit, ind in zip(fits, population):
            ind.fitness.values = fit


        # survival of the fittest- uses NSGA-II
        population = toolbox.select(population, POP_SIZE)
        population = toolbox.map(toolbox.clone, population)

        #for progress updates
        if g % 50 == 0:
            print("-- Generation %i --" % g)



    print("-- End of evolution --")



    #print outcome of evolution
    print ("%s total individuals in population" % len(population))
    all_ind = tools.selBest(population, (len(population)))
    all_ind = sorted(population, key=lambda member: abs(member.fitness.values[0]) + abs(member.fitness.values[1]) / 2)
    for member in all_ind:
        print member

    #prints summary of objective outcomes
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


    print "Selfish:  " + str(selfish)
    print "Mutual well-being:  " + str(mutual)
    print "Mutual cooperation:  " + str(cooperative)
    print "Selfless:  " + str(selfless)

    if TRAINING_GROUP == 'POP':
        timestr = 'train_pop/'
    else:
        timestr = 'train_axelrod/'
    timestr += time.strftime("%Y%m%d-%H%M%S")
    timestr += '-{}'.format(os.getpid())
    timestr += '.csv'
    deapplaygame.exportGenometoCSV(timestr, all_ind)


if __name__ == "__main__":
    main()
