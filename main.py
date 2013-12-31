#!/usr/bin/env python
#encoding=utf-8

import optparse
import os

import tornado.ioloop
import tornado.web

from settings import DEBUG,DEFAULT_PORT,SAVE_CACHE_MS
from urls import urlpatterns
from common import cache



config = {
   "static_path" : os.path.join(os.path.dirname(__file__), "static"),
    "template_path" : os.path.join(os.path.dirname(__file__), "templates"),
    "gzip" : True,
    "debug" : DEBUG,
}

parser= optparse.OptionParser()
parser.add_option('-p','--port',dest='port',default=DEFAULT_PORT)
options,args = parser.parse_args()
port = options.port 

if __name__ == '__main__':
    application = tornado.web.Application(urlpatterns,**config)
    application.listen(port)
    main_loop = tornado.ioloop.IOLoop.instance()
    cache_save_loop = tornado.ioloop.PeriodicCallback(cache.save_cache,SAVE_CACHE_MS,io_loop=main_loop)
    cache_save_loop.start()
     
    main_loop.start()


