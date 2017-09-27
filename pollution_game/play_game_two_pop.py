from deap import tools
import random
import itertools

# Decisions:
# 0 = Abate
# 1 = Pollute

ABATE_COST = [-170, -100]       # denoted c in McGinty
POLLUTE_COST = 1
ABATE_BENEFIT = [1, 2]          # denoted d in McGinty
POLLUTE_BENEFIT = [4, 3]        # denoted b in McGinty


def evaluate(member):

    # score1 = float(member[2])
    # score2 = float(member[3])

    # return score1, score2
    return member[3],


'''
def uniformobjectives(population):
    x = 0
    for member in population:
        member[5] = int(x%4)
        x += 1
    return population

def uniformobjectivesSelfish(population):
    for member in population:
            member[5] = 0

    return population
'''


# multiobjective version
def update_score_multi(member, dec, greens, pop_size, GREEN_THRESHOLD):
    # cost for going green
    if dec == 0:
        member[2] += ABATE_COST
    # update cumulative cost
    member[4] += member[2]
    # update cumulative benefit
    member[5] += member[3]
    # penalty of 1 for each member that defected
    member[2] += (pop_size - greens) * POLLUTE_COST
    # benefit if enough nations go green
    member[3] += ((greens >= (GREEN_THRESHOLD * pop_size)) * ABATE_BENEFIT)
    # increment number of rounds
    member[6] += 1

    return member


# single objective version
# score as defined by:
#   Matthew McGinty, IEA as Evo Games,
#   Environmental Resource Economics (2010) 45:251-269
def update_score_single(member, dec, greens):
    i = member[7]
    # objective value is:
    #   (benefit * #_of_abaters) - cost_of_abate (if individual abates)
    if dec == 0:
        score = ABATE_BENEFIT[0] * greens[0] + ABATE_BENEFIT[1] * greens[1] - ABATE_COST[i]
    else:
        score = POLLUTE_BENEFIT[i] * (greens[0] + greens[1])

    member[3] += score

    # number of rounds
    member[6] += 1

    return score


def get_alt_score(member, dec, greens):
    i = member[7]
    alt_dec = 1 - dec

    if alt_dec == 0:
        alt_score = ABATE_BENEFIT[0] * (greens[0] + (1 - i)) + ABATE_BENEFIT[1] * (greens[1] + i) - ABATE_COST[i]
    else:
        alt_score = POLLUTE_BENEFIT[i] * (greens[0] + greens[1] - 1)

    return alt_score


def shift_decisions(history, dec, group_dec):
    history = history[2:]
    history.append(group_dec)
    history.append(dec)

    return history


def shift_decisions_single(history, dec):
    history = history[1:]
    history.append(dec)

    return history


def playround_trend(pop0, pop1, prev_greens):

    green_count = [0, 0]
    decision_list = []

    for nation in pop0:
        nat_hist = ''.join(map(str, nation[1]))
        index = int(nat_hist, 2)
        decision = nation[0][index]
        green_count[0] += (1 - decision)
        decision_list.append(decision)

    for nation in pop1:
        nat_hist = ''.join(map(str, nation[1]))
        index = int(nat_hist, 2)
        decision = nation[0][index]
        green_count[1] += (1 - decision)
        decision_list.append(decision)

    trend = 0
    total_greens = green_count[0] + green_count[1]
    trend += (total_greens > prev_greens)

    for i, nation in enumerate(pop0):
        nat_hist = nation[1]
        nat_hist = shift_decisions(nat_hist, decision_list[i], trend)
        nation[1] = nat_hist
        nation = update_score_single(nation, decision_list[i], green_count)

    for i, nation in enumerate(pop1):
        nat_hist = nation[1]
        nat_hist = shift_decisions(nat_hist, decision_list[i], trend)
        nation[1] = nat_hist
        nation = update_score_single(nation, decision_list[i], green_count)

    return total_greens


def playround_threshold(pops, gen):
    green_count = [0, 0]
    decision_list = []

    i = 0
    for p in pops:
        for nation in p:
            nat_hist = ''.join(map(str, nation[1]))
            index = int(nat_hist, 2)
            decision = nation[0][index]
            green_count[i] += (1 - decision)
            decision_list.append(decision)
        i += 1

    base = 0.1
    delta = 0.025
    if gen == -1:
        pct = 0.9
    else:
        pct = (gen/100) * delta + base

    thresh = 0
    total_greens = green_count[0] + green_count[1]
    if total_greens >= pct * (len(pops[0]) + len(pops[1])):
        thresh = 1

    for p in pops:
        for i, nation in enumerate(p):
            nat_hist = nation[1]
            nat_hist = shift_decisions(nat_hist, decision_list[i], thresh)
            nation[1] = nat_hist
            update_score_single(nation, decision_list[i], green_count)


def playround_alt_score(pops, gen):
    green_count = [0, 0]
    decision_list = [[], []]

    for i, p in enumerate(pops):
        for nation in p:
            nat_hist = ''.join(map(str, nation[1]))
            index = int(nat_hist, 2)
            decision = nation[0][index]
            green_count[i] += (1 - decision)
            decision_list[i].append(decision)

    for i, p in enumerate(pops):
        for j in range(len(p)):
            alt_score = get_alt_score(p[j], decision_list[i][j], green_count)
            score = update_score_single(p[j], decision_list[i][j], green_count)
            other_bit = int(alt_score > score)
            nat_hist = p[j][1]
            nat_hist = shift_decisions(nat_hist, decision_list[i][j], other_bit)
            p[j][1] = nat_hist


def playround_history_single(pops):
    green_count = [0, 0]
    decision_list = []

    for p in pops:
        for i, nation in enumerate(p):
            nat_hist = ''.join(map(str, nation[1]))
            index = int(nat_hist, 2)
            decision = nation[0][index]
            green_count[i] += (1 - decision)
            decision_list.append(decision)
            nat_hist = shift_decisions_single(nat_hist, decision)
            nation[1] = nat_hist


def playMultiRounds(pops, generation, numRounds=150):
    # reset decisions for each generation so that only results
    # with the current genome are included
    for p in pops:
        for member in p:
            resetPlayer(member)

    # number of abaters in previous round
    # this is used to determine the trend
    prev_greens = 0
    for x in range(numRounds):
        # prev_greens = playround_trend(pop0, pop1, prev_greens)
        playround_alt_score(pops, generation)


def calculate_threshold(current_val, gens):
    new_val = current_val * 1.5**(gens/250)
    if new_val > 0.5:
        return 0.5
    else:
        return new_val


def mutInternalFlipBit(individual, indpb=0.1):
    decisionSlice = individual[0][64:]
    genome = (individual[0][0:64])
    genome = (list)(tools.mutFlipBit(genome, indpb))

    fullGen = genome[0] + decisionSlice
    individual[0] = fullGen
    #individual[0] = individual[0].pop(0)

    return individual, #comma here


def mutInternalFlipBitWHistory(individual, indpb=0.1):

    genome = (list)(tools.mutFlipBit(individual[0], indpb))

    individual[0] = genome
    individual[0] = individual[0].pop(0)

    return individual,  # comma here


def cxOnePointGenome(ind1, ind2):
    """Executes a one point crossover on the input :term:`sequence` individuals.
    The two individuals are modified in place. The resulting individuals will
    respectively have the length of the other.

    :param ind1: The first individual participating in the crossover.
    :param ind2: The second individual participating in the crossover.
    :returns: A tuple of two individuals.
    This function uses the :func:`~random.randint` function from the
    python base :mod:`random` module.
    """

    size = min(len(ind1), len(ind2))
    cxpoint = random.randint(1, size - 1)
    ind1[cxpoint:], ind2[cxpoint:] = ind2[cxpoint:], ind1[cxpoint:]

    return ind1, ind2


def resetPlayer(member):
    member[2] = 0
    member[3] = 0
    member[6] = 0
    return member


def set_type(s):
    return s


def exportGenometoCSV(filename, population):
    import csv
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)

        for member in population:
            writer.writerow(member[0] +[float(member[1])/member[4]] + [float(member[2])/member[4]] + [ min(6* float(member[3])/member[4], 5)] + [member[4]] +[member[5]])


def exportGenometoCSVLOO(filename, population, testedPlayer):
    import csv
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)

        x = 0
        for member in population:
            writer.writerow(member[0] +[float(member[1])/member[4]] + [float(member[2])/member[4]] + [ 6* float(member[3])/member[4]] + [member[4]] +[member[5]] + [testedPlayer[x]])
            x += 1
