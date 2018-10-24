#!/bin/bash

for j in {1..30}; do
	echo "Started" &
	python trials.py &
done
