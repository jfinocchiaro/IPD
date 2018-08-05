#!/bin/bash

for j in {1..30}; do
	echo "Started" &
	python without_selfless_scripts/no_selfless_no_trump_train_axelrod.py &
done
