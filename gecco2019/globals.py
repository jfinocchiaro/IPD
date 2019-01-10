#
# values needed in multiple files in the project
#

# indicices into members and individuals
class index:
    def __init__(self):
        pass

    # indices into individuals
    genome = 0          # for individual (evolving population)
    hist = 1            # history bits
    scores = 2          # scores: self, opponent, cooperation, number games played
    stats = 3           # stats: wins, draws, losses
    pair = 4            # objective pair for evolving players
    type = 5            # player type (Axelrod types, Gradual, Evolved)
    id = 6              # player id (integer identifier)
    grad = 7            # gradual fields -- used for Gradual players only

    # indices into scores
    self = 0            # self score
    opp = 1             # opponent score
    coop = 2            # mutual cooperation count
    games = 3           # number of games played
    match = 4           # self score this match

    # indices into stats
    win = 0             # number of matches won
    draw = 1            # number of matches drawn
    loss = 2            # number of matches lost

    # indices into gradual
    opp_last = 0        # opponent last play
    opp_d = 1           # number of opponent defects
    d_flag = 2          # flag set when player is defecting
    d_cnt = 3           # self consecutive defects
    c_flag = 4          # flag set when player is cooperating
    c_cnt = 5           # self coop count

    # ids for objective pairs
    selfish = 0
    communal = 1
    cooperative = 2
    selfless = 3


class keys:
    def __init__(self):
        pass

    # values used in sort_key()
    SELF = 0  # self score
    WINS = 1  # number of wins
    WDL = 2  # 3 pts for win, 1 pt for draw, 0 pts for loss
    DRAWS = 3  # number of draws
    COOP = 4  # mutual cooperation score
    MUT = 5  # mutual benefit -- minimize difference between self and opp scores
    MATCH = 6  # score of most recent match
