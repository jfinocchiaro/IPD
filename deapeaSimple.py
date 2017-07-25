import numpy as np
import random
from deap import tools, base, creator, algorithms
import deapplaygame
import deapalgorithms

import itertools

creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)


IND_SIZE = 70
POP_SIZE = 60


toolbox = base.Toolbox()


toolbox.register("attr_int", random.randint, 0 , 0)


toolbox.register("attribute", random.random)
toolbox.register("bit", random.randint, 0, 1)
toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)
toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.attr_int,toolbox.attr_int,toolbox.attr_int,toolbox.attr_int, toolbox.attr_int), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
population = toolbox.population(n=POP_SIZE)

#make initial objectives of population uniformly distributed
population = deapplaygame.uniformobjectives(population)

toolbox.register("evaluate", deapplaygame.evaluate)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", deapplaygame.mutInternalFlipBit)
toolbox.register("select", tools.selNSGA2)

NGEN = 5000
CXPB = (.1)
MUTPB = (.015)

for pair in itertools.combinations(population, r=2):
    deapplaygame.playMultiRounds(*pair)

population = deapalgorithms.eaSimple(population, toolbox, cxpb=CXPB, mutpb=MUTPB,ngen=NGEN)

for member in population:
    print member





selfish = 0
cooperative = 0
selfless = 0
mutual = 0


for member in population:
    objectives = member[5]
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