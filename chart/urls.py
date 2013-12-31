#encoding=utf-8

from handlers import Model,ChartSchema,DrawSchema,Tmp, ChartSchemaInsert, SchemaEdit

urlpatterns = [
    (r'^/chart/model/(?P<tablename>\w+)/$',Model),
    (r'^/chart/schema/$',ChartSchema),
    (r'^/chart/schema/insert/$',ChartSchemaInsert),
    (r'^/chart/schema/(?P<name>\w+)/edit/$',SchemaEdit),
    (r'^/chart/schema/(?P<name>\w+)/$',DrawSchema),
    (r'^/chart/tmp/(?P<datestr>.+)/$',Tmp),
]
