import logging
import os
from .utils import rel, APP_DIR
from .base import Singleton
from .exceptions import Error
from .config import CONFIG


class TMLLogRecord(logging.LogRecord):
    def __init__(self, *args):
        super(TMLLogRecord, self).__init__(*args)


class TMLLogger(logging.Logger):

    reserved_keys = ('message', 'asctime')

    def make_record(self, *args, **kwargs):
        extra = kwargs.pop('extra', {})
        record = TMLLogRecord(*args, **kwargs)
        if extra:
            for key in extra:
                if (key in TMLLogger.reserved_keys) or (key in record.__dict__):
                    raise KeyError("TMLLogger: Attemnt to overwrite reserved `%r` in LogRecord" % key)
                    record.__dict__[key] = extra[key] or 'undefined'
        return record


class Logger(Singleton):

    default_path = rel(APP_DIR, 'logs', 'tml.log')
    default_level = logging.DEBUG
    max_bytes = 1024 * 1000 * 3 # 3 MB
    backup_count = 30
    mode = 'a'
    namespace = 'trex.TML'

    def init(self, path=None, log_level=None, **kwargs):
        self.path = Logger.default_path if path is None else path
        dirname = os.path.dirname(self.path)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        self.logger = None
        self.configure(log_level)

    def __getattr__(self, name):
        if name in ('debug', 'info', 'warning', 'error', 'critical', 'log', 'exception'):  # proxy logging methods
            if self.logger is None:  # suppress if not configured
                return lambda *args, **kwargs: None
            return getattr(self.logger, name)
        return getattr(self, name)

    def configure(self, log_level):
        self.logger = logging.getLogger(self.namespace)
        self.logger.setLevel(log_level or Logger.default_level)
        file_handler = logging.handlers.RotatingFileHandler(self.path, mode=self.mode, maxBytes=self.max_bytes, backupCount=self.backup_count)
        file_handler.setFormatter(logging.Formatter(u'[%(asctime)s] - %(name)s - %(message)-4s', '%Y-%m-%d %H:%M:%S'))
        self.logger.addHandler(file_handler)
        self.logger.propagate = False


class LoggerNotConfigured(Error):
    pass


def get_logger(**kwargs):
    return Logger.instance(**CONFIG.logger)


getattr_ = object.__getattribute__


class LoggerMixin(object):
    _logger = None

    def log_it(self, name, *args, **kwargs):
        if not self._logger:
            self._logger = get_logger()
        fn = getattr(self._logger, name, None)
        if fn and callable(fn):
            return fn(*args, **kwargs)
        raise NotImplementedError("")

    def debug(self, *args, **kwargs):
        self.log_it('debug', *args, **kwargs)

    def info(self, *args, **kwargs):
        self.log_it('info', *args, **kwargs)

    def warning(self, *args, **kwargs):
        self.log_it('warning', *args, **kwargs)

    def error(self, *args, **kwargs):
        self.log_it('error', *args, **kwargs)

    def critical(self, *args, **kwargs):
        self.log_it('critical', *args, **kwargs)

    def log(self, *args, **kwargs):
        self.log_it('log', *args, **kwargs)

    def exception(self, *args, **kwargs):
        self.log_it('exception', *args, **kwargs)

