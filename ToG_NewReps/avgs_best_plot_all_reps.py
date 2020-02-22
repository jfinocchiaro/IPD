#
# create a violin plot from result of post-evolution rr tournament for all representations
#
# plots the best score of each type over all runs
#

import csv
from os import listdir
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math

# this is the dictionary mapping player types to descriptive strings
from globals import strategy_dict

# total number of possible types -- some may not be present
NUM_TYPES = len(strategy_dict)

# path = 'rep1_pop_no-noise_5k/rep1_pop_no-noise_rr1000_results/'
path = 'newreps_all/rep_all_axelrod_single-elim_multi_no-noise_rr1000-axelrod-2/'
in_file_name = 'best_raw_by_type.csv'
path_parts = path.split('/')[1].split('_')
# fig_filename = '_'.join([path_parts[x] for x in range(3)])
fig_filename = 'rep_all_axelrod_single-elim_multi_no-noise_rr-ax'

SHOW_PLOT = True

# How to sort the IPD strategies.  Data elements are best value for each tournament.
#   AVG: average of the data elements
#   MAX: maximum of the data elements
SORT = 'MAX'

fn = open(path + in_file_name)
reader = csv.reader(fn)

# data: each entry in data is a list of the avgs for a single player type
# each avg for a player type is that type's average in a rr tournament
data = [[float(x) for x in row] for row in reader]

# data_indexed: each entry is a pair containing the player type and the averages described above
# this is used so that we know which labels to use in the plot
data_indexed = list(enumerate(data))
    
# number of data points for each strategy (= number of tournaments)
NUM_PTS = len(data[0])

if SORT == 'AVG':
    data.sort(reverse=True, key=lambda m: sum(m)/len(m))
    data_indexed.sort(reverse=True, key=lambda m: sum(m[1])/len(m))
elif SORT == 'MAX':
    data.sort(reverse=True, key=lambda m: max(m))
    data_indexed.sort(reverse=True, key=lambda m: max(m[1]))
else:
    print('ERROR: SORT invalid.')
    exit()

zeros = []
for j, row in enumerate(data):
    if row[0] == 0.0:
        zeros.append(j)
        
fn.close()
    
data_indexed = [data_indexed[k] for k in range(NUM_TYPES) if k not in zeros]
data = [row[1] for row in data_indexed]

fig_width = 8
if len(data_indexed) > 40:
    fig_width = 10
    
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(fig_width,6))
parts = ax.violinplot(data, points=NUM_PTS, showmeans=True, showextrema=False, showmedians=True, bw_method='silverman')

ax.set_xlabel('IPD Strategy')
ax.set_ylabel('Avg Scores per Tournament')

for pc in parts['bodies']:
    pc.set_facecolor('#2020ff')
    pc.set_alpha(1.0)

med = parts['cmedians']
med.set_edgecolor('#ff0000')
med.set_linewidth(1)

mn = parts['cmeans']
mn.set_edgecolor('#00ff00')
mn.set_linewidth(1)

if SORT == 'AVG':
    ax.set_title('IPD Strategies Best Scores Ranked by Mean over ' + str(NUM_PTS) + ' Tournaments')
    fig_filename += '_best_by-mean_violinplot.png'
elif SORT == 'MAX':
    ax.set_title('IPD Strategies Best Scores Ranked by Maximum over ' + str(NUM_PTS) + ' Tournaments')
    fig_filename += '_best_by-max_violinplot.png'

labels = []
for e in data_indexed:
    labels.append(strategy_dict[e[0]])

ax.set_xticks(np.arange(1, len(labels) + 1))
ax.set_xticklabels(labels, rotation=90)

plt.tight_layout()

fig.savefig(path + fig_filename)

if SHOW_PLOT:
    plt.show()
    
plt.close()
