from deap import tools
import random
import itertools

# 0 = Join pact
# 1 = Defect

# GREEN_THRESHOLD = 0.5
COOP_COST = 3
DEFECT_COST = 1
THRESHOLD_BENEFIT = 4


def evaluate(member):

    score1 = float(member[2])
    score2 = float(member[3])

    return score1, score2


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

def update_score(member, dec, greens, pop_size, GREEN_THRESHOLD):
    # cost for going green
    if dec == 0:
        member[2] += COOP_COST
    # update cumulative cost
    member[4] += member[2]
    # update cumulative benefit
    member[5] += member[3]
    # penalty of 1 for each member that defected
    member[2] += (pop_size - greens) * DEFECT_COST
    # benefit if enough nations go green
    member[3] += ((greens >= (GREEN_THRESHOLD * pop_size)) * THRESHOLD_BENEFIT)
    # increment number of rounds
    member[6] += 1

    return member


def shift_decisions(history, dec, group_dec):
    history[0:2] = history[2:4]
    history[2:4] = history[4:6]
    history[4] = group_dec
    history[5] = dec

    return history


def playround(population, GREEN_THRESHOLD):

    green_count = 0
    decision_list = []

    for nation in population:
        nat_hist = ''.join(map(str, nation[1]))
        # print nat_hist
        # print len(nat_gene)
        index = int(nat_hist, 2)
        decision = nation[0][index]
        green_count += (1 - decision)
        decision_list.append(decision)

    coop = 0
    if green_count >= (GREEN_THRESHOLD * len(population)):
        coop += 1

    for i, nation in enumerate(population):
        nat_hist = nation[1]
        nat_hist = shift_decisions(nat_hist, decision_list[i], coop)
        nation[1] = nat_hist
        nation = update_score(nation, decision_list[i], green_count, len(population), GREEN_THRESHOLD)


def playMultiRounds(population, GREEN_THRESHOLD, numRounds=150):
    for member in population:
        resetPlayer(member)

    for x in range(numRounds):
        playround(population, GREEN_THRESHOLD)


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
