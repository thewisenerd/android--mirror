#!/bin/bash

set -euo pipefail

REPO=git@github.com:LineageOS/android.git

cleanup() {
	rm -rf android.git
	for branch in cm-11.0 cm-12.1 cm-13.0 cm-14.1 lineage-15.1 lineage-16.0; do
		rm -rf $branch
	done
	rm -rf aio
	rm -rf aio-sort-uniq
}

cleanup

git clone --mirror $REPO
for branch in cm-11.0 cm-12.1 cm-13.0 cm-14.1 lineage-15.1 lineage-16.0; do
	git clone android.git -b $branch $branch
	scripts/parse.py $branch/default.xml | sort >> aio
done

cat aio | sort | uniq > aio-sort-uniq

scripts/merge.py aio-sort-uniq > default.xml

cleanup
