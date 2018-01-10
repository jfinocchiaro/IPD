#!/bin/bash

for j in {1..30}; do
	echo "Started" &
	python new_evolve_trump_axelrod.py &
done
