#!/bin/bash

for j in {1..5}; do
	echo "Started" &
	python trials.py &
done
