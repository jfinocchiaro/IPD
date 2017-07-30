#!/bin/bash

for j in {1..30}; do
	echo "Started" &
	python coevolution/coevolution_without_selfless.py &
done
