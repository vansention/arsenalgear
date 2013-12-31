#coding: utf-8

from datetime import datetime, timedelta

oneDatAgo = lambda : (datetime.today() - timedelta(hours=24)).strftime('%Y-%m-%d %H:0')
def get_filter_args(M, params={}):
    sep = '__'
    _datetime_tag = False
    _datetime_name = 'datetime'
    _datetime_default_op = '__gt__'
    filter_args = []
    print params.items()
    for k, v in params.items():
        if k.startswith(_datetime_name):
            _datetime_tag = True
        parts = k.split(sep)
        filter_args.append( getattr(M, parts[0])==v if len(parts)!=2 else getattr(getattr(M, parts[0]),sep+parts[1]+sep)(v))
    if not _datetime_tag:
        filter_args.append( getattr(getattr(M, _datetime_name), _datetime_default_op)(oneDatAgo()))
    return filter_args

def data_counter(iterable, max_cnt=None):
    tmp = None 
    for i in iterable:
        i = int(i)
        if tmp is None:
            tmp = i
            continue
        n = i - tmp
        tmp = i
        yield n

def parse_query(query,field_query,option = {}):
    time_series = []
    field_count = len(field_query) - 1
    series = [ {'name':field.name,'data':[]} for field in field_query[:-1] ]

    # modify step position, not here, and there is no need to config step in the yaml
    # this is a stupid data bug
    if False and option.get('step'):
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
                'marker':{'enabled':False}    
            }    
        },
        'title':{
            'text': option.get('title','Chart')
        },
        'xAxis':{
            'type': 'datetime',
            'categories': time_series,
            'labels':{
                'step':len(time_series)/DISPLAY_COUNT
            }
        },
        'yAxis':{
            
        },
        'series': series ,
    }
    return data



def get_field(field_name):
    table_name,field_name = field_name.split('.')
    Model = make_table_model(table_name)
    field = getattr(Model,field_name)
    return Model,field


