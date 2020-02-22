#
# calculate the average score of all players by objective/objective pair
# uses scores from all tournaments in the provided directory
#
# Works for tournaments that include players with different representations
#

import csv
from os import listdir
import numpy

from globals import strategy_dict

path = 'newreps_all/rep_all_pop_single-elim_multi_no-noise_rr1000-2/'
files = listdir(path)

# NUM_TYPES is all of the possible player types
# Possible that some not represented in this data set
NUM_TYPES = len(strategy_dict)
NUM_EACH = 10

# number of multi-objective pairs
NUM_PAIRS = 4
# number of single objectives
NUM_SINGLE = 2
# number of standard players (Axelrod)
NUM_STD = 17
# number of objectives/objective pairs -- Axelrod players are counted separately
NUM_OBJS = NUM_PAIRS + NUM_SINGLE + NUM_STD

L64_nums = [17, 18, 19, 20, 33, 34, 35, 36, 49, 50, 51, 52, 65, 66, 67, 68]
L8_nums = [21, 22, 23, 24, 37, 38, 39, 40, 53, 54, 55, 56, 69, 70, 71, 72]
M8_nums = [25, 26, 27, 28, 41, 42, 43, 44, 57, 58, 59, 60, 73, 74, 75, 76]
FSM_nums = [29, 30, 31, 32, 45, 46, 47, 48, 61, 62, 63, 64, 77, 78, 79, 80]

rep_nums = L64_nums + L8_nums + M8_nums + FSM_nums

# player type at which single objective players begin
SINGLE_OBJ_THRESH = 49

# averages per tournament, over all tournaments, by objective
avgs_all = [[] for _ in range(NUM_OBJS)]

# count of occurrences of each player type
# we really only care which types are present
types_included = [0] * NUM_TYPES
 
for f in files:
    if 'type' not in f and 'top' not in f and 'Store' not in f and '.png' not in f and 'avg' not in f:
        # print('filename: {}'.format(f))
        fn = open(path + f, 'rb')
        reader = csv.reader((line.replace('\0', '') for line in fn))

        lines = []
        for row in reader:
            lines.append(row)
        #remove header lines
        del lines[:5]
        
        # increment the occurrences for current player type
        # for line in lines:
            # types_included[int(line[-1])] += 1

        # sort the data by player type
        # and then by objective/objective-pair
        lines.sort(key=lambda m: int(m[-1]))
        lines.sort(key=lambda m: int(m[-2]))
        
        fn.close()

        # list of total scores (for one tournament) by objective
        totals = [0] * NUM_OBJS
        
        # list of number of scores (for one tournament) by objective
        counts = [0] * NUM_OBJS

        # iterate over the players in a tournament
        for line in lines:
            # index into totals and counts -- based on objectives
            index = int(line[-2])
            p_type = int(line[-1])
            
            # if single objective player, shift index by 4
            if p_type >= 49:
                index += NUM_PAIRS
            # if Axelrod player, index is 6 + player_type
            elif p_type < 17:
                index = int(line[-1]) + 6
            
            if p_type in rep_nums or p_type < 17:
                totals[index] += float(line[-6])
                counts[index] += 1
                        
        # avgs_all is a list of lists -- one per objective/objective-pair
        # it stores the average for each objective for each of the tournaments
        for j in range(len(totals)):
            avgs_all[j].append(totals[j]/counts[j])
            
        
fout = open(path + 'avgs_by_obj.csv', 'wb')
writer = csv.writer(fout)

for j in avgs_all:
    writer.writerow(j)
    
fout.close()

