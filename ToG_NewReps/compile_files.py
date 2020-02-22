
# Each run of main.py creates a file of best members found during the run.
# This program aggregates the contents of all of these files for a set of runs.
# For each objective pair, it sorts the entries by self score and writes the
# best 160 of each objective pair to a file to be used in competitions.
#

import deapplaygame2 as dpg
from globals import index as i, HIST6, HIST3

from copy import deepcopy
import os
import pwd
import csv

REP = 4

def main():
    # determine the index of self score for sorting
    if REP in HIST6:
        score_index = 70
    elif REP == 4:
        score_index = 65
    elif REP in HIST3:
        score_index = 11
    
    # directory containing the files to be aggregated
    directory = 'newreps_trained_pop/rep4_pop_single-obj_noise05_5k/'
    file_prefix = 'rep4_pop_single-obj_noise05_5k_'
    # directory = 'newreps_trained_axelrod/rep0_axelrod_single-obj_noise05_5k/'
    # file_prefix = 'rep0_axelrod_single-obj_noise05_5k_'
    file_list = [f for f in os.listdir(directory) if '-best' in f]
    
    # lists of individuals for different objective pairs
    type0 = []
    type1 = []
    type2 = []
    type3 = []
    
    for f_name in file_list:
        f_in = open(directory + '/' + f_name, 'r')
        print('Processing file: {}'.format(f_name))
        # each line is a single string -- splitlines consumes \n
        s_lines = f_in.read().splitlines()[6:]
        
        f_in.close()
        
        # process the list of strings to create a list of lists of numbers
        lines = []
        index = 0
        for line in s_lines:
            # split each line (which is a string), using comma as delimiter, into a list of strings
            new_line = line.split(',')
            # remove the first element because it is an empty string
            new_line.pop(0)
            # cast the individual strings to numeric types
            n_line = [float(x) if '.' in x else int(x) for x in new_line]
            lines.append(n_line)
            print('   line: {}'.format(index))
            index += 1
            
        # each file contains 20 elements for each objective pair
        type0.extend(lines[:20])
        type1.extend(lines[20:40])
        type2.extend(lines[40:60])
        type3.extend(lines[60:])
        
    # sort the elements by self score
    type0.sort(key=lambda m: m[score_index], reverse=True)
    type1.sort(key=lambda m: m[score_index], reverse=True)
    type2.sort(key=lambda m: m[score_index], reverse=True)
    type3.sort(key=lambda m: m[score_index], reverse=True)

    # put the best 160 (5 per run) of each objective pair into a list
    inds = type0[:160] + type1[:160] + type2[:160] + type3[:160]
    
    # open the output file
    f_out = open(directory + file_prefix + 'best-during_selfscore.csv', 'w')
    
    # put the emppty string back at front of each line, convert to string, and write to file
    for line in inds:
        line.insert(0, '')
        s = ','.join([str(i) for i in line])
        f_out.write(s + '\n')
        
    f_out.close()
        
        
if __name__ == "__main__":
    main()
