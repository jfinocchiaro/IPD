#!/bin/bash

for j in {1..10}; do
	echo "Started" &
	python coevolution.py &
done

