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



class Config:

	def __init__(self, current_locale = None, current_user = None):
		self.enabled = True
		self.default_locale = "en-US"
		self.default_level  = 0
		self.format = "html"
		

		self.current_locale_method =  current_locale
		self.current_user_method = current_user
		
		self.application = None

		self.translator_options = dict(
	        debug = False,
	        debug_format_html = "<span style='font-size:20px;color:red;'>{</span> {$0} <span style='font-size:20px;color:red;'>}</span>",
	        debug_format = '{{{{$0}}}}',
	        split_sentences = False,
	        nodes= dict(
	            ignored =    [],
	            scripts =    ['style','script'],
	            inline =    ['a','span', 'i', 'b', 'img', 'strong', 's', 'em', 'u', 'sub', 'sup'],
	            short =     ['i', 'b'],
	            splitters =  ['br', 'hr']
			),
	        attributes = dict(
	            labels =     ['title', 'alt']
			),
	        name_mapping = dict(
	            b =    'bold',
	            i =    'italic',
	            a =    'link',
	            img =  'picture'
	        ),
	        data_tokens = dict(
	            special = False,
	            numeric = False,
	            numeric_name = 'num'
			)
		)

		self.context_rules = dict(
            number = dict(
                variables = dict()
            ),
            gender  = dict(
                variables = {
                 '@gender': 'gender'
                }
            ),
	        genders = dict(
		        variables = {
			        'genders' : lambda list : [ l.gender  for l in list ],
		            '@size' : lambda  list: len(list)
		          }
				),
	        date = dict(
	          variables = dict(),
			),
	        time = dict(
	          variables = ()
			),
	        list = dict(
	          variables = {
	            '@count' :  lambda  list: len(list)
	          }
			)
	    )
