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
from globals import REP
from rr_reps_competition import run_rr

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

    # NUM_TYPES = 33

    num_each_std = 10
    num_each_evolved = 10
    training_group = 'AX'
    # num_reps = 4

    NUM_COMPETITIONS = 50

    logpath = ''
    if 'comet' in platform.node():
        logpath += '/oasis/scratch/comet/'
        logpath += pwd.getpwuid(os.getuid())[0]
        logpath += '/temp_project/'

    if training_group == 'POP':
        logpath += 'train_pop/'
    elif training_group == 'AX':
        logpath += 'train_axelrod/'
    else:
        logpath += 'train_both/'
    
    if training_group == 'BOTH':
        logpath += 'rr-rep-all-'
    else:
        logpath += 'rr-rep{}-'.format(REP)
    logpath += time.strftime("%Y%m%d")
    logpath += '-{}'.format(os.getpid())
    logpath += '-{}'.format(NUM_COMPETITIONS)

    fname_top10 = logpath + '-top10.csv'
    fname_type = logpath + '-type.csv'

    f_top10 = open(fname_top10, 'wb')
    writer_10 = csv.writer(f_top10, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    f_type = open(fname_type, 'wb')
    writer_type = csv.writer(f_type, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for comps in range(NUM_COMPETITIONS):
        print("\n Begin run number: {}".format(comps))

        # result_pop = run_rr(training_group, num_each_std, num_each_evolved, num_reps)
        result_pop = run_rr(training_group, num_each_std, num_each_evolved)

        for j in range(10):
            write_member(writer_10, result_pop[j])
        writer_10.writerow("")

        sorted_by_type = sorted(result_pop, key=lambda m: (m[i.type], -m[i.scores][i.self]))

        # for j in range(NUM_TYPES):
        while sorted_by_type:
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

        print(" End run number: {}\n".format(comps))
        
        
def write_member(writer, member):
    writer.writerow([member[i.pair]] + \
                    [member[i.type]] + \
                    member[i.scores] + \
                    member[i.stats] + \
                    member[i.genome] + \
                    [member[i.id]])


if __name__ == "__main__":
    multi_rr()
