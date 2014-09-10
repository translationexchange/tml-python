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


from datetime import date
import re

class Evaluator:

		@staticmethod
		def drop():
			def f(list,n):
				[list.pop(0) for i in (0,n)]
				return list
			return f

		def __init__(self):
			self.vars = {}
			def label():
				def f(l,r):
					self.vars[l] = r
					return r
				return f


			self.env = {
			    # McCarthy's Elementary S-functions and Predicates
			    'label'   : lambda l, r : label()(l,r),
			    'quote'   : lambda expr :       expr ,
			    'car'     : lambda list :       list[1],
			    'cdr'     : lambda list:      Evaluator.drop()(list,1),
			    'cons'    : lambda e, cell:    [e] + cell ,
			    'eq'      : lambda l, r:       l == r ,
			    'atom'    : lambda expr:       isinstance(expr,(type(None),str,int,float,bool)),
			    'cond'    : lambda c, t, f:    (self.evaluate(t) if self.evaluate(c) else self.evaluate(f))

			    # Tr8n Extensions
				'='       : lambda l, r :       l == r,                                              # ['=', 1, 2]
			    '!='      : lambda l, r:      l != r ,                                             # ['!=', 1, 2]
			    '<'       : lambda l, r:      l < r ,                                              # ['<', 1, 2]
			    '>'       : lambda l, r:      l > r ,                                              # ['>', 1, 2]
			    '+'       : lambda l, r:      l + r ,                                              # ['+', 1, 2]
			    '-'       : lambda l, r:      l - r ,                                              # ['-', 1, 2]
			    '*'       : lambda l, r:      l * r ,                                              # ['*', 1, 2]
			    '%'       : lambda l, r:      l % r ,                                              # ['%', 14, 10]
			    'mod'     : lambda l, r:      l % r ,                                              # ['mod', '@n', 10]
			    '/'       : lambda l, r:      (l * 1.0) / r ,                                      # ['/', 1, 2]
			    '!'       : lambda expr:      not expr ,                                           # ['!', ['true']]
			    'not'     : lambda val:       not val ,                                            # ['not', ['true']]
			    '&&'      : lambda exprs:     all(self.evaluate(expr) for expr in exprs),                         # ['&&', [], [], ...]
			    'and'     : lambda exprs:     all(self.evaluate(expr) for expr in exprs),                         # ['and', [], [], ...]
			    '::'      : lambda exprs:     any(self.evaluate(expr) for expr in exprs),                          # ['::', [], [], ...]
			    'or'      : lambda exprs:     any(self.evaluate(expr) for expr in  exprs),                          # ['or', [], [], ...]
			    'if'      : lambda c, t, f:   self.evaluate(t) if self.evaluate(c) else  self.evaluate(f) ,            # ['if', 'cond', 'true', 'false']
			    'let'     : lambda l, r:      label()(l,r) ,                                       # ['let', 'n', 5]
			    'true'    : lambda  True ,                                                           # ['true']
			    'false'   : lambda  False ,                                                          # ['false']
			
			    'date'    : lambda date:      date.strptime(date, '%Y-%m-%d'),                    # ['date', '2010-01-01']
			    'today'   : lambda date.now().today(),                                               # ['today']
			    'time'    : lambda time:      date.strptime(date '%Y-%m-%d %H:%M:%S'),           # ['time', '2010-01-01 10:10:05']
			    'now'     : lambda date.now(),                                                       # ['now']
			
			    'append'  : lambda l, r:      str(r) + str(l) ,                                    # ['append', 'world', 'hello ']
			    'prepend' : lambda l, r:      str(l) + str(r)                                     # ['prepend', 'hello  ', 'world']
			    # 'match'   : lambda { |search, subject|                                                 # ['match', /a/, 'abc']
			    #   search = regexp_from_string(search)
			    #   not search.match(subject).nil?
			    # },
			    # 'in'      : lambda { |values, search|                                                  # ['in', '1,2,3,5..10,20..24', '@n']
			    #   search = search.to_s.strip
			    #   values.split(',').each do |e|
			    #     if e.index('..')
			    #       bounds = e.strip.split('..')
			    #       return true if (bounds.first.strip..bounds.last.strip).include?(search)
			    #     end
			    #     return true if e.strip == search
			    #   end
			    #   false
			    # },
			#     'within'  : lambda { |values, search|                                                 # ['within', '0..3', '@n']
			#       bounds = values.split('..').map{|d| Integer(d)}
			#       (bounds.first..bounds.last).include?(search)
			#     },
			#     'replace' : lambda { |search, replace, subject|                                       # ['replace', '/^a/', 'v', 'abc']
			#                                                                                            # handle regular expression
			#       if /\/i$/.match(search)
			#         replace = replace.gsub(/\$(\d+)/, '\\\\\1') # for compatibility with Perl notation
			#       end
			#       search = regexp_from_string(search)
			#       subject.gsub(search, replace)
			#     },
			#     'count'   : lambda { |list|                                                          # ['count', '@genders']
			#       (list.is_a?(String) ? vars[list] : list).count
			#     },
			#     'all'     : lambda { |list, value|                                                   # ['all', '@genders', 'male']
			#       list = (list.is_a?(String) ? vars[list] : list)
			#       list.is_a?(Array) ? list.all?{|e| e == value} : false
			#     },
			#     'any'     : lambda { |list, value|                                                   # ['any', '@genders', 'female']
			#       list = (list.is_a?(String) ? vars[list] : list)
			#       list.is_a?(Array) ? list.any?{|e| e == value} : false
			#     },
			}

      def regexp_from_string(self,str)
            pattern = re.compile(str)
            pattern2 = "^\/"
            match1 = re.match(pattern2,str)
            return pattern if not match1 else None
    #
    #     str = str.gsub(/^\//, '')
    #
    #     if /\/i$/.match(str)
    #       str = str.gsub(/\/i$/, '')
    #       return Regexp.new(/#{str}/i)
    #     end
    #
    #     str = str.gsub(/\/$/, '')
    #     Regexp.new(/#{str}/)
    #   end
    #
    #   def reset!
    #     @vars = {}
    #   end
    #
		def apply(self, fn, args)
			#raise "undefined symbols #{fn}" unless @env.keys.include?(fn)
			self.env[fn].call(*args)

    #
		def evaluate(self,expr):
			None
			if self.env['atom'].call(expr):
			  return self.vars[expr] if (expr is string and self.vars[expr]) else expr

			fn = expr[0]
			args = Evaluator.drop(expr,1)

			unless ['quote', 'car', 'cdr', 'cond', 'if', '&&', '||', 'and', 'or', 'true', 'false', 'let', 'count', 'all', 'any'].member?(fn)
			  args = args.map { |a| self.evaluate(a) }
			end
			self.apply(fn, args)

    # end