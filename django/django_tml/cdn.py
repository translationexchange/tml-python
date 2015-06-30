# encoding: UTF-8
"""
# Copyright (c) 2015, Translation Exchange, Inc.
#
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

from tml.api.client import Client as APIClient
from tml.api.cdn import Client as CDNClient
from .cache import CachedClient
from django.conf import settings

def build_client():
    """ Build client for CDN """
    if settings.TML.get('cdn_version'):
        # CDN version defined in config:
        version = settings.TML.get('cdn_version')
    else:
        # GET version from API:
        version = CDNClient.current_version( # fetch current version from API
            CachedClient.wrap( # using standart cache
                APIClient(settings.TML.get('token')) # with base API client
            )
        )

    return CachedClient.wrap(# Use cache
        CDNClient(settings.TML.get('token'), version) # for CDN client
    )

