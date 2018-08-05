#general purpose helper script that has all of the functionality of the IPD game


#0 = Cooperate
#1 = Defect


import matplotlib.pyplot as plt     #graphing funcitons
from deap import tools              #GA helper functions
import scorechange                  #the script that has functionality that changes player scores
import numpy as np                  #numpy
import random                       #for random number generation
import itertools                    #in order to generate permutations and iterate over lists
import networkx as nx               #networks library


#returns the player's two scores that we are optimizing based on their objectiecs
def evaluate(member):
    score1 = 0 #initialize to 0
    score2 = 0 #initialize to 0
    objectives = member[5] #find the player's objectives
    personal = float(member[1]) / member[4] #their personal average score
    opp = float(member[2]) / member[4]      #their opponent's average score


    #maximizing personal score, min opp score
    if objectives == 0:
        score1 = personal #maximizing their score
        score2 = 3 - opp #so this was messing us up earlier, since everything needs to be in terms of a maximization and on the same range.  Since 3 is determined to be the baseline, we want 3-score to be maximized by the opponent having a score of 0 (i.e. minimizing their score)

    #max personal and opponent score
    if objectives == 1:
        score1 = personal       #maximizing their score
        score2 = opp            #maximizing their opponent's score as well

    #max personal score and cooperation
    if objectives == 2:
        score1 = personal                                   #maximizing their score
        score2 = min(float(member[3]) / member[4] * 6, 3)   #baseline is argued to be 1/2, so scaling by 6 so that 3 is acquired if baseline is hit, but maxed at 3 to be fair.



    #max personal score and cooperation
    if objectives == 3:
        score1 = opp #opponent's score
        score2 = min(float(member[3]) / member[4] * 6, 3) #baseline is argued to be 1/2, so scaling by 6 so that 3 is acquired if baseline is hit, but maxed at 3 to be fair.

    return score1, score2


#when we optimize over 3 objectives, max personal, min opponent, and max cooperation
#looking at it now, doesn't make sense to me why we're minimizing opponent score
def evaluate_three_obj(member):
    score1 = float(member[1]) / member[4]
    score2 = 3- (float(member[2]) / member[4])
    score3 = min(float(member[3]) / member[4] * 6, 3)

    return score1, score2, score3


#initialize members so that there's a uniform distributions over the objectives.
def uniformobjectives(population):
    x = 0
    for member in population:
        member[5] = int(x%4)
        x += 1
    return population

#initialize every member to be selfish
def uniformobjectivesSelfish(population):
    for member in population:
            member[5] = 0

    return population


#play a round between the two members
def playround(member1, member2):

    ind1 = member1[0]                                   #genome of first player
    decisionind1 = (''.join(map(str, ind1[64:70])))     #decision index
    decisionind1 = int(decisionind1, 2)                 #decision index cast from binary
    decision1 = ind1[decisionind1]                      #access the decision bit

    ind2 = member2[0]                                   #genome of second player
    decisionind2 = (''.join(map(str, ind2[64:70])))     #decision index
    decisionind2 = int(decisionind2, 2)                 #decision index cast from binary
    decision2 = ind2[decisionind2]                      #access the decision bit

    ind1 = shift_decisions(ind1, decision2, decision1)  #change player 1's histry
    ind2 = shift_decisions(ind2, decision1, decision2)  #change palyer 2's history

    member1[0] = ind1                                   #change genome of player 2
    member2[0] = ind2                                   #change genome of player 2


    #change scores accordingly
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


#changes the history bits in the genome
def shift_decisions(ind1, oppdec, yourdec):
    ind1[64:66] = ind1[66:68]
    ind1[66:68] = ind1[68:70]
    ind1[68] = oppdec
    ind1[69] = yourdec
    return ind1

#calls playRound multiple times
def playMultiRounds(ind1, ind2, numRounds=50):
    for x in range(numRounds):
        playround(ind1, ind2)

#plays a round against a player that always defects
def playroundtrump(member1):

    ind1 = member1[0]                                   #genome of first player
    decisionind1 = (''.join(map(str, ind1[64:70])))     #decision index
    decisionind1 = int(decisionind1, 2)                 #decision index cast from binary
    decision1 = ind1[decisionind1]                      #access the decision bit

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


#play multiple rounds against a player that always defects
def playMultiRoundsTrump(ind1, numRounds=150):
    for x in range(numRounds):
        playroundtrump(ind1)


#mutation function that doesn't include the history of a player
def mutInternalFlipBit(individual, indpb=0.1, indpb2 = 0.0):
    decisionSlice = individual[0][64:]
    genome = (individual[0][0:64])
    genome = (list)(tools.mutFlipBit(genome, indpb))

    fullGen =  genome[0] + (decisionSlice)
    individual[0] = fullGen
    #individual[0] = individual[0].pop(0)
    test = random.random
    if test < indpb2:
        individual[5] = random.randint(0,2)
    return individual, #comma here


#mutation function that includes the history of a player
def mutInternalFlipBitWHistory(individual, indpb=0.1, indpb2=0.0):

    genome = (list)(tools.mutFlipBit(individual[0], indpb))


    individual[0] = genome
    individual[0] = individual[0].pop(0)
    test = random.random
    if test < indpb2:
        individual[5] = random.randint(0, 3)
    return individual,  # comma here

#one point crossover
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


#without changing their objectives, reset's a players scores.
def resetPlayer(member):
    member[1] = 0
    member[2] = 0
    member[3] = 0
    member[4] = 0
    #member[5] = random.randint(0,3)
    return member


#write each member of population in CSV called filename
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


#draw the graph in matplotlib
def drawGraph(population, G, rows=8, COLS=8):
    #lists of which nodes are each color based on objectives
    redlist = []
    greenlist = []
    bluelist = []
    blacklist = []

    for node in G.nodes():
        ind = node[0] * rows + node[1]
        if population[ind][5] == 0:
            redlist.append(node)
        elif population[ind][5] == 1:
            bluelist.append(node)
        elif population[ind][5] == 2:
            greenlist.append(node)
        else:
            blacklist.append(node)


    #draw each part of the graph
    nx.draw_spectral(G, nodelist=redlist, node_color='r')
    nx.draw_spectral(G, nodelist=bluelist, node_color='blue')
    nx.draw_spectral(G, nodelist=greenlist, node_color='green')
    nx.draw_spectral(G, nodelist=blacklist, node_color='black')
    #nx.draw_networkx_edges(G,pos,width=1.0,alpha=0.5)

    import matplotlib.patches as mpatches
    #labels for legend
    red_patch = mpatches.Patch(color='red', label='Selfish')
    blue_patch = mpatches.Patch(color='blue', label='MWB')
    green_patch = mpatches.Patch(color='green', label='Cooperative')
    black_patch = mpatches.Patch(color='black', label='Selfless')
    plt.legend(handles=[red_patch, blue_patch,green_patch,black_patch])


    plt.show()
