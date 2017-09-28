#!/usr/bin/env python3

"""Tests to check that Provgen is working

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

   :Copyright:
       2014-2017 Javier Quinteros, GEOFON, GFZ Potsdam <geofon@gfz-potsdam.de>
   :License:
       GPLv3
   :Platform:
       Linux

.. moduleauthor:: Javier Quinteros <javier@gfz-potsdam.de>, GEOFON, GFZ Potsdam
"""

import sys
import os
import datetime
import unittest
import urllib2
from urlparse import urlparse
import json
from difflib import Differ
from xml.dom.minidom import parseString

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))
from unittestTools import WITestRunner


class ProvgenTests(unittest.TestCase):
    """Test the functionality of provgen.py."""

    @classmethod
    def setUp(cls):
        """Setting up test."""
        cls.host = host

    def test_long_URI(self):
        """Very large URI."""
        msg = 'A URI of more than 2000 characters is not allowed and ' + \
            'should return a 414 error code'
        req = urllib2.Request('%s?net=GE%s' % (self.host, '&net=GE' * 500))
        try:
            u = urllib2.urlopen(req)
            u.read()
        except urllib2.URLError as e:
            self.assertEqual(e.code, 414, msg)
            return

        self.assertTrue(False, msg)
        return

    def test_wrong_parameter(self):
        """Unknown parameter."""
        msg = 'An error code 400 Bad Request is expected for an unknown ' + \
            'parameter'
        req = urllib2.Request('%s?net=GE&wrongparam=1' % self.host)
        try:
            u = urllib2.urlopen(req)
            u.read()
        except urllib2.URLError as e:
            self.assertEqual(e.code, 400, msg)
            return

        self.assertTrue(False, msg)
        return

    def test_wrong_format(self):
        """Wrong format option."""
        req = urllib2.Request('%s?net=GE&format=WRONGFORMAT' %
                              self.host)
        msg = 'When a wrong format is specified an error code 400 is expected!'
        try:
            u = urllib2.urlopen(req)
            u.read()
        except urllib2.URLError as e:
            if hasattr(e, 'code'):
                self.assertEqual(e.code, 400, '%s (%s)' % (msg, e.code))
                return

            self.assertTrue(False, '%s (%s)' % (msg, e))
            return

        self.assertTrue(False, msg)
        return

    def test_version(self):
        """'version' method."""
        if self.host.endswith('query'):
            vermethod = '%sversion' % self.host[:-len('query')]
        else:
            pass

        req = urllib2.Request(vermethod)
        try:
            u = urllib2.urlopen(req)
            buffer = u.read()
        except:
            raise Exception('Error retrieving version number')

        # Check that it has three components (ints) separated by '.'
        components = buffer.split('.')
        msg = 'Version number does not include the three components'
        self.assertEqual(len(components), 3, msg)

        try:
            components = map(int, components)
        except ValueError:
            msg = 'Components of the version number seem not to be integers.'
            self.assertEqual(1, 0, msg)
        # Check for exact version
        self.assertEqual(components, [1, 1, 0], 'Version is not 1.1.0 !')

# ----------------------------------------------------------------------
def usage():
    """Print how to use the service test."""
    print 'testService [-h|--help] [-p|--plain] http://server/path'


global host

if __name__ == '__main__':

    # 0=Plain mode (good for printing); 1=Colourful mode
    mode = 1

    # The default host is localhost
    for ind, arg in enumerate(sys.argv):
        if ind == 0:
            continue
        if arg in ('-p', '--plain'):
            del sys.argv[ind]
            mode = 0
        elif arg in ('-h', '--help'):
            usage()
            sys.exit(0)
        else:
            host = arg
            del sys.argv[ind]

    unittest.main(testRunner=WITestRunner(mode=mode))
