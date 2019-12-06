
import csv
import random
import itertools
# from matplotlib import pyplot as plt

from deap import tools
from copy import deepcopy
import scorechange
from globals import REP, HIST3, HIST6, MARKOV, FSM, NOISE
from globals import index as i
from globals import keys

# 0 = Cooperate
# 1 = Defect

# version of representation being used:
#   0: 64 bits for decisions, 6 bits for history
#   1: lookup table: 8 decision bits; 3 history bits (opponent only)
#   2: markov process: 8 decision floats (probabilities); 3 history bits (opponent only)
#   3: markov process: 64 decision floats (probabilities); 6 history bits (opp and self)
#   4: FSM (Mealy machine)
# REP = 2

# list of representations using 3 history bits
# HIST3 = [1, 2]

# list of representations using 6 history bits
# HIST6 = [0, 3]

# list of markov representations
# MARKOV = [2, 3]

# Mealy machine representation
# FSM = 4

COOPERATION_MAX = 3


# assigns scores to the objective values depending on what the member's objectives are
def evaluate(member):
    score1 = 0
    score2 = 0
    objectives = member[i.pair]
    if objectives == 0:
        # maximizing personal score, min opp score
        score1 = float(member[i.scores][i.self]) / member[i.scores][i.games]
        # since everyone is trying to maximize objectives, minimizing opponent score
        # is the same as maximizing 3 - opp score, since 3 is generally treated as the baseline.
        score2 = 3 - float(member[i.scores][i.opp]) / member[i.scores][i.games]
    if objectives == 1:
        # max personal and opponent score
        score1 = float(member[i.scores][i.self]) / member[i.scores][i.games]
        score2 = float(member[i.scores][i.opp]) / member[i.scores][i.games]
    if objectives == 2:
        # max personal score and cooperation
        score1 = float(member[i.scores][i.self]) / member[i.scores][i.games]
        # score2 = min(float(member[i.scores][i.coop]) / member[i.scores][i.games] * 6, COOPERATION_MAX)
        score2 = float(member[i.scores][i.coop]) / member[i.scores][i.games]
    if objectives == 3:
        # max opp score and cooperation
        score1 = float(member[i.scores][i.opp]) / member[i.scores][i.games]
        # score2 = min(float(member[i.scores][i.coop]) / member[i.scores][i.games] * 6, COOPERATION_MAX)
        score2 = float(member[i.scores][i.coop]) / member[i.scores][i.games]
    return score1, score2


# in case we wanted to max personal score, min opponent score, and maximize cooperation
def evaluate_three_obj(member):
    score1 = float(member[i.scores][i.self]) / member[i.scores][i.games]
    score2 = 3 - float(member[i.scores][i.opp]) / member[i.scores][i.games]
    score3 = min(float(member[i.scores][i.coop]) / member[i.scores][i.games] * 6, COOPERATION_MAX)

    return score1, score2, score3


# used in calls to sorted to get the sort key (rather than use a lambda function)
def sort_key(member, metric):
    if metric == keys.SELF:
        return member[i.scores][i.self]
    elif metric == keys.WINS:
        return member[i.stats][i.win]
    elif metric == keys.WDL:
        return 3 * member[i.stats][i.win] + member[i.stats][i.draw]
    elif metric == keys.DRAWS:
        return member[i.stats][i.draw]
    elif metric == keys.COOP:
        return member[i.scores][i.coop]
    elif metric == keys.MUT:
        return -1 * abs(member[i.scores][i.self] - member[i.scores][i.opp])
    elif metric == keys.MATCH:
        return member[i.scores][i.match]


# used in calls to sorted to get the sort key (rather than use a lambda function)
# In this version, the member is a list containing a member of the
# population and the generation in which the member was added to
# the best_tested list.  That's the reason for the additional [0]
# index at the front of the accessors
def sort_key_best(member, metric):
    if metric == keys.SELF:
        return member[0][i.scores][i.self]
    elif metric == keys.WINS:
        return member[0][i.stats][i.win]
    elif metric == keys.WDL:
        return 3 * member[0][i.stats][i.win] + member[0][i.stats][i.draw]
    elif metric == keys.DRAWS:
        return member[0][i.stats][i.draw]
    elif metric == keys.COOP:
        return member[i.scores][i.coop]
    elif metric == keys.MUT:
        return -1 * abs(member[i.scores][i.self] - member[i.scores][i.opp])
    elif metric == keys.MATCH:
        return member[i.scores][i.match]


# initialize each player with one of four objectives uniformly.
def uniformobjectives(population):
    for counter, member in enumerate(population):
        member[i.pair] = int(counter % 4)
    return population


# initialize every player to be selfish
def uniformobjectivesSelfish(population):
    for member in population:
            member[i.pair] = 0
    return population


# initialize every player to be communal
def uniformobjectivesCommunal(population):
    for member in population:
            member[i.pair] = 1
    return population


# initialize every player to be cooperative
def uniformobjectivesCoop(population):
    for member in population:
            member[i.pair] = 2
    return population


# initialize every player to be selfless
def uniformobjectivesSelfless(population):
    for member in population:
            member[i.pair] = 3
    return population


# given an individual in FSM representation, determine
# the new state based on the current state and opponent's
# last move
def get_FSM_state(ind):
    state = ind[i.state]
    # ind[i.hist][2] is opponent most recent decision
    if ind[i.hist][2] == 0:
        return ind[i.genome][state * 4 + 1]
    else:
        return ind[i.genome][state * 4 + 2 + 1]
    

# given an individual in FSM representation, determine
# the next move based on the current state and opponent's
# last move
def get_FSM_decision(ind):
    state = ind[i.state]
    # ind[i.hist][2] is opponent most recent decision
    if ind[i.hist][2] == 0:
        return ind[i.genome][state * 4 + 1 + 1]
    else:
        return ind[i.genome][state * 4 + 3 + 1]

    
# play one round of IPD
def playround(member1, member2):
    # FSM represenation -- doesn't use history as index into list
    if REP == FSM:
        # get member1 decision
        decision1 = get_FSM_decision(member1)
        # set member1 new state
        member1[i.state] = get_FSM_state(member1)

        # get member2 decision
        decision2 = get_FSM_decision(member2)
        # set member2 new state
        member2[i.state] = get_FSM_state(member2)
            
    # history-based representations
    else:    
        # genome of decision bits
        ind1 = member1[i.genome]
        # get the index of the decision we want to make
        decisionind1 = (''.join(map(str, member1[i.hist])))
        decisionind1 = int(decisionind1, 2)

        # genome of decision bits
        ind2 = member2[i.genome]
        # get the index of the decision we want to make
        decisionind2 = (''.join(map(str, member2[i.hist])))
        decisionind2 = int(decisionind2, 2)

        if REP in MARKOV:
            # indexed value is the probability of cooperation
            decision1 = 0 if random.random() < ind1[decisionind1] else 1
            decision2 = 0 if random.random() < ind2[decisionind2] else 1
        else:           
            # the decision is the value at the above index
            decision1 = ind1[decisionind1]
            decision2 = ind2[decisionind2]

    # apply noise
    decision1 = (1 - decision1) if random.random() < NOISE else decision1
    decision2 = (1 - decision2) if random.random() < NOISE else decision2
        
    # changes both players history bits
    shift_decisions(member1[i.hist], decision2, decision1)
    shift_decisions(member2[i.hist], decision1, decision2)

    # change scores based on the outcome
    # mutual cooperation
    if decision1 == 0 and decision2 == 0:
        scorechange.mutualcooperation2(member1)
        scorechange.mutualcooperation2(member2)

    # player 1 is screwed
    elif decision1 == 0 and decision2 == 1:
        scorechange.screwed2(member1)
        scorechange.tempt2(member2)

    # player 2 is screwed
    elif decision1 == 1 and decision2 == 0:
        scorechange.tempt2(member1)
        scorechange.screwed2(member2)

    # both players defect
    else:
        scorechange.mutualdefect2(member1)
        scorechange.mutualdefect2(member2)


# change the history bits
def shift_decisions(hist, oppdec, yourdec):
    if REP in HIST6:
        # history contains 6 bits - 2 per round
        del hist[:2]
        hist.append(oppdec)
        hist.append(yourdec)
    elif REP in HIST3 or REP == FSM:
        # history contains 3 bits - 1 per round (opponent only)
        del hist[:1]
        hist.append(oppdec)


# set history bits to bits 64..69 of genome
def setHistBits(ind):
    if REP in HIST6:
        ind[i.hist] = ind[i.genome][64:70]
    elif REP in HIST3:
        ind[i.hist] = ind[i.genome][8:11]


def calc_wdl(p1, p2):
    if p1[i.scores][i.match] > p2[i.scores][i.match]:
        p1[i.stats][i.win] += 1
        p2[i.stats][i.loss] += 1
    elif p1[i.scores][i.match] < p2[i.scores][i.match]:
        p1[i.stats][i.loss] += 1
        p2[i.stats][i.win] += 1
    else:
        p1[i.stats][i.draw] += 1
        p2[i.stats][i.draw] += 1


# has the same two players against each other for multiple rounds
def playMultiRounds(ind1, ind2, numRounds=150):
    ind1[i.scores][i.match] = 0
    ind2[i.scores][i.match] = 0
    setHistBits(ind1)
    setHistBits(ind2)
    for x in range(numRounds):
        playround(ind1, ind2)

    calc_wdl(ind1, ind2)


# have player play against a member that always defects
def playroundtrump(member1):
    # get player genome
    ind1 = member1[i.genome]
    decisionind1 = (''.join(map(str, member1[i.hist])))
    decisionind1 = int(decisionind1, 2)
    # index in to see ultimate decision
    decision1 = ind1[decisionind1]

    # opponent decision is always 1
    shift_decisions(member1[i.hist], 1, decision1)

    member1[i.genome] = ind1

    # player 1 is screwed
    if decision1 == 0:
        member1 = scorechange.screwed(member1)

    # both players defect
    else:
        member1 = scorechange.mutualdefect(member1)


# a player faces a defector for numRounds times
def playMultiRoundsTrump(ind1, numRounds=150):
    setHistBits(ind1)
    for x in range(numRounds):
        playroundtrump(ind1)


# with probability indpb, flits a bit b to 1 + b % 2-- can also change the history bit
def mutInternalFlipBit(individual, indpb=float(1.0/70)):

    genome = list(tools.mutFlipBit(individual[i.genome], indpb))

    individual[i.genome] = deepcopy(genome.pop(0))


def mutMarkov(individual, prob_size, hist_size, mu, sigma, indpb1, indpb2):
    # markov genome consists of probabilities and history bits
    # these two lines store the two parts in other objects
    genome_probs = list(tools.mutGaussian(individual[i.genome][:prob_size], mu, sigma, indpb1))
    genome_hist = list(tools.mutFlipBit(individual[i.genome][prob_size:], indpb2))
    
    for k in range(prob_size):
        val = genome_probs[0][k]
        if val < 0:
            genome_probs[0][k] = -val
        elif val > 1:
            genome_probs[0][k] = 1 - (val - 1)
            
    individual[i.genome] = genome_probs[0] + genome_hist[0]


# mutation for finite state machine (Mealy machine) representation
# note that size is the number of states -- length of genome is 4 * size + 1
# format: initial_move s1_next if C s1_move if C s1_next if D s1_move if D s2_next if C s2_move if D ...
# even positions hold moves [0, 1]; odd positions hold next states [0, size)
def mutFSM(individual, size, indpb):
    for k in range(4 * size + 1):
        if random.random() < indpb:
            if k % 2 == 0:
                move = 1 - individual[i.genome][k]
                individual[i.genome][k] = move
            else:
                individual[i.genome][k] = random.randint(0, size - 1)
                

# in this function, ind1, ind2 are genomes rather than members
def cxOnePointGenome(ind1, ind2):
    # the length of the genomes
    size = min(len(ind1), len(ind2))
    # choose where to cross the individuals over
    cxpoint = random.randint(1, size - 1)
    # switches the two players at cxpoint
    ind1[cxpoint:], ind2[cxpoint:] = ind2[cxpoint:], ind1[cxpoint:]

    return ind1, ind2


# resets all score values for a player
def resetPlayer(member):
    member[i.scores][i.self] = 0
    member[i.scores][i.opp] = 0
    member[i.scores][i.coop] = 0
    member[i.scores][i.games] = 0
    member[i.scores][i.match] = 0


def load_evolved_players(population, NUM_EACH_TYPE, NUM_TYPES):
    csvfile = open('best-players-notrump.csv', 'r')
    reader = csv.reader(csvfile)

    # read evolved players from csv and put in population
    evolved_candidates = []
    for row in reader:
        evolved_candidates.append(row)

    evolved_obj_pairs = [0] * 4
    j = 0
    while j < NUM_EACH_TYPE:
        ind = random.randint(0, len(evolved_candidates) - 1)
        k = 0
        genome = []
        for k in range(70):
            genome.append(int(evolved_candidates[ind][k+1]))

        index = (NUM_TYPES - 1) * NUM_EACH_TYPE + j
        population[index][0] = deepcopy(genome)
        population[index][6] = NUM_TYPES - 1
        evolved_obj_pairs[int(evolved_candidates[ind][75])] += 1
        del evolved_candidates[ind]
        j += 1


# used to see how population size and best player scores converge with number of generations
def plotbestplayers(trials_dict, training_group=None, filename = None):
    colors = list("rgbcmyk")
    for pop_size, best_scores in trials_dict.iteritems():
        plt.scatter(range(1, len(best_scores)+1), best_scores, color=colors.pop())


    titlestr = "Increase in score of best player"
    if training_group == 'POP':
        titlestr += " when trained within population"
    if training_group == 'AX':
        titlestr += " when trained on Axelrod"

    plt.title(titlestr)
    plt.legend([ky for ky in trials_dict.iterkeys()])
    plt.xlabel('Number of generations')
    plt.ylabel('Highest self-score in population')
    plt.xlim(1, max([len(num_gens) for num_gens in trials_dict.itervalues()]))
    plt.ylim(2.5, 4)
    if filename is not None:
        plt.savefig(filename)
    # plt.show()


# build a population from a csv file
def pop_from_csv(filename):
    # the population to be returned
    pop = []

    csvfile = open(filename, 'r')
    reader = csv.reader(csvfile)

    # read players from csv and put in a list for processing
    members = []
    for row in reader:
        members.append(row)

    # identify the preamble lines in csv file and
    # read the population size
    j = 0
    while len(members[j]) < 70:
        if len(members[j]) > 0 and 'population' in members[j][0]:
            pop_size = int(members[0][0][12:])
        j += 1

    # delete the preamble lines and the lines after the last player
    # from the list
    del members[:j]
    # del members[pop_size:]

    # process the members in the list
    for m in members:
        genome = [0] * 70
        scores = [0] * 5
        stats = [0] * 3
        gradual = [0] * 6

        pos = 1
        for k in range(len(genome)):
            genome[k] = int(m[pos + k])
        history = deepcopy(genome[64:])

        pos += len(genome)
        for k in range(len(scores)):
            scores[k] = int(m[pos + k])

        pos += len(scores)
        for k in range(len(stats)):
            stats[k] = int(m[pos + k])

        pos += len(stats)
        pair = int(m[pos])

        pos += 1
        p_type = int(m[pos])

        pos += 1
        id = int(m[pos])

        indv = [genome, history, scores, stats, pair, p_type, id, gradual]
        pop.append(deepcopy(indv))
        del indv

    return pop


# write data to a CSV
# added test_pop as a parameter so that we can write data from the
# testing phase to the same csv, if there was a testing phase.
def exportPoptoCSV(filename, population, run_vars, test_pops=None, test_labels=None, best=None, counts=None):
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)

        writer.writerow(["population: " + str(run_vars[0])])
        writer.writerow(["generations: " + str(run_vars[1])])
        writer.writerow(["training: " + run_vars[2]])
        writer.writerow(["testing: " + str(run_vars[3])])
        writer.writerow(["trumps: " + str(run_vars[4])])
        writer.writerow("")
        for member in population:
            writer.writerow([''] +                                       \
            member[i.genome] +                                           \
            # [float(member[i.scores][i.self])/member[i.scores][i.games]] +                              \
            # [float(member[i.scores][i.opp])/member[i.scores][i.games]] +                              \
            # [float(member[i.scores][i.coop]) / member[i.scores][i.games]] +                            \
            member[i.scores] +                                           \
            member[i.stats] +                                            \
            [member[i.pair]] +                                           \
            [member[i.type]] +                                           \
            [member[i.id]])

        if test_pops is not None:
            k = 0
            for tp in test_pops:
                if tp is not None:
                    writer.writerow("")
                    writer.writerow("")
                    writer.writerow(["Testing:"])
                    writer.writerow([test_labels[k]])
                    for member in tp:
                        writer.writerow([''] +                                            \
                        member[i.genome]+                                                  \
                        [float(member[i.scores][i.self])/member[i.scores][i.games]] +                              \
                        [float(member[i.scores][i.opp])/member[i.scores][i.games]] +                              \
                        # [ min(6* float(member[3])/member[4], COOPERATION_MAX)] +    \
                        [float(member[i.scores][i.coop]) / member[i.scores][i.games]] +                            \
                        [member[i.scores][i.games]] +                                               \
                        [member[i.pair]] +                                               \
                        [member[i.type]])
                k += 1

        if best is not None:
            writer.writerow("")
            writer.writerow("")
            writer.writerow(["Best Tested Members:"])
            # member in this context is a list consisting of [individual, generation]
            for member in best:
                writer.writerow([member[1]] +                                            \
                member[0][i.genome] +                                                  \
                [float(member[0][i.scores][i.self])/member[0][i.scores][i.games]] +                              \
                [float(member[0][i.scores][i.opp])/member[0][i.scores][i.games]] +                              \
                # [ min(6* float(member[3])/member[4], COOPERATION_MAX)] +    \
                [float(member[0][i.scores][i.coop]) / member[0][i.scores][i.games]] +                            \
                [member[0][i.scores][i.games]] +                                               \
                [member[0][i.pair]] +                                               \
                [member[0][i.type]])


        if counts is not None:
            writer.writerow("")
            writer.writerow("")
            writer.writerow(["Objective Pair Counts for each Testing Phase:"])
            for e in counts:
                writer.writerow([''] + e)


# write data to a CSV
# This is for the writing the collection of best members throughout the run
# to a separate CSV to ease importing for later testing
def exportBesttoCSV(filename, population, run_vars, num_members):
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)

        writer.writerow(["population: " + str(num_members)])
        writer.writerow(["generations: " + str(run_vars[1])])
        writer.writerow(["training: " + run_vars[2]])
        writer.writerow(["testing: " + str(run_vars[3])])
        writer.writerow(["trumps: " + str(run_vars[4])])
        writer.writerow("")
        for member in population:
            # member in this context is a list consisting of [individual, generation]
            writer.writerow([''] + \
            member[0][i.genome] + \
            member[0][i.scores] + \
            member[0][i.stats] + \
            [member[0][i.pair]] + \
            [member[0][i.type]] + \
            [member[0][i.id]] + \
            [member[1]])
