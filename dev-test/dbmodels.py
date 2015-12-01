# -*- coding: UTF-8 -*-
from sqlalchemy import Column
from sqlalchemy.types import CHAR, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()

class LogSource(BaseModel):
    __tablename__ = 'logsrc'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))

class LogItem(BaseModel):
	__tablename__ = 'logitems'
	id = Column(BigInteger, primary_key=True)


def init_db(engine):
    BaseModel.metadata.create_all(engine)