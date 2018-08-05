#member[0] = 70 bit string
#member[1] = personal score
#member[2] = opponent score
#member[3] = mutual cooperation
#member[4] = total Rounds
#member[5] = player objectives

#change score if
def mutualcooperation(member):
    member[4] += 1 #+1 every round
    member[1] += 3 #+personal score
    member[2] += 3 #+opponent score
    member[3] += 1 #1 if both players cooperate, +0 otherwise
    return member


def tempt(member):
    member[4] += 1 #+1 every round
    member[1] += 5 #+personal score
    member[2] += 0 #+opponent score
    member[3] += 0 #1 if both players cooperate, +0 otherwise
    return member

def screwed(member):
    member[4] += 1 #+1 every round
    member[1] += 0 #+personal score
    member[2] += 5 #+opponent score
    member[3] += 0 #1 if both players cooperate, +0 otherwise
    return member

def mutualdefect(member):
    member[4] += 1 #+1 every round
    member[1] += 1 #+personal score
    member[2] += 1 #+opponent score
    member[3] += 0 #1 if both players cooperate, +0 otherwise
    return member
