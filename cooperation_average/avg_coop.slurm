#!/bin/bash
#SBATCH --job-name=avg_coop_axelrod    # Job name
#SBATCH --mail-type=END,FAIL          # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=22jjf22@gmail.com     # Where to send mail	
#SBATCH --ntasks=30                    # Run on a single CPU
#SBATCH --mem=1gb                     # Job memory request
#SBATCH --time=08:00:00               # Time limit hrs:min:sec
#SBATCH --output=serial_test_%j.log   # Standard output and error log

 
module load python
 
echo "Running plot script on a single CPU core"
 
python new_evolve_no_trump_train_pop.py
 
