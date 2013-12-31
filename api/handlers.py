#encoding=utf-8

from datetime import datetime
import time
import simplejson as json
import traceback

from tornado.web import RequestHandler
from sqlalchemy import desc

from db.schema import Base,Session,engine,make_table_model

from common import utils,cache
from common.log import logger

from settings import CACHE_NAME

class Index(RequestHandler):
    def get(self):
        pass


class Model(RequestHandler):
    def __init__(self,*args,**kwargs):
        super(Model,self).__init__(*args,**kwargs)
        self.redis_cli = cache.get_redis()

    def get(self,tablename):
        try:
            session = Session()
            M = make_table_model(tablename.encode('utf-8'))   
            #filter_args = [ getattr(M,k)==v[0] for k,v in self.request.arguments.items()]
            _params = {}
            [_params.update({k: v[0]}) for k, v in self.request.arguments.items()]
            logger.info(tablename+str(_params))
            filter_args = utils.get_filter_args(M, _params)
            if filter_args:
                models =  session.query(M).filter(*filter_args).order_by(desc('id')).limit(100)
            else:
                models =  session.query(M).order_by(desc('id')).limit(100)
            logger.debug(models)
            models = [ [ getattr(model,c.name) for c in M.__table__._columns] for model in models]
            clms = map(lambda x:x.name, M.__table__._columns)
            # hide the primary_key 
            result = map(lambda x: dict(zip(clms[1:], x[1:])), models)
            for item in result:
                for k in item:
                    if  type(item[k])==datetime:
                        item[k] = item[k].strftime("%Y-%m-%d %H:%M:%S")
                    elif type(item[k])==unicode:
                        item[k] = item[k].strip()
            self.write(json.dumps(result))
        except BaseException, e:
            self.write(json.dumps({'msg':'Request Error'}))
            logger.error(traceback.format_exc(e))
        finally:
            session.close()
     
    def post(self,tablename):
        logger.info(str(self.request.arguments))
        cli = self.redis_cli

        apidata = self.get_arguments('apidata')
        if apidata:
            logger.debug(str(apidata))
            data_list = json.loads(apidata[0])
            for data in data_list:
                cli.rpush('ag:post',{'tablename':tablename.encode('utf-8'),'data':data})
        else:
            data = { k:v[0] for k,v in self.request.arguments.items()}
            logger.debug('redis cli start rpush %s'%time.time())
            cli.rpush(CACHE_NAME,{'tablename':tablename.encode('utf-8'),'data':data})
            logger.debug('redis cli end rpush %s'%time.time())
        self.write({'status':'OK'})

class Doc(RequestHandler):
    def get(self,tablename):
        session = Session()
        M = make_table_model(tablename.encode('utf-8'))   
        cols = [ (c.name,c.type,c.primary_key) for c in M.__table__.columns]
        self.render('chart/doc.html',tablename=tablename,cols=cols)

