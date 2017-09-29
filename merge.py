#!/usr/bin/env python

import os
import sys
import argparse
import array

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('FILE', nargs=1)
	args = parser.parse_args()

	if not os.path.exists(args.FILE[0]):
		print("enter file for argument; not '%s'" % args.DIR[0])
		quit(1)

	header = '''\
<?xml version="1.0" encoding="UTF-8"?>
<manifest>

  <remote  name="github"
           fetch=".." />

  <remote  name="aosp"
           fetch="https://android.googlesource.com" />

  <default revision="refs/heads/*"
           remote="github"
           sync-c="true"
           sync-j="4" />

'''
	print(header)

	with open(args.FILE[0], "r") as file:
		for line in file:
			# fekin empty lines
			if (line.strip() == ''):
				continue

			sp=[w.strip() for w in line.split('\t')]
			remote = sp[0].strip()
			name = sp[1].strip()
			print('<project name="%s" remote="%s" />' % (name, remote))

	footer = '''\

</manifest>\
'''
	print(footer)

if __name__ == '__main__':
	main()
