# encoding: UTF-8
#--
# Copyright (c) 2014 Michael Berkovich, TranslationExchange.com
#
#  _______                  _       _   _             ______          _
# |__   __|                | |     | | (_)           |  ____|        | |
#    | |_ __ __ _ _ __  ___| | __ _| |_ _  ___  _ __ | |__  __  _____| |__   __ _ _ __   __ _  ___
#    | | '__/ _` | '_ \/ __| |/ _` | __| |/ _ \| '_ \|  __| \ \/ / __| '_ \ / _` | '_ \ / _` |/ _ \
#    | | | | (_| | | | \__ \ | (_| | |_| | (_) | | | | |____ >  < (__| | | | (_| | | | | (_| |  __/
#    |_|_|  \__,_|_| |_|___/_|\__,_|\__|_|\___/|_| |_|______/_/\_\___|_| |_|\__,_|_| |_|\__, |\___|
#                                                                                        __/ |
#                                                                                       |___/
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#++


__author__ = 'randell'

import logging
import sys
import unittest
from unittest import TestCase

class BaseTest(TestCase):


	@classmethod
	def setUpClass(cls):
		logging.basicConfig(stream=sys.stdout)
		logging.getLogger().setLevel(logging.DEBUG)
		logging.getLogger().handlers[0].setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(filename)s %(module)s.%(funcName)s:%(lineno)d %(message)s", "%a, %d %b %Y %H:%M:%S"))

		logging.debug("enter")

	@classmethod
	def setUp(self):
		logging.debug("enter")
		# Left blank for base class

	@classmethod
	def tearDownClass(cls):
		logging.debug("enter")


	@classmethod
	def tearDown(self):
		logging.debug("enter")
		# Left blank for base class

if __name__ == '__main__':
	unittest.main()