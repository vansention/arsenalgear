#encoding=utf-8

from new import classobj

from sqlalchemy import create_engine,Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import DB_ENGINE,DEBUG

engine = create_engine(DB_ENGINE, echo=DEBUG)
Base = declarative_base(bind=engine)

Session = sessionmaker(bind=engine)

def make_table_model(tablename):
    __table__ = Table(tablename, Base.metadata, autoload=True, autoload_with=engine)
    return classobj(tablename,(Base,),{'__table__':__table__}) 

