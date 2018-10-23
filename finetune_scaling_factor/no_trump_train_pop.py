import numpy as np
import random
from deap import tools, base, creator, algorithms
import deapplaygame
import itertools
from matplotlib import pyplot as plt


COOPERATION_MAX = 2

def initialize_GM():
    global COOPERATION_MAX
    return COOPERATION_MAX

def increment_GM():
    COOPERATION_MAX = initialize_GM()
    COOPERATION_MAX += 1
    return COOPERATION_MAX



def main():

    CM_range = []
    selfless_count = []
    selfish_count = []
    mutualwellbeing_count = []
    coop_count = []

    creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    COOPERATION_MAX = initialize_GM()

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

    toolbox.register("evaluate", evaluate)
    #toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mate", deapplaygame.cxOnePointGenome)
    toolbox.register("mutate", deapplaygame.mutInternalFlipBitWHistory)
    toolbox.register("select", tools.selNSGA2)

    NGEN = 100
    CXPB = (0.9)
    MUTPB = (0.01428571)
    frontfreeze = NGEN *0.01
    #freezevalue = NGEN * 0.8

    for i in range(0,4):



        for pair in itertools.combinations(population, r=2):
            deapplaygame.playMultiRounds(*pair)


        # Evaluate the entire population
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        prevgen = population

        # Begin the evolution
        for g in range(1, NGEN):
            for member in population:
                member = deapplaygame.resetPlayer(member)

            for pair in itertools.combinations(population, r=2):
                deapplaygame.playMultiRounds(*pair)



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

        selfish_count.append(selfish)
        mutualwellbeing_count.append(mutual)
        coop_count.append(cooperative)
        selfless_count.append(selfless)

        global COOPERATION_MAX
        CM_range.append(COOPERATION_MAX)
        COOPERATION_MAX = increment_GM()
        print COOPERATION_MAX

    import time
    timestr = 'train_pop_no_trump/'
    timestr += time.strftime("%Y%m%d-%H%M%S")
    timestr += '.csv'
    #timestr = 'additionaltrials/trainresettest.csv'
    #deapplaygame.exportGenometoCSV(timestr, all_ind)


    colors = ['red', 'blue', 'green', 'black']
    for j in range(len(selfish_count)):
        plt.scatter([CM_range[j] for k in range(4)], [selfish_count[j], mutualwellbeing_count[j], coop_count[j], selfless_count[j]], c=colors, s=150)


    import matplotlib.patches as mpatches
    #labels for legend
    red_patch = mpatches.Patch(color=colors[0], label='Selfish')
    blue_patch = mpatches.Patch(color=colors[1], label='Communal')
    green_patch = mpatches.Patch(color=colors[2], label='Cooperative')
    black_patch = mpatches.Patch(color=colors[3], label='Selfless')
    plt.legend(handles=[red_patch, blue_patch,green_patch,black_patch])
    plt.title('Population tournament convergence as function of $\eta$')
    plt.xlabel('Scaling parameter $\eta$')
    plt.ylabel('# algorithms with given objective pair')
    plt.xlim(1,6)
    plt.ylim(0,60)
    plt.show()

def evaluate(member):
    global COOPERATION_MAX
    COOPERATION_MAX = initialize_GM()

    score1 = 0
    score2 = 0
    objectives = member[5]
    if objectives == 0:
        #maximizing personal score, min opp score
        score1 = float(member[1]) / member[4]
        score2 =  3- float(member[2]) / member[4]
    if objectives == 1:
        #max personal and opponent score
        score1 = float(member[1]) / member[4]
        score2 = float(member[2]) / member[4]
    if objectives == 2:
        #max personal score and cooperation
        score1 = float(member[1]) / member[4]
        score2 = min(float(member[3]) / member[4] * 6, COOPERATION_MAX)
    if objectives == 3:
        #max opp score and cooperation
        score1 = float(member[2]) / member[4]
        score2 = min(float(member[3]) / member[4] * 6, COOPERATION_MAX)
    return score1, score2

if __name__ == "__main__":
    main()
