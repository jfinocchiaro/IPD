
from deap import tools, base, creator
import random
import os
import time


def make_types():
    rseed = int(os.getpid() * (time.time() % 7589))
    random.seed(rseed)
    print("\n\nRandom seed: {}\n".format(rseed))

    creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
    creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))
    creator.create("Indv_multi", list, fitness=creator.FitnessMulti)
    creator.create("Indv_single", list, fitness=creator.FitnessSingle)

    # global-ish variables won't be changed
    IND_SIZE = 70

    toolbox = base.Toolbox()
    toolbox.register("attr_int", random.randint, 0, 0)
    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)

    # history bits:
    #   xyxyxy
    #   each xy is: opp_decision self_decision
    #   left pair is oldest, right is most recent
    toolbox.register("history", tools.initRepeat, list, toolbox.bit, 6)

    # fields in scores:
    #   0: self score
    #   1: opponent score
    #   2: cooperation score
    #   3: number of games
    #   4: score this match (each match is some number of games)
    toolbox.register("scores", tools.initRepeat, list, toolbox.attr_int, 5)

    # fields in stats:
    #   0: matches won
    #   1: matches drawn
    #   2: matches lost
    toolbox.register("stats", tools.initRepeat, list, toolbox.attr_int, 3)

    # fields for gradual players:
    #   0: opponent last play
    #   1: opponent defects
    #   2: defect flag
    #   3: self consecutive defects
    #   4: coop flag
    #   5: coop count
    toolbox.register("gradual", tools.initRepeat, list, toolbox.attr_int, 6)

    # fields in individual:
    #   0: genome
    #   1: history (last 3 moves -- history in genome is only for start of game)
    #   2: scores
    #   3: stats
    #   4: objective pair
    #   5: player type
    #   6: id
    #   7: gradual fields (for gradual players only)
    toolbox.register("indv_multi", tools.initCycle, creator.Indv_multi, (toolbox.genome, toolbox.history,
                                    toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int,
                                    toolbox.attr_int, toolbox.gradual), n=1)

    toolbox.register("indv_single", tools.initCycle, creator.Indv_single, (toolbox.genome, toolbox.history,
                                    toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int,
                                    toolbox.attr_int, toolbox.gradual), n=1)

    return toolbox
