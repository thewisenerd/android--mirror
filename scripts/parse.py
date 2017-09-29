#!/usr/bin/env python

import xml.etree.ElementTree
from subprocess import call
import os
import sys
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('FILE', nargs=1)
	args = parser.parse_args()

	if not os.path.exists(args.FILE[0]):
		print("enter file for argument; not '%s'" % args.DIR[0])
		quit(1)


	files=[]
	for file in args.FILE:
		if file.endswith(".xml"):
			files.append(file)

	for file in files:
		e = xml.etree.ElementTree.parse(file).getroot()

		remotes={}
		for atype in e.findall('remote'):
			if atype.get('name') is not None and atype.get('fetch') is not None:
				remotes[atype.get('name')] = atype.get('fetch')
		defaultremote = "github"
		for atype in e.findall('default'):
			if atype.get('remote') is not None:
				defaultremote = atype.get('remote')

		for atype in e.findall('project'):
			if (atype.get('remote') == None):
				remote = "github"
			else:
				remote = atype.get('remote')
			name = atype.get('name')
			print("%s\t%s\n" % (remote, name))

		for atype in e.findall('include'):
			importFILE = os.path.dirname(os.getcwd() + os.path.sep + file) + os.path.sep + atype.get('name')
			call(["python", "scripts/parse.py", importFILE])

if __name__ == '__main__':
	main()
