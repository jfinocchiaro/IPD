#member[0] = 72 bit string
#member[1] = personal score
#member[2] = opponent score
#member[3] = mutual cooperation
#member[4] = total Rounds
#member[5] = player objectives

def mutualcooperation(member):
    member[4] += 1
    member[1] += 3
    member[2] += 3
    member[3] += 1
    return member


def tempt(member):
    member[4] += 1
    member[1] += 5
    member[2] += 0
    member[3] += 0
    return member

def screwed(member):
    member[4] += 1
    member[1] += 0
    member[2] += 5
    member[3] += 0
    return member

def mutualdefect(member):
    member[4] += 1
    member[1] += 1
    member[2] += 1
    member[3] += 0
    return member
