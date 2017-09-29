#!/bin/bash

REPO=git@github.com:LineageOS/android.git

# rm -rf android.git
# git clone --mirror $REPO

rm -rf aio

for branch in cm-11.0 cm-12.1 cm-13.0 cm-14.1 lineage-15.0; do
	# rm -rf $branch
	# git clone android.git -b $branch $branch
	./parse.py $branch/default.xml | sort >> aio
done

cat aio | sort | uniq > aio-sort-uniq

# git clone --single-branch $REPO -b cm-14.1
