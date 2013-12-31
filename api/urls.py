#encoding=utf-8

from handlers import Index,Model,Doc

urlpatterns = [
    (r'^/api/$',Index),
    (r'^/api/model/(?P<tablename>\w+)/$',Model),
    (r'^/api/model/(?P<tablename>\w+)/doc/$',Doc),
]
