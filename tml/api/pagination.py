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
    ret = None
    while params['page'] < total_pages:
        params['page'] = params['page'] + 1
        resp = client.get(url, params)
        if ret is None:
            ret = resp['results']
        elif type(ret) is list:
            ret = ret + resp['results']
        elif type(ret) is dict:
            ret.update(resp['results'])
        else:
            raise Exception('Results with type %s can not be used in pagination' % type(resp['results']))
        try:
            total_pages = resp['pagination']['total_pages']
        except KeyError:
            pass
    return ret