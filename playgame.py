import deap

def evaluate(member):
    individual = member.individual
    objectives = (''.join(map(str, individual[70:72])))
    objectives = int(objectives, 2)
    print objectives
    if objectives == 0:
        #maximizing personal score, min opp score
        score1 = member.personalscore
        score2 = 450 - member.oppscore
    if objectives == 1:
        #max personal and opponent score
        score1 = member.personalscore
        score2 = member.oppscore
    if objectives == 2:
        #max personal score and cooperation
        score1 = member.personalscore
        score2 = member.mutualcoop
    if objectives == 3:
        #max opp score and cooperation
        score1 = member.oppscore
        score2 = member.mutualcoop
    return score1, score2


def playround(member1, member2):

    ind1 = member1.individual
    decisionind1 = (''.join(map(str, ind1[64:70])))
    print "Binary 1:  " + str(decisionind1)
    decisionind1 = int(decisionind1, 2)
    decision1 = ind1[decisionind1]
    print "Decision 1:  " + str(decision1)

    ind2 = member2.individual
    decisionind2 = (''.join(map(str, ind2[64:70])))
    print "Binary 2:  " + str(decisionind2)
    decisionind2 = int(decisionind2, 2)
    decision2 = ind2[decisionind2]
    print "Decision 2:  " + str(decision2)

    ind1 = shift_decisions(ind1, decision2, decision1)

    if decision1 == 0 and decision2 == 0:
        member1.mutualcooperation()
        member2.mutualcooperation()

    elif decision1 == 0 and decision2 == 1:
        member1.screwed()
        member2.tempt()

    elif decision1 == 1 and decision2 == 0:
        member1.tempt()
        member2.screwed()

    else:
        member1.mutualdefect()
        member2.mutualdefect()

    print ind1

def shift_decisions(ind1, oppdec, yourdec):
    ind1[64:66] = ind1[66:68]
    ind1[66:68] = ind1[68:70]
    ind1[68] = oppdec
    ind1[69] = yourdec
    return ind1