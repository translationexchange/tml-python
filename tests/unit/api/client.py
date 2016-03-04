from __future__ import absolute_import
# encoding: UTF-8
import six
import weakref
import unittest
from mock import patch
import requests
import json
import tml.api.client as client
from tml.config import CONFIG
from pydoc import cli


class RequestMockResponse(object):
    """ Response for Mock """
    def __init__(self, data, *args, **kwargs):
        self.data = data
        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)

    def set_request(self, request):
        self.request = weakref.ref(request)()

    @property
    def content(self):
        return json.dumps(self.data)

    @property
    def text(self):
        return self.content

    @property
    def status_code(self):
        return 200

    def raise_for_status(self):
        pass

    def json(self):
        if isinstance(self.data, six.string_types):
            self.data = json.loads(self.data)
        return self.data

class InvalidStatusResponse(object):
    """ Response with invalid status for mock """
    def __init__(self, exception):
        self.exception = exception

    def raise_for_status(self):
        raise self.exception


class RequestMock(object):
    """ Mock for request """
    def __init__(self, response = None):
        """ Mock for requests
            Args:
                response (dict): example response json
                error (Exception): network error
                raise_for_status (Excpetion): status error
        """
        self.response = weakref.ref(response)()
        self.response.set_request(self)

    def request(self, method, url, params, **kwargs):
        """ Stub for get request
            Args:
                url (string): URL
                params (dict): get params
            Returns:
                dict: mocked data
        """
        self.method = method
        self.url = url
        self.params = params
        self.response.url = url
        return self.response


class RequestFault(object):
    """ Error """
    def __init__(self, exception):
        self.exception = exception

    def request(self, method, url, params, **kwargs):
        raise self.exception


class TranslatorMock(object):
    def __call__(self):
        return self

    def is_inline(self):
        return True


class ClientTest(unittest.TestCase):
    """ Test client """

    def diff_(self, params):
        generic_params = set(('app_id', 'access_token', 'key'))
        incoming_params = set(params.keys())
        return incoming_params - generic_params

    def check_in_(self, params, param):
        return param in self.diff_(params)

    @patch('tml.api.client.get_current_translator', TranslatorMock)
    def test_success(self):
        """ Test success response """
        # mock http response:
        expected = {'result':'OK'}
        client.requests = RequestMock(RequestMockResponse(expected))
        c = client.Client('qwerty', '123124512412')
        # execute request:
        resp = c.get('test', params={'param':'value'}, opts={'response_class': RequestMockResponse, 'uncompressed': True})
        self.assertEquals(expected, resp, 'Return response')
        # check url and query building:
        self.assertEquals(CONFIG.api_host() + '/v1/test', client.requests.url, 'Call URL')
        self.assertTrue(self.check_in_(client.requests.params, 'param'), 'Token sent as GET parameter')
        # check call with no params:
        resp = c.get('test')
        self.assertTrue(len(self.diff_(client.requests.params)) == 0)
        # check string response:
        expected = 'Hello world'
        client.requests = RequestMock(RequestMockResponse(expected))
        resp = c.get('test', params={'param':'value'}, opts={'response_class': RequestMockResponse, 'uncompressed': True})
        self.assertEquals(expected, resp, 'Return response')

    @patch('tml.api.client.get_current_translator', TranslatorMock)
    def test_network_error(self):
        """ Check network error case """
        error = Exception('My error')
        client.requests = RequestFault(error)
        c = client.Client('qwerty', '123')
        with self.assertRaises(Exception) as context:
            c.get('test', params={'param':'value'})
        self.assertEquals(error, context.exception)

    @patch('tml.api.client.get_current_translator', TranslatorMock)
    def test_api_error(self):
        """ Test error from API """
        expected = {'error':'Error message'}
        client.requests = RequestMock(RequestMockResponse(expected))
        c = client.Client('qwerty', '123')
        with self.assertRaises(client.APIError) as context:
            c.get('test', params={'param':'value'}, opts={'response_class': RequestMockResponse, 'uncompressed': True})
        self.assertEquals('Error message', context.exception.error, 'Check API error')


if __name__=='__main__':
    unittest.main()
