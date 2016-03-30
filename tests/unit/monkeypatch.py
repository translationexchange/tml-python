import datetime
from tml.monkeypatch import patch_types
from tml.ext import date as date_ext, datetime as datetime_ext

def test_monkeypatch():

    # test before
    for method in date_ext:
        assert not hasattr(datetime.date, method)
    for method in datetime_ext:
        assert not hasattr(datetime.datetime, method)

    patch_types()

    # test after
    for method in date_ext:
        assert hasattr(datetime.date, method) and callable(getattr(datetime.date, method))
    for method in datetime_ext:
        assert hasattr(datetime.datetime, method) and callable(getattr(datetime.datetime, method))
