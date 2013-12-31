#encoding=utf-8

from tornado import web

from settings import INSTALL_APP


def url_config():
    urlpatterns = [
        (r"/static/(.*)", web.StaticFileHandler, {"path": "static"}), 
    ] 
    for app in INSTALL_APP:
        try:
            module = __import__('%s.urls'%app,globals(), locals(), ['eggs', 'sausage'], -1) 
        except ImportError,e:
            print e
            continue
        urls = getattr(module,'urlpatterns')
        urlpatterns.extend(urls)
    return urlpatterns


urlpatterns = url_config()
