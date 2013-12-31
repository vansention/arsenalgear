#encoding=utf-8

from tornado.web import RequestHandler
from tornado import template
from sqlalchemy import desc,func,asc
import json,yaml
from datetime import datetime,timedelta
import traceback

from db.schema import Base,Session,engine,make_table_model
from settings import TEMPLATE_PATH

from common.log import logger

#try:
#    logger = LOGGER[CHART_NAME + LOG_NORM_TAG]
#    logerror = LOGGER[CHART_NAME + LOG_ERROR_TAG]
#except BaseException, e:
#    import logger
#    logerror = logger

DISPLAY_COUNT = 5
TIME_FORMAT = "%m-%d %H:%M"

def data_counter(iterable, max_cnt=None):
    tmp = None 
    for i in iterable:
        i = int(i)
        if tmp is None:
            tmp = i
            continue
        n = (i - tmp) if not i<tmp else i 
        tmp = i
        yield n

def data_jump(iterable,step=1):
    tmp = 0
    for i in iterable:
        if tmp == 0:
            tmp = step 
            yield i
        else:
            tmp = tmp - 1

dataSource = {
    'counter': data_counter    
}

class Model(RequestHandler):
    def get(self,tablename):
        session = Session()
        M = make_table_model(tablename.encode('utf-8'))   
        filter_args = []
        filter_args = [ getattr(M,k) == v[0] for k,v in self.request.arguments.items()]
        if filter_args:
            models =  session.query(M).filter(*filter_args).order_by(desc('id')).limit(100)
        else:
            models =  session.query(M).order_by(desc('id')).limit(100)

        models = [ [ getattr(model,c.name) for c in M.__table__._columns] for model in models]
        session.close()
        self.render('chart/model.html',tablename=tablename,models=models,columns=M.__table__._columns)

class ChartSchema(RequestHandler):
    def get(self):
        session = Session()
        Schema = make_table_model('system_chartschema') 
        query = session.query(Schema).order_by(desc('id'))
        session.close()
        self.render('chart/schema.html',query=query)

class ChartSchemaInsert(RequestHandler):
    def get(self,):
        self.render('chart/schema_insert.html')

    def post(self,):
        if not self.request.arguments:
            self.render('chart/schema_insert.html')
        else:
            session = Session()
            M = make_table_model('system_chartschema')
            m = M()
            for k, v in self.request.arguments.items():
                setattr(m, k, v[0])
            session.add(m)
            session.commit()
            session.close()
            return self.redirect('/chart/schema/')

class SchemaEdit(RequestHandler):
    def get(self,name):
        session = Session()
        Schema = make_table_model('system_chartschema')
        schema =  session.query(Schema).filter(Schema.name==name).one()
        session.close()
        self.render('chart/schema_edit.html',schema=schema)

    def post(self,name):
        session = Session()
        Schema = make_table_model('system_chartschema')
        schema =  session.query(Schema).filter(Schema.name==name).one()
        schema.name = self.request.arguments.get('name')[0]
        schema.schema = self.request.arguments.get('schema')[0]
        session.commit()
        session.close()
        return self.redirect('/chart/schema/')

def get_field(field_name):
    table_name,field_name = field_name.split('.')
    Model = make_table_model(table_name)
    field = getattr(Model,field_name)
    return Model,field

def _parse_query(query,field_query,option = {}):
    time_series = []
    field_count = len(field_query) - 1
    series = [ {'name':field.name,'data':[]} for field in field_query[:-1] ]

    # modify step position, not here, and there is no need to config step in the yaml
    # this is a stupid data bug
    if True and option.get('step'):
        query = data_jump(query,option.get('step'))

    for q in query:
        try:
            time_series.append(q[-1].strftime(option['timeformat']))
        except BaseException,e:
            time_series.append(q[-1].strftime(TIME_FORMAT))
        for i in range(field_count):
            series[i]['data'].append(q[i])
    
    if option.get('dataSource'):
        for sr in series:
            sr['data'] = list(dataSource[option['dataSource']](sr['data']))

    if option.get('chartType'):
        for sr in series:
            sr['type'] = option.get('chartType') 
            
    data = {
        'plotOptions': {
            'area': {
                'marker':{'enabled':False},
                'lineWidth':0.1
                #'lineColor':"#f70a0a"
            }    
        },
        'title':{
            'text': option.get('title','Chart')
        },
        'xAxis':{
            'type': 'datetime',
            'categories': time_series,
            'labels':{
                'rotation':1,
                'step':(len(time_series)+DISPLAY_COUNT-1)/DISPLAY_COUNT
                #'step':(len(time_series)/DISPLAY_COUNT)
            }
        },
        'yAxis':{
            
        },
        'series': series ,
    }
    return data

def _drawChart(data,option):
    pass

oneDatAgo = lambda : (datetime.today() - timedelta(hours=24)).strftime('%Y-%m-%d 0:0') 
#only display 24 hours data
oneDatAgo = lambda : (datetime.today() - timedelta(hours=24)).strftime('%Y-%m-%d %H:0')

someHourAgo = lambda x: (datetime.today() - timedelta(hours=x)).strftime('%Y-%m-%d %H:0')

def data_counter(iterable):
    tmp = None 
    for i in iterable:
        i = int(i)
        if tmp is None:
            tmp = i
            continue
        n = i - tmp
        tmp = i
        yield n

# unused  --
def data_jump(iterable,step=1):
    tmp = 0
    for i in iterable:
        if tmp == 0:
            tmp = step 
            yield i
        else:
            tmp = tmp - 1

#support any operations of multi_conditions, the condition will be datetime in last 24 hours by default if there are no conditions
def get_filter_args(M, params={}, interval=6):
    sep = '__'
    _datetime_tag = False
    _datetime_name = 'datetime'
    _datetime_default_op = '__gt__'
    filter_args = []
    for k, v in params.items():
        if k.startswith(_datetime_name):
            _datetime_tag = True
        parts = k.split(sep)
        filter_args.append( getattr(M, parts[0])==v if len(parts)!=2 else getattr(getattr(M, parts[0]),sep+parts[1]+sep)(v))
    if not _datetime_tag:
        filter_args.append( getattr(getattr(M, _datetime_name), _datetime_default_op)(someHourAgo(interval)))
        #filter_args.append( getattr(getattr(M, _datetime_name), _datetime_default_op)(oneDatAgo()))
    return filter_args

def get_filter_args1(M,parms):
    return [ getattr(M,k) == v for k,v in parms.items() if not k.startswith('datetime')]

# unused --
def get_datetime_filter(datetime_field,params={}):
    for k,v in params.items():
        if k.startswith('datetime'):
            print k,v
    datetime_query = [  (k,v) for k,v in params.items() if k.startswith('datetime')]
    if not datetime_query:
        datetime_query = [ ('datetime__gt',oneDatAgo()) ]

    filter_args = []
    for k,v in datetime_query:
        _, cmp_str = k.split('datetime')
        if cmp_str:
            cmp_func = cmp_str + '__'
        else:
            cmp_func = '__eq__'
        filter_args.append(getattr(datetime_field,cmp_func)(v))
    return filter_args

DEFAULT_OFFSET = 100
DEFAULT_DATE_QUERY = [datetime.today().strftime('%Y-%m-%d 0:0')]

def get_group_fields(fields_str):
    for field_str in fields_str:
        _ , field = get_field(field_str)
        yield field

def make_query(name,params={},default_conf={}):
    session = Session()
    Schema = make_table_model('system_chartschema')
    schema = session.query(Schema).filter(Schema.name==name).one()
    schema = yaml.load(schema.schema)

    XModel,xfield = get_field(schema[name]['X'])
    y = schema[name]['Y']
    time_interval = schema[name]['interval'] if schema[name].has_key('interval') else 12

    field_query = []
    filter_args = []
    group_by = []

    for table_field ,options in y.items():
        if options is None: options = {}
        Model,field = get_field(table_field)
        filter_args = get_filter_args(Model, params, time_interval)
        if options and options.get('func'):
            function = getattr(func,options['func'])
            field = function(field)

        field_query.append(field)
    field_query.append(xfield)
    query = session.query(*field_query)
    filter_function = getattr(query,'filter')

    query = filter_function(*filter_args)
    if schema[name].get('group'):
        fields = get_group_fields(schema[name]['group'])
        query = query.group_by(*fields)
    query = query.order_by(asc('datetime'))
    logger.debug(str(query))
    option = schema[name].get('option',{})
    option.update(default_conf)
    result = _parse_query(query,field_query,option)
    session.close()
    return json.dumps(result)


class DrawSchema(RequestHandler):
    def get(self,name):
        configMap = {'width':1024, 'height':400, 'timeformat':TIME_FORMAT}
        params = {}
        try:
            for k, v in self.request.arguments.items():
                if not configMap.has_key(k):
                    params[k] = v[0]
                else:
                    configMap[k] = v[0]
            logger.info(name+str(params))
            data = make_query(name,params, configMap)
            self.render('chart/chart.html',data=data, conf=configMap)
        except BaseException, e:
            logerror.error(traceback.format_exc(e))


class Tmp(RequestHandler):

    def get(self,datestr):
        session = Session()
        M = make_table_model('skylight')
        res = session.execute("select sum(count) ,datetime from skylight where date(datetime) = '%s' group by datetime"%datestr).fetchall()
        res = [ (str(r[1]),int(r[0])) for r in res ]
        res = json.dumps(res)
        self.render('chart/tmp.html',res = res)
