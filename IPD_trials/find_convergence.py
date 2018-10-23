import glob
import numpy as np

POP_SIZE = 60
NUM_FILES = 0

objective_count = np.zeros(4) #counts the number of trials where everyone cooperates on a given strategy

for filename in glob.glob('train_pop_no_trump/*.csv'): #go through every file name
    NUM_FILES += 1
    agreement_matrix = np.zeros(4)
    file = open(filename, 'r')
    for line in file:

        index = int(line.split(',')[-1].rstrip('\r\n'))

        agreement_matrix[index] += 1
    print agreement_matrix
    for x in range(len(objective_count)):
        if agreement_matrix[x] >= POP_SIZE- 5:
            objective_count[x] += 1 #everyone converged to same objective




print_threshold = 20
#print out which bits had total cooperation and defection across trials
for x in range(len(objective_count)):
    print "Population converged to all Objective " + str(x) + ": " + str(objective_count[x]) + " times. " 

