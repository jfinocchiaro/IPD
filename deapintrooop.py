import random
from deap import tools, base, creator
import playgame
import individuals

creator.create("FitnessMulti", base.Fitness, weights=(1.0,1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)

IND_SIZE = 72
POP_SIZE = 60


toolbox = base.Toolbox()
toolbox.register("attribute", random.random)
toolbox.register("bit", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.bit, IND_SIZE)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)
population = toolbox.population(n=POP_SIZE)

ind1 = toolbox.individual()
ind2 = toolbox.individual()

indiv1 = individuals.member(ind1)
indiv2 = individuals.member(ind2)


print indiv1.individual

playgame.evaluate(indiv1)
playgame.playround(indiv1, indiv2)


print indiv1.personalscore