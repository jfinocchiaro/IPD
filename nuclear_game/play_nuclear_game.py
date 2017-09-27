from deap import tools
import random
import itertools

MUT_MEAN = 0
MUT_SD = 6

REWARD = 100
PENALTY = 10000
COOP_REWARD = 100


def evaluate(member):

    # return member score, armageddon events
    # return member[2], member[6]

    # return member score, cooperation score
    return member[2], member[8]


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


def shift_decisions(history, dec, result):
    # remove the oldest round
    history = history[4:]
    # convert to binary - result is string prepended with 0b
    dec_bits = bin(dec)
    if len(dec_bits) < 4:
        dec_bits = dec_bits[:2] + '0' + dec_bits[2]
    result_bits = bin(result)
    if len(result_bits) < 4:
        result_bits = result_bits[:2] + '0' + result_bits[2]

    # add decision and result bits for most recent round
    history.append(int(dec_bits[2]))
    history.append(int(dec_bits[3]))
    history.append(int(result_bits[2]))
    history.append(int(result_bits[3]))

    return history


def playround(member1, member2):

    ind1 = member1[0]
    hist1 = member1[1]
    dec_index1 = (''.join(map(str, hist1)))
    dec_index1 = int(dec_index1, 2)
    decision1 = ind1[dec_index1]

    ind2 = member2[0]
    hist2 = member2[1]
    dec_index2 = (''.join(map(str, hist2)))
    dec_index2 = int(dec_index2, 2)
    decision2 = ind2[dec_index2]

    # determine results
    if decision1 > decision2:
        result1 = 0
        result2 = 2
        low = decision2
    elif decision1 < decision2:
        result1 = 2
        result2 = 0
        low = decision1
    else:
        result1 = 1
        result2 = 1
        low = decision1

    # armageddon occurs if random int < low
    armageddon = random.randint(0, 100)
    if armageddon < low:
        result1 = result2 = 3

    # update history bits
    hist1 = shift_decisions(hist1, decision1, result1)
    hist2 = shift_decisions(hist2, decision2, result2)

    # update players' genomes and history
    member1[0] = ind1
    member1[1] = hist1
    member2[0] = ind2
    member2[1] = hist2

    # update scores
    if result1 == 0:
        member1[2] += REWARD
        member1[3] += 1
        member2[4] += REWARD
        member2[5] += 1
    elif result2 == 0:
        member2[2] += REWARD
        member2[3] += 1
        member1[4] += REWARD
        member1[5] += 1
    elif result1 == 3:
        member1[2] -= PENALTY
        member1[4] -= PENALTY
        member1[6] += 1
        member2[2] -= PENALTY
        member2[4] -= PENALTY
        member2[6] += 1

    if decision1 == 0:
        member1[8] += COOP_REWARD
    if decision2 == 0:
        member2[8] += COOP_REWARD


def playMultiRounds(ind1, ind2, rounds=150):
    for x in range(rounds):
        playround(ind1, ind2)


def mutate(genome, prob=0.1):
    for i in range(len(genome)):
        flip = random.random()
        if flip < prob:
            change = int(random.gauss(MUT_MEAN, MUT_SD))
            genome[i] += change
            if genome[i] < 0:
                genome[i] = 0
            elif genome[i] > 100:
                genome[i] = 100


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


def reset_pop_scores(pop):
    for member in pop:
        for i in range(2, 7):
            member[i] = 0
        member[8] = 0


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
