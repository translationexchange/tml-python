# encoding: UTF-8
import unittest
import requests
from tml.api import client
from pydoc import cli


class RequestMockResponse(object):
    """ Response for Mock """
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
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
        self.response = response

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

    def request(self, method, url, params):
        raise self.exception

class ClientTest(unittest.TestCase):
    """ Test client """
    def test_success(self):
        """ Test success response """
        # mock http response:
        expected = {'result':'OK'}
        client.requests = RequestMock(RequestMockResponse(expected))
        c = client.Client('qwerty')
        # execute request:
        resp = c.get('test', {'param':'value'})
        self.assertEquals(expected, resp, 'Return response')
        # check url and query building:
        self.assertEquals('https://api.translationexchange.com/v1/test', client.requests.url, 'Call URL')
        self.assertEquals({'access_token':'qwerty', 'param': 'value'}, client.requests.params, 'Token sent as GET parameter')
        # check call with no params:
        resp = c.get('test')
        self.assertEquals({'access_token':'qwerty'}, client.requests.params, 'Call with no params')
        # check string response:
        expected = 'Hello world'
        client.requests = RequestMock(RequestMockResponse(expected))
        resp = c.get('test', {'param':'value'})
        self.assertEquals(expected, resp, 'Return response')


    def test_network_error(self):
        """ Check network error case """
        error = Exception('My error')
        client.requests = RequestFault(error)
        c = client.Client('qwerty')
        with self.assertRaises(client.HttpError) as context:
            c.get('test', {'param':'value'})

        self.assertEquals(
                          'TML API call fault to https://api.translationexchange.com/v1/test with Exception: My error',
                          str(context.exception),
                          'Check exception message')
        self.assertEquals(error, context.exception.error, 'Check error proxy')

    def test_api_error(self):
        """ Test error from API """
        expected = {'error':'Error message'}
        client.requests = RequestMock(RequestMockResponse(expected))
        c = client.Client('qwerty')
        with self.assertRaises(client.APIError) as context:
            c.get('test', {'param':'value'})
        self.assertEquals('Error message', context.exception.error, 'Check API error')


if __name__=='__main__':
    unittest.main()
