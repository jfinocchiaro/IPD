import csv
from deap import tools
#0 = Cooperate
#1 = Defect
import scorechange
import random
import itertools
from matplotlib import pyplot as plt

COOPERATION_MAX = 3

#assigns scores to the objective values depending on what the member's objectives are
def evaluate(member):
    score1 = 0
    score2 = 0
    objectives = member[5]
    if objectives == 0:
        #maximizing personal score, min opp score
        score1 = float(member[1]) / member[4]
        #since everyone is trying to maximize objectives, minimizing opponent score is the same as maximizing 3 - opp score, since 3 is generally treated as the baseline.
        score2 =  3 - float(member[2]) / member[4]
    if objectives == 1:
        #max personal and opponent score
        score1 = float(member[1]) / member[4]
        score2 = float(member[2]) / member[4]
    if objectives == 2:
        #max personal score and cooperation
        score1 = float(member[1]) / member[4]
        # score2 = min(float(member[3]) / member[4] * 6, COOPERATION_MAX)
        score2 = float(member[3]) / member[4]
    if objectives == 3:
        #max opp score and cooperation
        score1 = float(member[2]) / member[4]
        # score2 = min(float(member[3]) / member[4] * 6, COOPERATION_MAX)
        score2 = float(member[3]) / member[4]
    return score1, score2


#in case we wanted to max personal score, min opponent score, and maximize cooperation
def evaluate_three_obj(member):
    score1 = float(member[1]) / member[4]
    score2 = 3 - float(member[2]) / member[4]
    score3 = min(float(member[3]) / member[4] * 6, COOPERATION_MAX)

    return score1, score2, score3

# initialize each player with one of four objectives uniformly.
def uniformobjectives(population):
    for counter, member in enumerate(population):
        member[5] = int(counter%4)
    return population

#initialize every player to be selfish
def uniformobjectivesSelfish(population):
    for member in population:
            member[5] = 0
    return population

#initialize every player to be communal
def uniformobjectivesCommunal(population):
    for member in population:
            member[5] = 1
    return population

#initialize every player to be cooperative
def uniformobjectivesCoop(population):
    for member in population:
            member[5] = 2
    return population

#initialize every player to be selfless
def uniformobjectivesSelfless(population):
    for member in population:
            member[5] = 3
    return population

#play one round of IPD
def playround(member1, member2):

    #genome of decision bits and history bits combined.
    ind1 = member1[0]
    #get the index of the decision we want to make
    decisionind1 = (''.join(map(str, ind1[64:70])))
    decisionind1 = int(decisionind1, 2)
    #the decision is the value at the above index
    decision1 = ind1[decisionind1]

    #genome of decision bits and history bits combined.
    ind2 = member2[0]
    #get the index of the decision we want to make
    decisionind2 = (''.join(map(str, ind2[64:70])))
    decisionind2 = int(decisionind2, 2)
    #the decision is the value at the above index
    decision2 = ind2[decisionind2]

    #changes both players history bits
    ind1 = shift_decisions(ind1, decision2, decision1)
    ind2 = shift_decisions(ind2, decision1, decision2)

    #reassign the genome of both players in the global variable to be the new genome after learning new history update
    member1[0] = ind1
    member2[0] = ind2

    #change scores based on the outcome
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


#change the history bits
def shift_decisions(ind1, oppdec, yourdec):
    #2nd most recent decision becomes 3rd
    ind1[64:66] = ind1[66:68]
    #most recent decision becomes 2nd most recent
    ind1[66:68] = ind1[68:70]
    #assign decisions to most recent spot
    ind1[68] = oppdec
    ind1[69] = yourdec

    return ind1

#has the same two players against each other for multiple rounds
def playMultiRounds(ind1, ind2, numRounds=150):
    for x in range(numRounds):
        playround(ind1, ind2)

#have player play against a member that always defects
def playroundtrump(member1):
    #get player genome
    ind1 = member1[0]
    decisionind1 = (''.join(map(str, ind1[64:70])))
    decisionind1 = int(decisionind1, 2)
    #index in to see ultimate decision
    decision1 = ind1[decisionind1]


    #opponent decision is always 1
    ind1 = shift_decisions(ind1, 1, decision1)

    member1[0] = ind1


    #player 1 is screwed
    if decision1 == 0:
        member1 = scorechange.screwed(member1)

    #both players defect
    else:
        member1 = scorechange.mutualdefect(member1)

#a player faces a defector for numRounds times
def playMultiRoundsTrump(ind1, numRounds=150):
    for x in range(numRounds):
        playroundtrump(ind1)

#with probability indpb, flits a bit b to 1 + b % 2 but doesn't change the history bit
def mutInternalFlipBit(individual, indpb=float(1.0/ 64), indpb2 = float(1.0/60)):
    #the part of the genome that contains the history
    historySlice = individual[0][64:]
    #the dicision bits
    genome = (individual[0][0:64])
    #use built in DEAP flip bit with probability indpb
    genome = (list)(tools.mutFlipBit(genome, indpb))

    #full genome joining decisions and history
    fullGen =  genome[0] + (historySlice)
    individual[0] = fullGen

    #random generator to see if we change the objective
    changeObj = random.random()
    if changeObj < indpb2:
        individual[5] = random.randint(0,3)

    return individual, #comma here

#with probability indpb, flits a bit b to 1 + b % 2-- can also change the history bit
def mutInternalFlipBitWHistory(individual, indpb=float(1.0/70), indpb2=float(1.0/60)):

    genome = (list)(tools.mutFlipBit(individual[0], indpb))

    individual[0] = genome
    individual[0] = individual[0].pop(0)
    #with probability indpb2, changes the palyer's objective
    changeObj = random.random()
    if changeObj < indpb2:
        curr_pair = individual[5]
        new_pair = random.randint(0, 3)
        while new_pair == curr_pair:
            new_pair = random.randint(0, 3)
        individual[5] = new_pair
    return individual,  # comma here

#with probability indpb, flits a bit b to 1 + b % 2-- can also change the history bit
def mutInternalFlipBitWHistoryNoObjChange(individual, indpb=float(1.0/70)):

    genome = (list)(tools.mutFlipBit(individual[0], indpb))

    individual[0] = genome
    individual[0] = individual[0].pop(0)

    return individual,  # comma here

def cxOnePointGenome(ind1, ind2):
    #the length of the genomes
    size = min(len(ind1), len(ind2))
    #choose where to cross the individuals over
    cxpoint = random.randint(1, size - 1)
    #switches the two players at cxpoint
    ind1[cxpoint:], ind2[cxpoint:] = ind2[cxpoint:], ind1[cxpoint:]

    return ind1, ind2


#resets all score values for a player
def resetPlayer(member):
    member[1] = 0
    member[2] = 0
    member[3] = 0
    member[4] = 0
    return member


#used to see how population size and best player scores converge with number of generations
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
    #plt.show()


# write data to a CSV
# added test_pop as a parameter so that we can write data from the
# testing phase to the same csv, if there was a testing phase.
def exportGenometoCSV(filename, population, run_vars, test_pops=None, test_labels=None):
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)

        writer.writerow(["population: " + str(run_vars[0])])
        writer.writerow(["generations: " + str(run_vars[1])])
        writer.writerow(["training: " + run_vars[2]])
        writer.writerow("")
        for member in population:
            writer.writerow([''] +                                       \
            member[0]+                                                  \
            [float(member[1])/member[4]] +                              \
            [float(member[2])/member[4]] +                              \
            # [ min(6* float(member[3])/member[4], COOPERATION_MAX)] +    \
            [float(member[3]) / member[4]] +                            \
            [member[4]] +                                               \
            [member[5]] +                                               \
            [member[6]])

        if test_pops is not None:
            i = 0
            for tp in test_pops:
                if tp is not None:
                    writer.writerow("")
                    writer.writerow("")
                    writer.writerow(["Testing:"])
                    writer.writerow([test_labels[i]])
                    for member in tp:
                        writer.writerow([''] +                                            \
                        member[0]+                                                  \
                        [float(member[1])/member[4]] +                              \
                        [float(member[2])/member[4]] +                              \
                        # [ min(6* float(member[3])/member[4], COOPERATION_MAX)] +    \
                        [float(member[3]) / member[4]] +                            \
                        [member[4]] +                                               \
                        [member[5]] +                                               \
                        [member[6]])
                i += 1
