import deap

class member:

    def __init__(self, individial):
        self.individual = individial
        self.personalscore = 0
        self.oppscore = 0
        self.mutualcoop = 0
        self.totalRounds = 0

    def incrementRound(self):
        self.totalRounds += 1

    def mutualcooperation(self):
        self.totalRounds += 1
        self.personalscore += 3
        self.oppscore += 3
        self.mutualcoop += 1

    def tempt(self):
        self.totalRounds += 1
        self.personalscore += 5
        self.oppscore += 0
        self.mutualcoop += 0

    def screwed(self):
        self.totalRounds += 1
        self.personalscore += 0
        self.oppscore += 5
        self.mutualcoop += 0

    def mutualdefect(self):
        self.totalRounds += 1
        self.personalscore += 1
        self.oppscore += 1
        self.mutualcoop += 0
