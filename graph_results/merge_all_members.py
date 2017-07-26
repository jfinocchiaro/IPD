import glob
import csv


mypath = "DM_runs/LOO3Objectives/LOO3_*.csv"
best_players = []
for filename in glob.glob(mypath):
    with open(filename, 'rb') as f:
        for line in f.readlines():
            row1 = line.rstrip('\r\n').split(',')
            best_players.append([element.strip() for element in row1])


print best_players

with open('DM_runs/LOO3Objectives/LOO3objCometAll.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar = '|', quoting=csv.QUOTE_MINIMAL)
    for player in best_players:
        writer.writerow(player)
