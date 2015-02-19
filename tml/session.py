# encoding: UTF-8
# --
# Copyright (c) 2015, Translation Exchange, Inc.
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

from tml.application import Application


class Session:
    def __init__(self):
        self.application = None
        self.current_user = None
        self.current_language = None
        self.current_translator = None
        self.current_source = None
        self.current_component = None
        self.block_options = None
        self.key = None
        self.secret = None
        self.host = None
        self.application = None


    def reset(self):
        self.application = None
        self.current_user = None
        self.current_language = None
        self.current_translator = None
        self.current_source = None
        self.current_component = None
        self.block_options = None


    @classmethod
    def initialize(cls, key=None, secret=None, host=None):
        logging.debug("Initializing session (%s,%s,%s)" % (key, secret, None))
        session = Session()
        session.key = None
        session.secret = None
        session.host = None

        cls.__instance = session  # Set module level instance
        session.application = Application()
        # TODO add logic for setting up application
        return session.application






