# encoding: UTF-8
"""
# Copyright (c) 2015, Translation Exchange, Inc.
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
"""
__author__ = 'a@toukmanov.ru'
from ..exceptions import Error


def allpages(client, url, params=None, opts=None):
    """ Return results from all pages
        Args:
            client (Client): API client
            url (string): URL
            params (dict): request params
    """
    total_pages = 1
    params['page'] = 0
    ret = None

    while params['page'] < total_pages:
        params['page'] = params['page'] + 1
        resp = client.get(url, params=params, opts=opts)
        if ret is None:
            ret = resp['results']
        elif type(ret) is list:
            ret = ret + resp['results']
        elif type(ret) is dict:
            ret.update(resp['results'])
        else:
            raise Error('Invalid result type %s' % type(resp['results']))
        try:
            total_pages = resp['pagination']['total_pages']
        except KeyError:
            pass
    return ret
