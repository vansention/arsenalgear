#coding: utf-8
import os,logging

#from common import log_handler

DEBUG = False 
DEFAULT_PORT = 22222

INSTALL_APP = (
    'api',
    'chart',
)

DB_ENGINE_DICT = {
    'default':'postgresql://postgres:1q2w3e4r@192.168.1.201:5433/arsenalgear',
    'test':'postgresql://postgres:1q2w3e4r@192.168.1.201:5433/arsenalgear',
    #'default':'mysql://root:1q2w3e4r@localhost/ArsenalGear',
}


PATH = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(PATH,'templates')
#LOG_DIR = os.path.join(PATH, 'logs')
LOG_DIR = '/var/log/ArsenalGear/'
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

#CHART_NAME = 'chart'
#API_NAME = 'api'
#LOG_NORM_TAG = '_norm'
#LOG_ERROR_TAG = '_error'
#LOG_CONFIG = {
#    CHART_NAME:{'norm_file':'zamppass_chart_normal.log', 'error_file':'zamppass_chart_error.log','level':'DEBUG'},
#    API_NAME:{'norm_file':'zamppass_api_normal.log', 'error_file':'zamppass_api_error.log', 'level':'INFO'}
#}
#LOGGER = {}
#for k in LOG_CONFIG:
#    _nfile = os.path.join(LOG_DIR, LOG_CONFIG[k]['norm_file'])
#    _efile = os.path.join(LOG_DIR, LOG_CONFIG[k]['error_file'])
#    LOGGER[k+LOG_NORM_TAG] = log_handler.get_logger(_nfile, LOG_CONFIG[k]['level'])
#    LOGGER[k+LOG_ERROR_TAG] = log_handler.get_logger(_efile, 'ERROR')
#
if DEBUG:
    DB_ENGINE = DB_ENGINE_DICT['test']
else:
    DB_ENGINE = DB_ENGINE_DICT['default']


LOG_FILE = 'arsenalgear.log'
LOG_LEVEL = logging.INFO

SAVE_CACHE_MS = 1000
MAX_SAVE = 1000
CACHE_NAME = 'ag:post'
CACHE_DB = 0 

try:
    from local_settings import *
    print 'import local settings'
except:
    pass
