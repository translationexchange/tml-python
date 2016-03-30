import datetime
from tml.monkeypatch import patch_types
from tml.ext import date as date_ext, datetime as datetime_ext, string as str_ext, lst as list_ext

def test_monkeypatch():

    # test before
    for method in date_ext:
        assert not chk_method(datetime.date, method)
    for method in datetime_ext:
        assert not chk_method(datetime.datetime, method)
    for method in str_ext:
        assert not chk_method(str, method)
    for method in list_ext:
        assert not chk_method(list, method)

    patch_types()

    # test after
    for method in date_ext:
        assert chk_method(datetime.date, method)
    for method in datetime_ext:
        assert chk_method(datetime.datetime, method)
    for method in str_ext:
        assert chk_method(str, method)
    for method in list_ext:
        assert chk_method(list, method)


def chk_method(klass, method):
    return hasattr(klass, 'tml_{}'.format(method)) and callable(getattr(klass, 'tml_{}'.format(method)))
