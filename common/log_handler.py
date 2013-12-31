#coding: utf-8

import types
import logging
import logging.handlers

DEFAULT_LOG_NAME = 'zamppass'
DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s %(process)d %(message)s'
DEFAULT_LOG_SIZE = 100*1024*1024
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_BACKUPCNT = 50

def get_logger(log_file, level=None, Format=None, maxLogSize=None, backupCnt=None):
    logger = logging.getLogger(DEFAULT_LOG_NAME)
    _level = DEFAULT_LOG_LEVEL 
    if level is not None:
        try:
            _level = getattr(logging, level)
        except BaseException, e:
            pass
    logger.setLevel(_level)
    
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        mode = 'a',
        maxBytes = maxLogSize if not maxLogSize else DEFAULT_LOG_SIZE,
        backupCount = backupCnt if not isinstance(backupCnt, types.IntType) else DEFAULT_LOG_BACKUPCNT
    )
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
