#
# shell to make multiple calls to run_rr round-robin competition
# and record the results
#

import time
import csv

import deapplaygame2 as dpg
from globals import index as i
from bracket_competition import run_bracket

# change this to determine the evaluation metric for testing
# SELF = 0    # self score
# WINS = 1    # number of wins
# WDL = 2     # 3 pts for win, 1 pt for draw, 0 pts for loss
# DRAWS = 3   # number of draws
# COOP = 4    # mutual cooperation score
# MUT = 5     # mutual benefit -- minimize difference between self and opp scores
# MATCH = 6   # score of most recent match
# TESTING_METRIC = keys.SELF


def multi_bracket():

    NUM_TYPES = 21

    num_each_std = 1
    num_each_evolved = 1
    training_group = 'AX'

    NUM_COMPETITIONS = 100

    logpath = ''
    if training_group == 'POP':
        logpath += 'train_pop/'
    else:
        logpath += 'train_axelrod/'
    logpath += 'bracket-'
    logpath += time.strftime("%Y%m%d")
    logpath += '-{}'.format(num_each_std)
    logpath += '-{}.csv'.format(NUM_COMPETITIONS)

    f_out = open(logpath, 'wb')
    writer = csv.writer(f_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for comps in range(NUM_COMPETITIONS):
        print("\n\n Run number: {}\n".format(comps))

        time.sleep(10)

        result = run_bracket(training_group, num_each_std, num_each_evolved)

        write_comp(writer, result, comps)

        del result


def write_comp(writer, bracket, comp):
    first = True
    writer.writerow([])
    for line in bracket:
        if first:
            writer.writerow([comp] + line)
            first = False
        else:
            writer.writerow([''] + line)


if __name__ == "__main__":
    multi_bracket()
