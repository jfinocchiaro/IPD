
import random
import os
import time

from deap import tools, base, creator

from globals import REP, TABLE_SIZE, HIST_SIZE, FSM_STATES


# takes a list of functions -- one that creates a list of probabilities
# and one that creates a list of bits -- runs them and returns a single
# list that is their concatenation
def make_markov_genome(f_list):
    return f_list[0]() + f_list[1]()


def make_fsm_genome(f_list, num_states):
    g = []
    g.append(f_list[1]())
    for _ in range(num_states):
        g.append(f_list[0]())
        g.append(f_list[1]())
        g.append(f_list[0]())
        g.append(f_list[1]())

    return g


def make_types():
    rseed = int(os.getpid() * (time.time() % 7589))
    random.seed(rseed)
    # print("\n\nRandom seed: {}\n".format(rseed))

    # when running from multi_rr, this try avoids redeclaration errors
    # the check for in dir() doesn't do anything - accessing creator.FitnessSingle
    # if it doesn't exist gives an AttributeError which we are catching
    try:
        creator.FitnessSingle in dir()
    except AttributeError:
        creator.create("FitnessSingle", base.Fitness, weights=(1.0,))
        creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))
        creator.create("Indv_multi", list, fitness=creator.FitnessMulti)
        creator.create("Indv_single", list, fitness=creator.FitnessSingle)

    # global-ish variables won't be changed
    IND_SIZE = 70

    toolbox = base.Toolbox()
    toolbox.register("attr_int", random.randint, 0, 0)
    toolbox.register("bit", random.randint, 0, 1)
    toolbox.register("state", random.randint, 0, FSM_STATES - 1)
    toolbox.register("init_state", random.randint, 0, 0)        # init state always 0
    toolbox.register("prob", random.random)
    toolbox.register("prob_list", tools.initRepeat, list, toolbox.prob, TABLE_SIZE)
    toolbox.register("rep", random.randint, REP, REP)

    markov_func_list = [lambda: toolbox.prob_list(), lambda: toolbox.history()]
    fsm_func_list = [lambda: toolbox.state(), lambda: toolbox.bit()]
    toolbox.register("binary_genome", tools.initRepeat, list, toolbox.bit, TABLE_SIZE + HIST_SIZE)
    toolbox.register("markov_genome", make_markov_genome, markov_func_list)
    toolbox.register("fsm_genome", make_fsm_genome, fsm_func_list, FSM_STATES)

    # history bits:
    #   xyxyxy
    #   each xy is: opp_decision self_decision
    #   left pair is oldest, right is most recent
    toolbox.register("history", tools.initRepeat, list, toolbox.bit, HIST_SIZE)

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
    #   8: state (for FSM representation only)
    if REP == 0:
        toolbox.register("indv_multi", tools.initCycle, creator.Indv_multi, (toolbox.binary_genome, 
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.state, toolbox.rep), n=1)

        toolbox.register("indv_single", tools.initCycle, creator.Indv_single, (toolbox.binary_genome,
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.state, toolbox.rep), n=1)
    if REP == 1:
        toolbox.register("indv_multi", tools.initCycle, creator.Indv_multi, (toolbox.binary_genome, 
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.state, toolbox.rep), n=1)

        toolbox.register("indv_single", tools.initCycle, creator.Indv_single, (toolbox.binary_genome,
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.state, toolbox.rep), n=1)
    if REP == 2:
        toolbox.register("indv_multi", tools.initCycle, creator.Indv_multi, (toolbox.markov_genome, 
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.state, toolbox.rep), n=1)

        toolbox.register("indv_single", tools.initCycle, creator.Indv_single, (toolbox.markov_genome,
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.state, toolbox.rep), n=1)
    if REP == 3:
        toolbox.register("indv_multi", tools.initCycle, creator.Indv_multi, (toolbox.markov_genome, 
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.state, toolbox.rep), n=1)

        toolbox.register("indv_single", tools.initCycle, creator.Indv_single, (toolbox.markov_genome,
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.state, toolbox.rep), n=1)
    if REP == 4:
        toolbox.register("indv_multi", tools.initCycle, creator.Indv_multi, (toolbox.fsm_genome, 
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.init_state, toolbox.rep), n=1)

        toolbox.register("indv_single", tools.initCycle, creator.Indv_single, (toolbox.fsm_genome,
                                    toolbox.history, toolbox.scores, toolbox.stats, toolbox.attr_int, toolbox.attr_int, toolbox.attr_int, toolbox.gradual, toolbox.init_state, toolbox.rep), n=1)

    return toolbox
