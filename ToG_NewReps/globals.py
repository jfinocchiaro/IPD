#
# values needed in multiple files in the project
#

# total number of player types including:
#   standard strategies
#   evolved types
TOTAL_TYPES = 81

# version of representation being used:
#   0: 64 bits for decisions, 6 bits for history
#   1: lookup table: 8 decision bits; 3 history bits (opponent only)
#   2: markov process: 8 decision floats (probabilities); 3 history bits (opponent only)
#   3: markov process: 64 decision floats (probabilities); 6 history bits (opp and self)
#   4: FSM (Mealy machine)
REP = 0

# indicates if multiple objectives are being used
#   False: single-objective individuals
#   True: multi-objective individuals
MULTI = False

# list of representations using 3 history bits
HIST3 = [1, 2, 4]

# list of representations using 6 history bits
HIST6 = [0, 3]

# list of markov representations
MARKOV = [2, 3]

# list of binary representations
BINARY = [0, 1]

# Mealy machine representation
FSM = 4

NOISE = 0.05

if REP in HIST6:
    TABLE_SIZE = 64
    HIST_SIZE = 6
else:
    TABLE_SIZE = 8
    HIST_SIZE = 3

FSM_STATES = 16
    
# Define standard player types
# 17-20: Lookup64 multi-obj trained population
# 21-24: Lookup8 multi-obj trained population
# 25-28: Markov8 multi-obj trained population
# 29-32: FSM multi-obj trained population
# 33-36: Lookup64 multi-obj trained axelrod
# 37-40: Lookup8 multi-obj trained axelrod
# 41-44: Markov8 multi-obj trained axelrod
# 45-48: FSM multi-obj trained axelrod
# 49-52: Lookup64 single-obj trained population
# 53-56: Lookup8 single-obj trained population
# 57-60: Markov8 single-obj trained population
# 61-64: FSM single-obj trained population
# 65-68: Lookup64 single-obj trained axelrod
# 69-72: Lookup8 single-obj trained axelrod
# 73-76: Markov8 single-obj trained axelrod
# 77-80: FSM single-obj trained axelrod
strategy_dict = {0: 'Always C', 1: 'Always D', 2: 'TFT', 3: 'STFT', 4: 'Pavlov', 5: 'Spiteful', 6: 'Random',
             7: 'CD', 8: 'DDC', 9: 'CCD', 10: 'TF2T', 11: 'Soft Maj', 12: 'Hard Maj', 13: 'HTFT',
             14: 'Naive', 15: 'Remorseful', 16: 'Gradual', 
             17: 'L64 P M Selfish', 18: 'L64 P M Communal', 19: 'L64 P M Cooperative', 20: 'L64 P M Selfless', 
             21: 'L8 P M Selfish', 22: 'L8 P M Communal', 23: 'L8 P M Cooperative', 24: 'L8 P M Selfless', 
             25: 'M8 P M Selfish', 26: 'M8 P M Communal', 27: 'M8 P M Cooperative', 28: 'M8 P M Selfless', 
             29: 'FSM P M Selfish', 30: 'FSM P M Communal', 31: 'FSM P M Cooperative', 32: 'FSM P M Selfless', 
             33: 'L64 A M Selfish', 34: 'L64 A M Communal', 35: 'L64 A M Cooperative', 36: 'L64 A M Selfless', 
             37: 'L8 A M Selfish', 38: 'L8 A M Communal', 39: 'L8 A M Cooperative', 40: 'L8 A M Selfless', 
             41: 'M8 A M Selfish', 42: 'M8 A M Communal', 43: 'M8 A M Cooperative', 44: 'M8 A M elfless', 
             45: 'FSM A M Selfish', 46: 'FSM A M Communal', 47: 'FSM A M Cooperative', 48: 'FSM A M Selfless',
             49: 'L64 P S Self', 50: 'L64 P S Min Diff', 51: 'L64 P S Coop', 52: 'L64 P S Opp', 
             53: 'L8 P S Self', 54: 'L8 P S Min Diff', 55: 'L8 P S Coop', 56: 'L8 P S Opp', 
             57: 'M8 P S Self', 58: 'M8 P S Min Diff', 59: 'M8 P S Coop', 60: 'M8 P S Opp', 
             61: 'FSM P S Self', 62: 'FSM P S Min Diff', 63: 'FSM P S Coop', 64: 'FSM P S Opp', 
             65: 'L64 A S Self', 66: 'L64 A S Min Diff', 67: 'L64 A S Coop', 68: 'L64 A S Opp', 
             69: 'L8 A S Self', 70: 'L8 A S Min Diff', 71: 'L8 A S Coop', 72: 'L8 A S Opp', 
             73: 'M8 A S Self', 74: 'M8 A S Min Diff', 75: 'M8 A S Coop', 76: 'M8 A S Opp', 
             77: 'FSM A S Self', 78: 'FSM A S Min Diff', 79: 'FSM A S Coop', 80: 'FSM A S Opp'}


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
    state = 8           # current state -- used for FSM players only
    rep = 9             # representation used for individuals

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
    selfish = 0         # if MULTI: max self & min opp;   else: max self 
    communal = 1        # if MULTI: max self & max opp;   else: max opp
    cooperative = 2     # if MULTI: max self & max coop;  else: max coop
    selfless = 3        # if MULTI: max opp & max coop;   else: min difference self and opp


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
