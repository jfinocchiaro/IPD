
from globals import index as i

def mutualcooperation(member):
    member[i.scores][i.games] += 1
    member[i.scores][i.self] += 3
    member[i.scores][i.opp] += 3
    member[i.scores][i.coop] += 1
    return member


def tempt(member):
    member[i.scores][i.games] += 1
    member[i.scores][i.self] += 5
    member[i.scores][i.opp] += 0
    member[i.scores][i.coop] += 0
    return member

def screwed(member):
    member[i.scores][i.games] += 1
    member[i.scores][i.self] += 0
    member[i.scores][i.opp] += 5
    member[i.scores][i.coop] += 0
    return member

def mutualdefect(member):
    member[i.scores][i.games] += 1
    member[i.scores][i.self] += 1
    member[i.scores][i.opp] += 1
    member[i.scores][i.coop] += 0
    return member

# the '2' versions of the operations update the new field that
# tracks the players score for this meeting (of x rounds)
def mutualcooperation2(member):
    member[i.scores][i.games] += 1
    member[i.scores][i.self] += 3
    member[i.scores][i.opp] += 3
    member[i.scores][i.coop] += 1
    member[i.scores][i.match] += 3


def tempt2(member):
    member[i.scores][i.games] += 1
    member[i.scores][i.self] += 5
    member[i.scores][i.opp] += 0
    member[i.scores][i.coop] += 0
    member[i.scores][i.match] += 5


def screwed2(member):
    member[i.scores][i.games] += 1
    member[i.scores][i.self] += 0
    member[i.scores][i.opp] += 5
    member[i.scores][i.coop] += 0
    member[i.scores][i.match] += 0


def mutualdefect2(member):
    member[i.scores][i.games] += 1
    member[i.scores][i.self] += 1
    member[i.scores][i.opp] += 1
    member[i.scores][i.coop] += 0
    member[i.scores][i.match] += 1
