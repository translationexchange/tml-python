# encoding: UTF-8

def allpages(client, url, params):
    """ Return results from all pages 
        Args:
            client (Client): API client
            url (string): URL
            params (dict): request params
    """
    total_pages = 1
    params['page'] = 0
    ret = []
    while params['page'] < total_pages:
        params['page'] = params['page'] + 1
        resp = client.get(url, params)
        ret = ret + resp['results']
        total_pages = resp['pagination']['total_pages']
    return ret