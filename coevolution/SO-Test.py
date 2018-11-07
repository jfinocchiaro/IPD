import time
import numpy as np
import random
from copy import deepcopy
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

    #global-ish variables won't be changed
    IND_SIZE = 70
    POP_SIZE = 60
    NGEN = 1000
    CXPB = 0.9

    run_info = [POP_SIZE, NGEN, TRAINING_GROUP]
    
    rseed = os.getpid() * (time.time() % 4919)
    random.seed(rseed)
    print("\n\nRandom seed: {}\n".format(rseed))

    toolbox = base.Toolbox()
    toolbox.register("attr_int", random.randint, 0 , 0)
    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)

    # fields in individual:
    #   0: genome
    #   1: self score
    #   2: opponent score
    #   3: cooperation score
    #   4: number of games
    #   5: objective pair
    #   6: id
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome,                           toolbox.attr_int,toolbox.attr_int,toolbox.attr_int,toolbox.attr_int,                         toolbox.attr_int,toolbox.attr_int), n=1)
    
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # 4 subpopulations
    selfish_population = toolbox.population(n=POP_SIZE / 4)
    communal_population = toolbox.population(n=POP_SIZE / 4)
    cooperative_population = toolbox.population(n=POP_SIZE / 4)
    selfless_population = toolbox.population(n=POP_SIZE / 4)
    
    # assign ids to the members
    n = POP_SIZE/4
    i = 0
    while i < n:
        selfish_population[i][6] = i
        communal_population[i][6] = n + i
        cooperative_population[i][6] = 2 * n + i
        selfless_population[i][6] = 3 * n + i
        i += 1
    
    # set an id variable to use for assigning ids to offspring
    id = POP_SIZE

    #make initial objectives of population uniformly distributed
    selfish_population = deapplaygame.uniformobjectivesSelfish(selfish_population)
    communal_population = deapplaygame.uniformobjectivesCommunal(communal_population)
    cooperative_population = deapplaygame.uniformobjectivesCoop(cooperative_population)
    selfless_population = deapplaygame.uniformobjectivesSelfless(selfless_population)

    toolbox.register("evaluate", deapplaygame.evaluate)
    toolbox.register("mate", deapplaygame.cxOnePointGenome)
    toolbox.register("mutate", deapplaygame.mutInternalFlipBitWHistoryNoObjChange)
    toolbox.register("select", tools.selNSGA2)


    #conducts round-robin, depending on who's the training population
    if TRAINING_GROUP == 'POP':
        for pair in itertools.combinations(selfish_population + communal_population + cooperative_population + selfish_population, r=2):
            deapplaygame.playMultiRounds(*pair)
    elif TRAINING_GROUP == 'AX':
        axelrodPop = axelrodplayers.initAxpop()
        for population in [selfish_population, communal_population, cooperative_population, selfless_population]:
            for member in population:
                for opponent in axelrodPop:
                    axelrodplayers.playAxelrodPop(member, opponent)
    else:
        print 'Invalid training group- please fix.'
        quit()


    # Evaluate each population
    for population in [selfish_population, communal_population, cooperative_population, selfish_population]:
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit




    print "About to start evolution"
    # Begin the evolution
    for g in range(1, NGEN):
        #SELFISH
        for member in selfish_population:
            member = deapplaygame.resetPlayer(member)


        # create offspring
        offspring = toolbox.map(toolbox.clone, selfish_population)
        
        for i in range(len(offspring)):
            offspring[i][6] = id
            id += 1

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
        selfish_population.extend(offspring)
        selfish_population = toolbox.map(toolbox.clone, selfish_population)

        #COMMUNAL
        for member in communal_population:
            member = deapplaygame.resetPlayer(member)


        # create offspring
        offspring = toolbox.map(toolbox.clone, communal_population)

        for i in range(len(offspring)):
            offspring[i][6] = id
            id += 1

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
        communal_population.extend(offspring)
        communal_population = toolbox.map(toolbox.clone, communal_population)


        #COOPERATIVE
        for member in cooperative_population:
            member = deapplaygame.resetPlayer(member)


        # create offspring
        offspring = toolbox.map(toolbox.clone, cooperative_population)

        for i in range(len(offspring)):
            offspring[i][6] = id
            id += 1

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
        cooperative_population.extend(offspring)
        cooperative_population = toolbox.map(toolbox.clone, cooperative_population)


        #SELFLESS
        for member in selfless_population:
            member = deapplaygame.resetPlayer(member)


        # create offspring
        offspring = toolbox.map(toolbox.clone, selfless_population)

        for i in range(len(offspring)):
            offspring[i][6] = id
            id += 1

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
        selfless_population.extend(offspring)
        selfless_population = toolbox.map(toolbox.clone, selfless_population)


        #conducts round-robin, depending on who's the training population
        if TRAINING_GROUP == 'POP':
            for pair in itertools.combinations(selfish_population + communal_population + cooperative_population + selfless_population, r=2):
                deapplaygame.playMultiRounds(*pair)
        elif TRAINING_GROUP == 'AX':
            for population in [selfish_population, communal_population, cooperative_population, selfless_population]:
                for member in population:
                    for opponent in axelrodPop:
                        axelrodplayers.playAxelrodPop(member, opponent)
        else:
            print 'Invalid training group- please fix.'
            quit()


        #SELFISH
        #evaluate how well players did
        fits = toolbox.map(toolbox.evaluate, selfish_population)
        for fit, ind in zip(fits, selfish_population):
            ind.fitness.values = fit


        # survival of the fittest- uses NSGA-II
        selfish_population = toolbox.select(selfish_population, POP_SIZE/4)
        selfish_population = toolbox.map(toolbox.clone, selfish_population)


        #COMMUNAL
        #evaluate how well players did
        fits = toolbox.map(toolbox.evaluate, communal_population)
        for fit, ind in zip(fits, communal_population):
            ind.fitness.values = fit


        # survival of the fittest- uses NSGA-II
        communal_population = toolbox.select(communal_population, POP_SIZE/4)
        communal_population = toolbox.map(toolbox.clone, communal_population)


        #COOPERATIVE
        #evaluate how well players did
        fits = toolbox.map(toolbox.evaluate, cooperative_population)
        for fit, ind in zip(fits, cooperative_population):
            ind.fitness.values = fit


        # survival of the fittest- uses NSGA-II
        cooperative_population = toolbox.select(cooperative_population, POP_SIZE/4)
        cooperative_population = toolbox.map(toolbox.clone, cooperative_population)


        #SELFLESS
        #evaluate how well players did
        fits = toolbox.map(toolbox.evaluate, selfless_population)
        for fit, ind in zip(fits, selfless_population):
            ind.fitness.values = fit


        # survival of the fittest- uses NSGA-II
        selfless_population = toolbox.select(selfless_population, POP_SIZE/4)
        selfless_population = toolbox.map(toolbox.clone, selfless_population)



        #for progress updates
        if g % 50 == 0:
            print("-- Generation %i --" % g)



    print("-- End of evolution --")



    #print outcome of evolution
    print ("%s total individuals in each population" % len(selfish_population))
    #all_ind = tools.selBest(population, (len(population)))
    sorted_selfish = sorted(selfish_population, key=lambda member: (abs(member.fitness.values[0]) + abs(member.fitness.values[1])) / 2)
    sorted_communal = sorted(communal_population, key=lambda member: (abs(member.fitness.values[0]) + abs(member.fitness.values[1])) / 2)
    sorted_cooperative = sorted(cooperative_population, key=lambda member: (abs(member.fitness.values[0]) + abs(member.fitness.values[1])) / 2)
    sorted_selfless = sorted(selfless_population, key=lambda member: (abs(member.fitness.values[0]) + abs(member.fitness.values[1])) / 2)
    all_ind = sorted_selfish + sorted_communal + sorted_cooperative + sorted_selfless

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


    # test_pop = []
    # test_pop.append(deepcopy(sorted_selfish[len(sorted_selfish)-1]))
    # test_pop.append(deepcopy(sorted_communal[len(sorted_communal)-1]))
    # test_pop.append(deepcopy(sorted_cooperative[len(sorted_cooperative)-1]))
    # test_pop.append(deepcopy(sorted_selfless[len(sorted_selfless)-1]))
    
    # test_pop will be used in the testing phase against Axelrod
    test_pop = deepcopy(all_ind)
    
    # reset the scores for the test_pop
    for member in test_pop:
        deapplaygame.resetPlayer(member)

    # play against Axelrod -- 150 rounds for each member-opponent pair
    axelrodPop = axelrodplayers.initAxpop()
    for member in test_pop:
        for opponent in axelrodPop:
            axelrodplayers.playAxelrodPop(member, opponent)

    # sort the test_pop by decreasing value of self score
    # testing is single objective - self score only
    # to use cooperation as single objective: change member[1] to member[3]
    sorted_test_self = sorted(test_pop, key=lambda member: member[1], reverse=True)
    sorted_test_opp = sorted(test_pop, key=lambda member: member[2], reverse=True)
    # sorted_test_opp = None
    sorted_test_coop = sorted(test_pop, key=lambda member: member[3], reverse=True)
    # sorted_test_coop = None

    # flags for which test objectives to log in csv file
    #     test_pops[0]: self score
    #     test_pops[1]: opppnent score
    #     test_pops[2]: cooperation
    # set position to None to exclude
    test_pops = [1, None, None]
    
    # labels to print for each of the tests
    test_labels = ["Self Score", "Opp Score", "Cooperation"]
    
    # number of members to display after testing
    m = 20
    
    # for the test objectives indicated in test_pops
    # grab just the top m test_pop members for writing to the csv file
    if test_pops[0] is not None:
        if len(sorted_test_self) > m:
            sorted_test_self = sorted_test_self[:m]
        test_pops[0] = sorted_test_self

    if test_pops[1] is not None:
        if len(sorted_test_opp) > m:
            sorted_test_opp = sorted_test_opp[:m]
        test_pops[1] = sorted_test_opp

    if test_pops[2] is not None:
        if len(sorted_test_coop) > m:
            sorted_test_coop = sorted_test_coop[:m]
        test_pops[2] = sorted_test_coop

    # write to csv file
    if TRAINING_GROUP == 'POP':
        timestr = 'train_pop/'
    else:
        timestr = 'train_axelrod/'
    timestr += time.strftime("%Y%m%d-%H%M%S")
    timestr += '-{}'.format(os.getpid())
    timestr += '.csv'
    deapplaygame.exportGenometoCSV(timestr, all_ind, run_info, test_pops, test_labels)

if __name__ == "__main__":
    main()
