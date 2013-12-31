
from datetime import datetime
import json
import traceback

from settings import MAX_SAVE
from db.schema import Base,Session,engine,make_table_model

import redis

from common.log import logger
from settings import CACHE_NAME,CACHE_DB




pool = redis.ConnectionPool(host='localhost', port=6379,db=CACHE_DB)

def get_redis():
    cli = redis.Redis(connection_pool=pool)
    return cli


def save_records(records):
    session = Session()
    for r in records:
        try:
            r = eval(r)
            tablename = r['tablename']
            data = r['data']
            M = make_table_model(tablename.encode('utf-8'))   
            m = M()
            for k,v in data.items():
                setattr(m,k,v)
            session.add(m)
            logger.debug('%s save %s'%(tablename,str(m)))
        except Exception,e:
            logger.error(traceback.format_exc(e))
    session.commit()
    session.close()



def save_cache():
    cli = get_redis()
    records = cli.lrange(CACHE_NAME,0,1000)
    cli.ltrim(CACHE_NAME,1001,-1)
    logger.debug(records) 
    save_records(records)
