from . import date as date_ext
from . import datetime as datetime_ext
from . import list as list_ext
from . import str as str_ext

date = {
    'translate': date_ext.translate,
    'tr': date_ext.translate,
    'trl': date_ext.trl
}

datetime = {
    'translate': datetime_ext.translate,
    'tr': datetime_ext.translate,
    'trl': datetime_ext.trl
}

lst = {
    'translate': list_ext.translate,
    'translate_and_join': list_ext.translate_and_join,
    'translate_sentence': list_ext.translate_sentence,
    'tro': list_ext.tro
}

string = {
    'translate': str_ext.translate,
    'trl': str_ext.trl,
}
