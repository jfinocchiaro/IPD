#
# shell to make multiple calls to run_rr round-robin competition
# and record the results
#

import time
import csv
import os
import pwd
import platform

import deapplaygame2 as dpg
from globals import index as i
from rr_competition import run_rr

# change this to determine the evaluation metric for testing
# SELF = 0    # self score
# WINS = 1    # number of wins
# WDL = 2     # 3 pts for win, 1 pt for draw, 0 pts for loss
# DRAWS = 3   # number of draws
# COOP = 4    # mutual cooperation score
# MUT = 5     # mutual benefit -- minimize difference between self and opp scores
# MATCH = 6   # score of most recent match
# TESTING_METRIC = keys.SELF


def multi_rr():

    NUM_TYPES = 21

    num_each_std = 20
    num_each_evolved = 20
    training_group = 'POP'

    NUM_COMPETITIONS = 100

    logpath = ''
    if 'comet' in platform.node():
        logpath += '/oasis/scratch/comet/'
        logpath += pwd.getpwuid(os.getuid())[0]
        logpath += '/temp_project/'

    if training_group == 'POP':
        logpath += 'train_pop/'
    else:
        logpath += 'train_axelrod/'
    logpath += 'rr-'
    logpath += time.strftime("%Y%m%d")
    logpath += '-{}'.format(NUM_COMPETITIONS)

    fname_top10 = logpath + '-top10.csv'
    fname_type = logpath + '-type.csv'

    f_top10 = open(fname_top10, 'wb')
    writer_10 = csv.writer(f_top10, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    f_type = open(fname_type, 'wb')
    writer_type = csv.writer(f_type, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for comps in range(NUM_COMPETITIONS):
        print("\n\n Run number: {}\n".format(comps))

        result_pop = run_rr(training_group, num_each_std, num_each_evolved)

        for j in range(10):
            write_member(writer_10, result_pop[j])
        writer_10.writerow("")

        sorted_by_type = sorted(result_pop, key=lambda m: (m[i.type], -m[i.scores][i.self]))

        for j in range(NUM_TYPES):
            write_member(writer_type, sorted_by_type[0])
            m_type = sorted_by_type[0][i.type]
            k = 1
            next_type = False
            while not next_type:
                if k < len(sorted_by_type):
                    if m_type == sorted_by_type[k][i.type]:
                        k += 1
                    else:
                        next_type = True
                else:
                    next_type = True
            del sorted_by_type[:k]
        writer_type.writerow("")

        del result_pop
        del sorted_by_type


def write_member(writer, member):
    writer.writerow([''] + \
                    [member[i.pair]] + \
                    [member[i.type]] + \
                    member[i.scores] + \
                    member[i.stats] + \
                    member[i.genome] + \
                    [member[i.id]])


if __name__ == "__main__":
    multi_rr()
