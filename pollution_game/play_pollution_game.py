from deap import tools
import random
import itertools

# 0 = Join pact
# 1 = Defect

GREEN_THRESHOLD = 0.8
COOP_COST = 3
DEFECT_COST = 1
THRESHOLD_BENEFIT = 2


def evaluate(member):

    score1 = float(member[1]) / member[4]
    score2 = float(member[2]) / member[4]

    return score1, score2


def evaluate_three_obj(member):
    score1 = float(member[1]) / member[4]
    score2 = float(-member[2]) / member[4]
    score3 = min(float(member[3]) / member[4] * 6, 5)

    return score1, score2, score3

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

def update_score(member, dec, greens, pop_size):
    # cost for going green
    if dec == 0:
        member[1] += 3
    # penalty of 1 for each member that defected
    member[1] += pop_size - greens
    # benefit if enough nations go green
    member[2] += (greens > GREEN_THRESHOLD * pop_size) * THRESHOLD_BENEFIT
    # increment number of rounds
    member[4] += 1

    return member


def shift_decisions(gene, dec, group_dec):
    gene[64:66] = gene[66:68]
    gene[66:68] = gene[68:70]
    gene[68] = group_dec
    gene[69] = dec

    return gene


def playround(population):

    green_count = 0
    decision_list = []

    for i, nation in enumerate(population):
        nat_gene = nation[0]
        history = ''.join(map(str, nat_gene[64:70]))
        index = int(history, 2)
        decision = nat_gene[index]
        green_count += (1 - decision)
        decision_list.append(decision)

    coop = 0
    if green_count >= GREEN_THRESHOLD * len(population):
        coop += 1

    for i, nation in enumerate(population):
        nat_gene = nation[0]
        nat_gene = shift_decisions(nat_gene, decision_list[i], coop)
        nation[0] = nat_gene
        nation = update_score(nation, decision_list[i], green_count, len(population))


def playMultiRounds(population, numRounds=150):
    for x in range(numRounds):
        playround(population)

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
    member[1] = 0
    member[2] = 0
    member[3] = 0
    member[4] = 0
    #member[5] = random.randint(0,3)
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
