#
# calculate the average score of all players by player type
# uses scores from all tournaments in the provided directory
#
# Works for tournaments that include multiple player representations
#

import csv
from os import listdir
import numpy

from globals import strategy_dict

path = 'newreps_all/rep_all_axelrod_single-elim_multi_no-noise_rr1000-axelrod-2/'
# path = 'newreps_all/single-rep_pop_single-obj_multi_rr1000/rep0/'
files = listdir(path)

# NUM_TYPES is all of the possible player types
# Possible that some not represented in this data set
NUM_TYPES = len(strategy_dict)
NUM_EACH = 10

# list to track rank of avg score by player type
places = []
# averages over all tournaments
avgs_all = [[] for _ in range(NUM_TYPES)]
# score of best individual of each type for each tournament
best_ind = [[] for _ in range(NUM_TYPES)]

for i in range(NUM_TYPES):
    places.append([0] * NUM_TYPES)

# count of occurrences of each player type
# we really only care which types are present
types_included = [0] * NUM_TYPES
for f in files:
    if 'type' not in f and 'top' not in f and 'Store' not in f and '.png' not in f:
        # print('filename: {}'.format(f))
        fn = open(path + f, 'rb')
        reader = csv.reader((line.replace('\0', '') for line in fn))

        lines = []
        for row in reader:
            lines.append(row)
        #remove header lines
        del lines[:5]
        # print len(lines)
        # print lines[0]
        
        # increment the occurrences for current player type
        for line in lines:
            types_included[int(line[-1])] += 1

        # sort the data by player type
        lines = sorted(lines, key=lambda m: int(m[-1]))
        
        fn.close()

        # averages for one tournament
        avgs = []

        # go through the player types, calculating average score for each
        for p_type in range(NUM_TYPES):
            total = 0
            self_index = -1             # declare here so in scope outside next for loop
            curr_type = []              # declare here so in scope outside next for loop
            
            if types_included[p_type]:
                for i in range(NUM_EACH):
                    self_index = len(lines[i]) - 6
                    total += float(lines[i][self_index])

            # avgs is the list of averages for the tournament in this data file
            avgs.append((p_type, (total * 30000)/NUM_EACH))
            
            # avgs_all is a list of lists -- one per player type
            # it stores the average for each player type for each of the tournaments
            avgs_all[p_type].append(total/NUM_EACH)
            
            # find the best of each type for each tournament, to be written to file
            if types_included[p_type]:
                curr_type = [line for line in lines[:NUM_EACH]]
                curr_type.sort(key=lambda m: float(m[self_index]), reverse=True)
                # print('{}  {}  {}  {}'.format(p_type, len(best_ind), self_index, len(curr_type[0])))
                best_ind[p_type].append(curr_type[0][self_index])

                del curr_type
                del lines[:NUM_EACH]
            else:
                best_ind[p_type].append(0.0)

        avgs = sorted(avgs, key=lambda s: s[1], reverse=True)
        # print avgs
        for i in range(NUM_TYPES):
            index = int(avgs[i][0])
            places[index][i] += 1

# print(avgs_all)
for i in range(NUM_TYPES):
    places[i].append(sum(avgs_all[i])/len(files))
    
fout = open(path + 'avgs_by_type.csv', 'wb')
writer = csv.writer(fout)

for j in places:
    writer.writerow(j)
    
fout.close()


fout = open(path + 'avgs_raw_by_type.csv', 'wb')
writer = csv.writer(fout)

for j in avgs_all:
    writer.writerow(j)
    
fout.close()


fout = open(path + 'best_raw_by_type.csv', 'wb')
writer = csv.writer(fout)

for j in best_ind:
    writer.writerow(j)
    
fout.close()

