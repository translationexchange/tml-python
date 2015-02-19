# -*- coding: utf-8 -*-
from tml.exceptions import Error

class Application(object):
    """ Application """
    def __init__(self, client, data):
        """ Application instance
            Args:
                client (Client): api client
                data (dict): application data
        """
        self.client = client
        self.data = data

    @classmethod
    def current(cls, client):
        """ Load current application
            Args:
                client (Client): api client
            Throws:
                api.ClientError
            Returns:
                Application
        """
        return Application(client = client, data = client.get('applications/current', {'definition':1}))

    @classmethod
    def load_by_id(cls, id, client):
        """ Load current application
            Args:
                id (int): application id
                client (Client): api client
            Throws:
                api.ClientError
            Returns:
                Application
        """
        return Application(client = client, data = client.get('applications/%d' % id, {'definition':1}))

    @property
    def id(self):
        """ Application ID getter
            Returns:
                (int): application id in sysem
        """
        return self.data['id']

    @property
    def default_locale(self):
        """ Get default locale for app """
        return self.get_locale(self.data['default_locale'])

class ApplicationError(Error):
    """ Error in application context """
    def __init__(self, application):
        self.application = application

    @property
    def context(self):
        """ Context message """
        return 'in application %d' % self.application.id


