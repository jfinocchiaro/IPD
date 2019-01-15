#this file should be in the same level of the directory as train_axelrod and train_pop


import glob
import numpy as np
import csv

NUM_PLAYER_TYPES = 21

def rranalysistop10(filename):
    tournament_tracker = []
    objective_counter = np.zeros(5)
    number_wins = np.zeros(5)
    firstelt = 1
    #goes through summary file and for each rr tournament, collects the type of player for each of the top ten players, as well as the total number of top finishers per objective group
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row == []:
                tournament_tracker.append(objective_counter)
                objective_counter = np.zeros(5)
                firstelt = 1
            else:
                objective_counter[int(row[1])+1] += 1
                if firstelt:
                    number_wins[int(row[1])+1] += 1
                firstelt = 0

    #print analysis across all 100 tournaments
    print np.mean(tournament_tracker, axis=0)
    print number_wins


def bracketanalysissumm(filename):
    tournament_tracker = []
    score_tracker = []
    objective_counter = np.zeros(NUM_PLAYER_TYPES)
    avg_scores = np.zeros(NUM_PLAYER_TYPES)
    number_wins = np.zeros(NUM_PLAYER_TYPES)
    prev_empty = 0
    round_number = 0

    total_matchups = 0
    total_ties = 0
    #goes through summary file and for each bracket, as well as thenumber of wins per objective group
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row == [''] and not(prev_empty):
                #new round in same tournament
                prev_empty = 1
            elif row == [] and prev_empty:
                #new tournament
                tournament_tracker.append(objective_counter)
                score_tracker.append(avg_scores)
                
                objective_counter = np.zeros(NUM_PLAYER_TYPES)
                round_number = 0

            elif len(row) > 1:
                prev_empty = 0
                if row[1] != '':
                    round_number = int(row[1])
                #add stats for first player in match
                if len(row) > 4:
                    objective_counter[int(row[2])] = round_number
                    avg_scores[int(row[2])] = int(row[4])
                    objective_counter[int(row[5])] = round_number
                    avg_scores[int(row[5])] = int(row[7])
                    
                    #check if the match was a tie
                    if int(row[4]) == int(row[7]):
                        total_ties += 1
                    total_matchups += 1

                #if the player wins the tournament, advance their objective
                if row[0] == '' and row[1] == '' and len(row) == 4:
                    objective_counter[int(row[2])] = round_number + 1
                    number_wins[int(row[2])] += 1



    #print analysis across all 100 tournaments
    print 'Nuber of times each player won'
    print number_wins
    print 'Average score in the farthest round the farthest player of each type made it to'
    print np.mean(score_tracker, axis=0)
    print 'Average round number the farthest player of each type reached'
    print np.mean(tournament_tracker, axis=0) #how many rounds, on average, each player advanced in the tournament
    print str(float(100 * total_ties / total_matchups)) + ' percent of the matchups were ties'
    
def bracketanalysis(filename):
    pass


def main():
    TRAINING_GROUP = 'axelrod' # or 'pop' 
    TOURNAMENT_TYPE = 'bracket' #or 'bracket'
    SUMMARY_FILE = 1
    filename = 'train_' + TRAINING_GROUP + '/' + TOURNAMENT_TYPE+ '-01each/bracket-20190113-1-100.csv' #'-20each/rr-20190110-100-top10.csv'

    
    if TOURNAMENT_TYPE == 'rr' and SUMMARY_FILE:
        rranalysistop10(filename)
    elif TOURNAMENT_TYPE == 'rr' and not(SUMMARY_FILE):
        rranalysis(filename)
    elif TOURNAMENT_TYPE == 'bracket' and SUMMARY_FILE:
        bracketanalysissumm(filename)
    elif TOURNAMENT_TYPE == 'bracket' and not(SUMMARY_FILE):
        bracketanalysis(filename)


if __name__ == "__main__":
    main()
