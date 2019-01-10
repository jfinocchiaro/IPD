import random
import csv
from copy import deepcopy

import deapplaygame2 as dpg
import scorechange
from globals import index as i

# Define standard player types (used in benchmark type)
std_types = {0: 'COOP', 1: 'DEFECT', 2: 'TFT', 3: 'STFT', 4: 'PAVLOV', 5: 'SPITE', 6: 'RANDOM',
             7: 'CD', 8: 'DDC', 9: 'CCD', 10: 'TF2T', 11: 'SOFTMAJ', 12: 'HARDMAJ', 13: 'HARDTFT',
             14: 'NAIVE', 15: 'REMORSE', 16: 'GRADUAL', 17: 'EVOLVED', 18: 'EVOLVED', 19: 'EVOLVED', 20: 'EVOLVED'}


def init_pop(pop, counts):
    sum = 0
    for k in range(len(std_types) - 4):
        for j in range(counts[k]):
            index = sum + j
            pop[index][i.type] = k
            if std_types[k] != 'EVOLVED':
                pop[index][i.pair] = -1
        sum += counts[k]


def get_decision(p, self_hist, opp_hist, n):
    p_type = std_types[p[i.type]]
    decision = -1

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
        elif p[i.grad][i.d_flag] == 1:
            decision = 1
            p[i.grad][i.d_cnt] += 1
            if p[i.grad][i.d_cnt] == p[i.grad][i.opp_d]:
                p[i.grad][i.d_cnt] = 0
                p[i.grad][i.d_flag] = 0
                p[i.grad][i.c_flag] = 1
        # if post-defect coop flag set
        elif p[i.grad][i.c_flag] == 1:
            decision = 0
            p[i.grad][i.c_cnt] += 1
            if p[i.grad][i.c_cnt] == 2:
                p[i.grad][i.c_flag] = 0
                p[i.grad][i.c_cnt] = 0
        else:
            if opp_hist[n-1] == 0:
                decision = 0
            else:
                decision = 1
                p[i.grad][i.opp_d] += 1
                p[i.grad][i.d_flag] = 1
                p[i.grad][i.d_cnt] = 1

    elif p_type == 'EVOLVED':
        # ind = p[i.genome]
        decisionind = (''.join(map(str, p[i.hist])))
        decisionind = int(decisionind, 2)
        decision = p[i.genome][decisionind]

    return decision


# reset the fields added to genome for implementing "GRADUAL"
def reset_gradual(p):
    p[i.grad][i.opp_last] = 0
    p[i.grad][i.opp_d] = 0
    p[i.grad][i.d_flag] = 0
    p[i.grad][i.d_cnt] = 0
    p[i.grad][i.c_flag] = 0
    p[i.grad][i.c_cnt] = 0


# reset score fields for player
def reset_scores(p):
    p[i.scores][i.self] = 0
    p[i.scores][i.opp] = 0
    p[i.scores][i.coop] = 0
    p[i.scores][i.games] = 0
    p[i.scores][i.match] = 0


def reset_wdl(p):
    p[i.stats][i.win] = 0
    p[i.stats][i.draw] = 0
    p[i.stats][i.loss] = 0


def playMultiRounds(player1, player2, rounds=150):
    decisionHist1 = []
    decisionHist2 = []

    player1[i.scores][i.match] = 0
    player2[i.scores][i.match] = 0

    if std_types[player1[i.type]] == 'GRADUAL':
        reset_gradual(player1)
    elif std_types[player1[i.type]] == 'EVOLVED':
        dpg.setHistBits(player1)

    if std_types[player2[i.type]] == 'GRADUAL':
        reset_gradual(player2)
    elif std_types[player2[i.type]] == 'EVOLVED':
        dpg.setHistBits(player2)

    for n in range(rounds):
        decision1 = get_decision(player1, decisionHist1, decisionHist2, n)
        decision2 = get_decision(player2, decisionHist2, decisionHist1, n)

        decisionHist1.append(decision1)
        decisionHist2.append(decision2)

        if std_types[player1[i.type]] == 'EVOLVED':
            dpg.shift_decisions(player1[i.hist], decision2, decision1)

        if std_types[player2[i.type]] == 'EVOLVED':
            dpg.shift_decisions(player2[i.hist], decision1, decision2)

        # mutual cooperation
        if decision1 == 0 and decision2 == 0:
            scorechange.mutualcooperation2(player1)
            scorechange.mutualcooperation2(player2)

        # player 1 is screwed
        elif decision1 == 0 and decision2 == 1:
            scorechange.screwed2(player1)
            scorechange.tempt2(player2)

        # player 2 is screwed
        elif decision1 == 1 and decision2 == 0:
            scorechange.tempt2(player1)
            scorechange.screwed2(player2)

        # both players defect
        else:
            scorechange.mutualdefect2(player1)
            scorechange.mutualdefect2(player2)

    dpg.calc_wdl(player1, player2)

    del decisionHist1
    del decisionHist2
