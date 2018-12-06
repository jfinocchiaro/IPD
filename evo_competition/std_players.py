import random
import csv
from copy import deepcopy
import deapplaygame
import scorechange

# Define standard player types (used in benchmark type)
std_types = {0: 'COOP', 1: 'DEFECT', 2: 'TFT', 3: 'STFT', 4: 'PAVLOV', 5: 'SPITE', 6: 'RANDOM',
             7: 'CD', 8: 'DDC', 9: 'CCD', 10: 'TF2T', 11: 'SOFTMAJ', 12: 'HARDMAJ', 13: 'HARDTFT',
             14: 'NAIVE', 15: 'REMORSE', 16: 'GRADUAL', 17: 'EVOLVED'}


def init_pop(pop, counts):
    sum = 0
    for i in range(len(counts) - 1):
        for j in range(counts[i]):
            index = sum + j
            pop[index][6] = i
        sum += counts[i]

def get_decision(p, self_hist, opp_hist, n):
    p_type = std_types[p[6]]

    # always cooperate
    if p_type == 'COOP':
        decision = 0

    # always defect
    elif p_type == 'DEFECT':
        decision = 1

    # tft
    elif p_type == 'TFT':
        if n == 0:
            decision = 0
        else:
            decision = opp_hist[n - 1]

    # suspicious tft
    elif p_type == 'STFT':
        if n == 0:
            decision = 1
        else:
            decision = opp_hist[n - 1]

    # pavlov- defect only if players didn't agree on previous move
    elif p_type == 'PAVLOV':
        if n == 0:
            decision = 0
        elif self_hist[n - 1] == opp_hist[n - 1]:
            decision = 0
        else:
            decision = 1

    # spiteful- cooperates until opponent defects
    elif p_type == 'SPITE':
        if 1 in opp_hist:
            decision = 1
        else:
            decision = 0

    # random
    elif p_type == 'RANDOM':
        decision = random.randint(0, 1)

    # periodicCD (rotates)
    elif p_type == 'CD':
        if n % 2 == 0:
            decision = 0
        else:
            decision = 1

    # periodic DDC
    elif p_type == 'DDC':
        if n % 3 == 2:
            decision = 0
        else:
            decision = 1

    # periodic CCD
    elif p_type == 'CCD':
        if n % 3 == 2:
            decision = 1
        else:
            decision = 0

    # tf2t
    elif p_type == 'TF2T':
        if n < 2:
            decision = 0
        elif opp_hist[n - 1] and opp_hist[n - 2]:
            decision = 1
        else:
            decision = 0

    # soft majority
    elif p_type == 'SOFTMAJ':
        if n == 0:
            decision = 0
        elif sum(opp_hist) <= (len(opp_hist) - sum(opp_hist)):
            decision = 0
        else:
            decision = 1

    # hard majority
    elif p_type == 'HARDMAJ':
        if n == 0:
            decision = 1
        elif sum(opp_hist) < len(opp_hist) - sum(opp_hist):
            decision = 0
        else:
            decision = 1

    # hard tit-for-tat
    elif p_type == 'HARDTFT':
        if n == 0:
            decision = 0
        elif n < 3:
            if 1 in opp_hist:
                decision = 1
            else:
                decision = 0
        elif opp_hist[n - 1] == 1 or opp_hist[n - 2] == 1 or opp_hist[n - 3] == 1:
            decision = 1
        else:
            decision = 0

    # naive prober
    elif p_type == 'NAIVE':
        probe = random.random()
        if probe < 0.01:
            decision = 1
        elif n == 0:
            decision = 0
        else:
            decision = opp_hist[n - 1]


    # remorseful prober
    elif p_type == 'REMORSE':
        probe = random.random()
        if probe < 0.01:
            decision = 1
        elif n == 0:
            decision = 0
        elif self_hist[n - 1] == 1 and opp_hist[n - 1] == 1:
            decision = 0
        else:
            decision = opp_hist[n - 1]

    # gradual is defined in Beaufils, Delahaye and Mathieu 1996
    elif p_type == 'GRADUAL':
        if n == 0:
            decision = 0
        # if defect flag set
        elif p[7][2] == 1:
            decision = 1
            p[7][3] += 1
            if p[7][3] == p[7][1]:
                p[7][3] = 0
                p[7][2] = 0
                p[7][4] = 1
        # if post-defect coop flag set
        elif p[7][4] == 1:
            decision = 0
            p[7][5] += 1
            if p[7][5] == 2:
                p[7][4] = 0
                p[7][5] = 0
        else:
            if opp_hist[n-1] == 0:
                decision = 0
            else:
                decision = 1
                p[7][1] += 1
                p[7][2] = 1
                p[7][3] = 1

    elif p_type == 'EVOLVED':
        ind = p[0]
        decisionind = (''.join(map(str, ind[64:70])))
        decisionind = int(decisionind, 2)
        decision = ind[decisionind]

    return decision


# reset the fields added to genome for implementing "GRADUAL"
def reset_gradual(p):
    p[7][0] = 0
    p[7][1] = 0
    p[7][2] = 0
    p[7][3] = 0
    p[7][4] = 0
    p[7][5] = 0


# reset score fields for player
def reset_scores(p):
    p[1] = 0
    p[2] = 0
    p[3] = 0
    p[4] = 0


def playMultiRounds(player1, player2, numRounds=150):
    decisionHist1 = []
    decisionHist2 = []
    for n in range(numRounds):
        decision1 = get_decision(player1, decisionHist1, decisionHist2, n)
        decision2 = get_decision(player2, decisionHist2, decisionHist1, n)

        decisionHist1.append(decision1)
        decisionHist2.append(decision2)

        if std_types[player1[6]] == 'EVOLVED':
            ind = player1[0]
            ind = deapplaygame.shift_decisions(ind, decision2, decision1)
            player1[0] = ind

        if std_types[player2[6]] == 'EVOLVED':
            ind = player2[0]
            ind = deapplaygame.shift_decisions(ind, decision1, decision2)
            player2[0] = ind

        # mutual cooperation
        if decision1 == 0 and decision2 == 0:
            player1 = scorechange.mutualcooperation(player1)
            player2 = scorechange.mutualcooperation(player2)

        # player 1 is screwed
        elif decision1 == 0 and decision2 == 1:
            player1 = scorechange.screwed(player1)
            player2 = scorechange.tempt(player2)

        # player 2 is screwed
        elif decision1 == 1 and decision2 == 0:
            player1 = scorechange.tempt(player1)
            player2 = scorechange.screwed(player2)

        # both players defect
        else:
            player1 = scorechange.mutualdefect(player1)
            player2 = scorechange.mutualdefect(player2)
