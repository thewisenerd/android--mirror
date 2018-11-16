#!/usr/bin/env python

import errno
import sys
import argparse

from io import StringIO
from os import path

from lxml import etree

import logging
logging.basicConfig(format='%(levelname)s: %(message)s')


argparser = argparse.ArgumentParser()
argparser.add_argument('FILE')

class ManifestParser(object):
	ERROR_BASE = 16
	ERROR_XML_PARSE = ERROR_BASE + 1
	ERROR_ROOT_MISMATCH = ERROR_BASE + 2
	ERROR_DTD_VALIDATE = ERROR_BASE + 3

	# taken from https://gerrit.googlesource.com/git-repo/+/master/docs/manifest-format.md
	# ref: e0410bcc344a60c1d034e6dec969e36b113bc8ec
	# replace default.remote and project.remote with CDATA instead of IDREF
	dtd = etree.DTD(StringIO('''\
  <!ELEMENT remote EMPTY>
  <!ATTLIST remote name         ID    #REQUIRED>
  <!ATTLIST remote alias        CDATA #IMPLIED>
  <!ATTLIST remote fetch        CDATA #REQUIRED>
  <!ATTLIST remote pushurl      CDATA #IMPLIED>
  <!ATTLIST remote review       CDATA #IMPLIED>
  <!ATTLIST remote revision     CDATA #IMPLIED>

  <!ELEMENT default EMPTY>
  <!ATTLIST default remote      CDATA #IMPLIED> <!-- switch to CDATA from IDREF -->
  <!ATTLIST default revision    CDATA #IMPLIED>
  <!ATTLIST default dest-branch CDATA #IMPLIED>
  <!ATTLIST default upstream    CDATA #IMPLIED>
  <!ATTLIST default sync-j      CDATA #IMPLIED>
  <!ATTLIST default sync-c      CDATA #IMPLIED>
  <!ATTLIST default sync-s      CDATA #IMPLIED>
  <!ATTLIST default sync-tags   CDATA #IMPLIED>

  <!ELEMENT project (annotation*,
                     project*,
                     copyfile*,
                     linkfile*)>
  <!ATTLIST project name        CDATA #REQUIRED>
  <!ATTLIST project path        CDATA #IMPLIED>
  <!ATTLIST project remote      CDATA #IMPLIED> <!-- switch to CDATA from IDREF -->
  <!ATTLIST project revision    CDATA #IMPLIED>
  <!ATTLIST project dest-branch CDATA #IMPLIED>
  <!ATTLIST project groups      CDATA #IMPLIED>
  <!ATTLIST project sync-c      CDATA #IMPLIED>
  <!ATTLIST project sync-s      CDATA #IMPLIED>
  <!ATTLIST default sync-tags   CDATA #IMPLIED>
  <!ATTLIST project upstream CDATA #IMPLIED>
  <!ATTLIST project clone-depth CDATA #IMPLIED>
  <!ATTLIST project force-path CDATA #IMPLIED>

  <!ELEMENT annotation EMPTY>
  <!ATTLIST annotation name  CDATA #REQUIRED>
  <!ATTLIST annotation value CDATA #REQUIRED>
  <!ATTLIST annotation keep  CDATA "true">

  <!ELEMENT copyfile EMPTY>
  <!ATTLIST copyfile src  CDATA #REQUIRED>
  <!ATTLIST copyfile dest CDATA #REQUIRED>

  <!ELEMENT linkfile EMPTY>
  <!ATTLIST linkfile src CDATA #REQUIRED>
  <!ATTLIST linkfile dest CDATA #REQUIRED>

  <!ELEMENT include EMPTY>
  <!ATTLIST include name CDATA #REQUIRED>'''))

	def __init__(self, filename):
		self.filename = filename

	def _validated_iter(self, iterable):
		for element in iterable:
			if not ManifestParser.dtd.validate(element):
				logging.error(ManifestParser.dtd.error_log.filter_from_errors()[0])
				yield (ManifestParser.ERROR_DTD_VALIDATE, element)
			else:
				yield (None, element)

	def _parse(self, root):
		remotes={}
		for (err, remote) in self._validated_iter(root.findall('remote')):
			if err is not None:
				return err
			remotes[remote.get('name')] = remote.get('fetch')

		defaultremote = 'github'
		for (err, default) in self._validated_iter(root.findall('default')):
			if err is not None:
				return err
			if default.get('remote') is not None:
				defaultremote = default.get('remote')

		for (err, project) in self._validated_iter(root.findall('project')):
			if err is not None:
				return err

			name = project.get('name')
			remote = 'github' if project.get('remote') is None else project.get('remote')

			print("%s\t%s\n" % (remote, name), end='')

		for include in root.findall('include'):
			prefix = path.dirname(self.filename)
			includefile = path.join(prefix, include.get('name'))

			retval = ManifestParser(includefile).parse()
			if retval != 0:
				return retval

		return 0

	def parse(self):
		try:
			tree = etree.parse(self.filename)
		except:
			return ManifestParser.ERROR_XML_PARSE

		return self._parse(tree.getroot())

def main():
	args = vars(argparser.parse_args())

	if not path.exists(args['FILE']):
		logging.error('"{}" does not exist'.format(args['FILE']))
		return -errno.ENOENT

	# todo: symlinks?
	if not path.isfile(args['FILE']):
		logging.error('"{}" is not a file'.format(args['FILE']))
		return -errno.EINVAL

	return ManifestParser(args['FILE']).parse()

if __name__ == '__main__':
	sys.exit(main())
