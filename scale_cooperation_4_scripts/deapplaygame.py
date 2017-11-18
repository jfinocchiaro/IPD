from deap import tools
#0 = Cooperate
#1 = Defect
import scorechange
import random
import itertools



def evaluate(member):
    score1 = 0
    score2 = 0
    objectives = member[5]
    if objectives == 0:
        #maximizing personal score, min opp score
        score1 = float(member[1]) / member[4]
        score2 =  float(-member[2]) / member[4]
    if objectives == 1:
        #max personal and opponent score
        score1 = float(member[1]) / member[4]
        score2 = float(member[2]) / member[4]
    if objectives == 2:
        #max personal score and cooperation
        score1 = float(member[1]) / member[4]
        score2 = min(float(member[3]) / member[4] * 6, 4)
    if objectives == 3:
        #max opp score and cooperation
        score1 = float(member[2]) / member[4]
        score2 = min(float(member[3]) / member[4] * 6, 4)
    return score1, score2


def evaluate_three_obj(member):
    score1 = float(member[1]) / member[4]
    score2 =  float(-member[2]) / member[4]
    score3 = min(float(member[3]) / member[4] * 6, 3)

    return score1, score2, score3


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


def playround(member1, member2):

    ind1 = member1[0]
    decisionind1 = (''.join(map(str, ind1[64:70])))
    decisionind1 = int(decisionind1, 2)
    decision1 = ind1[decisionind1]

    ind2 = member2[0]
    decisionind2 = (''.join(map(str, ind2[64:70])))
    decisionind2 = int(decisionind2, 2)
    decision2 = ind2[decisionind2]

    ind1 = shift_decisions(ind1, decision2, decision1)
    ind2 = shift_decisions(ind2, decision1, decision2)

    member1[0] = ind1
    member2[0] = ind2


    #mutual cooperation
    if decision1 == 0 and decision2 == 0:
        member1 = scorechange.mutualcooperation(member1)
        member2 = scorechange.mutualcooperation(member2)

    #player 1 is screwed
    elif decision1 == 0 and decision2 == 1:
        member1 = scorechange.screwed(member1)
        member2 = scorechange.tempt(member2)

    #player 2 is screwed
    elif decision1 == 1 and decision2 == 0:
        member1 = scorechange.tempt(member1)
        member2 = scorechange.screwed(member2)

    #both players defect
    else:
        member1 = scorechange.mutualdefect(member1)
        member2 = scorechange.mutualdefect(member2)


def shift_decisions(ind1, oppdec, yourdec):
    ind1[64:66] = ind1[66:68]
    ind1[66:68] = ind1[68:70]
    ind1[68] = oppdec
    ind1[69] = yourdec
    return ind1

def playMultiRounds(ind1, ind2, numRounds=150):
    for x in range(numRounds):
        playround(ind1, ind2)


def playroundtrump(member1):

    ind1 = member1[0]
    decisionind1 = (''.join(map(str, ind1[64:70])))
    decisionind1 = int(decisionind1, 2)
    decision1 = ind1[decisionind1]

    decision2 = 1

    ind1 = shift_decisions(ind1, decision2, decision1)

    member1[0] = ind1

    #mutual cooperation
    if decision1 == 0 and decision2 == 0:
        member1 = scorechange.mutualcooperation(member1)


    #player 1 is screwed
    elif decision1 == 0 and decision2 == 1:
        member1 = scorechange.screwed(member1)


    #player 2 is screwed
    elif decision1 == 1 and decision2 == 0:
        member1 = scorechange.tempt(member1)


    #both players defect
    else:
        member1 = scorechange.mutualdefect(member1)


def playMultiRoundsTrump(ind1, numRounds=150):
    for x in range(numRounds):
        playroundtrump(ind1)

'''
def finalFitness(member, population):
    for person in population:
        playMultiRounds(member, person)
    fit1, fit2 = evaluate(member)
    return fit1, fit2
'''

def mutInternalFlipBit(individual, indpb=0.1, indpb2 = 0.0):
    decisionSlice = individual[0][64:]
    genome = (individual[0][0:64])
    genome = (list)(tools.mutFlipBit(genome, indpb))

    fullGen =  genome[0] + (decisionSlice)
    individual[0] = fullGen
    #individual[0] = individual[0].pop(0)
    test = random.random
    if test < indpb2:
        individual[5] = random.randint(0,3)
    return individual, #comma here


def mutInternalFlipBitWHistory(individual, indpb=0.1, indpb2=0.0):

    genome = (list)(tools.mutFlipBit(individual[0], indpb))


    individual[0] = genome
    individual[0] = individual[0].pop(0)
    test = random.random
    if test < indpb2:
        individual[5] = random.randint(0, 3)
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
