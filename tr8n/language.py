# encoding: UTF-8
#--
# Copyright (c) 2015 Translation Exchange, Inc
#
#  _______				    _		_   _		      ______		   _
# |__   __|				  | |     | | (_)		    |  ____|		 | |
#    | |_ __ __ _ _ __  ___| | __ _| |_ _  ___  _ __ | |__  __  _____| |__   __ _ _ __   __ _  ___
#    | | '__/ _` | '_ \/ __| |/ _` | __| |/ _ \| '_ \|  __| \ \/ / __| '_ \ / _` | '_ \ / _` |/ _ \
#    | | | | (_| | | | \__ \ | (_| | |_| | (_) | | | | |____ >  < (__| | | | (_| | | | | (_| |  __/
#    |_|_|  \__,_|_| |_|___/_|\__,_|\__|_|\___/|_| |_|______/_/\_\___|_| |_|\__,_|_| |_|\__, |\___|
#																								    __/ |
#																								   |___/
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

class Language:

	def __init__(self, locale):
		# TODO
		self.locale = locale
		self.name = None
		self.english_name = None
		self.native_name = None
		self.right_to_left = None
		self.flag_url = None

#######################################################################################################
# Translation Methods
#
# Note - when inline translation mode is enable, cache will not be used and translators will
# always hit the live service to get the most recent translations
#
# Some cache adapters cache by source, others by key. Some are read-only, some are built on the fly.
#
# There are three ways to call the tr method
#
# tr(label, description = "", tokens = {}, options = {})
# or
# tr(label, tokens = {}, options = {})
# or
# tr(:label => label, :description => "", :tokens => {}, :options => {})
########################################################################################################

	def translate(self, label, description = None, tokens = {}, options = {}):
		return None


