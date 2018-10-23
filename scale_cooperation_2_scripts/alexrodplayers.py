import random
import deapplaygame
import scorechange


def initAxpop():
    #return ['coop']
    return ['coop', 'defect', 'tft', 'stft', 'pavlov', 'spiteful', 'random', 'CD', 'DDC', 'CCD', 'tf2t', 'softmaj', 'hardmaj', 'hardtft', 'naiveprober', 'remorseful']

def playAxelrodPop(member1, oppName, numRounds=150):
    decisionHist1 = []
    decisionHist2 = []
    for n in range(numRounds):

        #always cooperate
        if oppName == 'coop':
            decision2 = 0

        #always defect
        elif oppName == 'defect':
            decision2 = 1

        #tft
        elif oppName == 'tft':
            if n == 0:
                decision2 = 0
            else:
                decision2 = decisionHist1[n-1]

        #suspicious tft
        elif oppName == 'stft':
            if n == 0:
                decision2 = 1
            else:
                decision2 = decisionHist1[n-1]


        #pavlov- defect only if players didn't agree on previous move
        elif oppName == 'pavlov':
            if n == 0:
                decision2 = 0
            elif decisionHist1[n-1] == decisionHist2[n-1]:
                decision2 = 0
            else:
                decision2 = 1

        #spiteful- cooperates until opponent defects
        elif oppName == 'spiteful':
            if 1 in decisionHist1:
                decision2 = 1
            else:
                decision2 = 0

        #random
        elif oppName == 'random':
            decision2 = random.randint(0,1)

        #periodicCD (rotates)
        elif oppName == 'CD':
            if n % 2 == 0:
                decision2 = 0
            else:
                decision2 = 1

        #periodic DDC
        elif oppName == 'DDC':
            if n % 3 == 2:
                decision2 = 0
            else:
                decision2 = 1



        #periodic CCD
        elif oppName == 'CCD':
            if n % 3 == 2:
                decision2 = 1
            else:
                decision2 = 0

        #tf2t
        elif oppName == 'tf2t':
            if n< 2:
                decision2 = 0
            elif decisionHist1[n-1] == 1 and decisionHist1[n-2] == 1:
                decision2 = 1
            else:
                decision2 = 0

        #soft majority
        elif oppName == 'softmaj':
            if n == 0:
                decision2 = 0
            elif sum(decisionHist1) <= len(decisionHist1) - sum(decisionHist1):
                decision2 = 0
            else:
                decision2 = 1

        #hard majority
        elif oppName == 'hardmaj':
            if n == 0:
                decision2 = 1
            elif sum(decisionHist1) < len(decisionHist1) - sum(decisionHist1):
                decision2 = 0
            else:
                decision2 = 1

        #hard tit-for-tat
        elif oppName == 'hardtft':
            if n == 0:
                decision2 = 0
            elif n < 3:
                if 1 in decisionHist1:
                    decision2 = 1
            elif decisionHist1[n-1] == 1 or decisionHist1[n-2] == 1 or decisionHist1[n-3] == 1:
                decision2 = 1
            else: decision2 = 0



        #naive prober
        elif oppName == 'naiveprober':
            probe = random.random()
            if n == 0:
                decision2 = 0
            elif probe < 0.01:
                decision2 = 1
            else:
                decision2 = decisionHist1[n - 1]


        #remorseful prober
        elif oppName == 'remorseful':
            probe = random.random()
            if n == 0:
                decision2 = 0
            elif probe < 0.01:
                decision2 = 1
            elif decisionHist2[n-1] == 1 and decisionHist2[n-2] == 0:
                decision2 = 0
            else:
                decision2 = decisionHist1[n - 1]



        #else
        else:
            print "Error invalid Axelrod player"

        ind1 = member1[0]

        decisionind1 = (''.join(map(str, ind1[64:70])))
        decisionind1 = int(decisionind1, 2)
        decision1 = ind1[decisionind1]
        decisionHist1.append(decision1)
        decisionHist2.append(decision2)


        ind1 = deapplaygame.shift_decisions(ind1, decision2, decision1)


        member1[0] = ind1


        # mutual cooperation
        if decision1 == 0 and decision2 == 0:
            member1 = scorechange.mutualcooperation(member1)


        # player 1 is screwed
        elif decision1 == 0 and decision2 == 1:
            member1 = scorechange.screwed(member1)


        # player 2 is screwed
        elif decision1 == 1 and decision2 == 0:
            member1 = scorechange.tempt(member1)


        # both players defect
        else:
            member1 = scorechange.mutualdefect(member1)


