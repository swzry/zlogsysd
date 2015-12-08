# -*- coding: UTF-8 -*-
from dbsettings import ConfigurePeeWee
from peewee import Model
from peewee import CharField, IntegerField, BigIntegerField, TextField, ForeignKeyField, DateTimeField
from DataConvert import BigIntUniqueID
import uuid,datetime

pwdb = ConfigurePeeWee()

class BaseModel(Model):
	class Meta:
		database = pwdb

class LogApp(BaseModel):
	name = CharField(max_length=128,unique=True)
	desc = TextField()
	appkey = CharField(max_length=128)
	secret = CharField(max_length=128)

class LogSrc(BaseModel):
	name = CharField(max_length=128)
	app = ForeignKeyField(LogApp)

class LogItem(BaseModel):
	id = BigIntegerField(primary_key=True)
	src = ForeignKeyField(LogSrc)
	level = IntegerField()
	time = DateTimeField()
	type = CharField(max_length=32)
	content = TextField()

def DB_Init():
	pwdb.connect()
	LogApp.create_table()
	LogSrc.create_table()
	LogItem.create_table()
	thisapp = LogApp.get_or_create(name="zlogsys",defaults={"desc":"This Log Server.","appkey":"","secret":""})
	LogSrc.get_or_create(name="serverlog",defaults={"app":thisapp})

class Exceptions:
	class LogAppNotExist(Exception):
		pass

class LoggerModel():
	def __init__(self,logappname,logsrcname):
		try:
			logapp = LogApp.get(name=logappname)
			self.logsrc = LogSrc.get(app=logapp, name=logsrcname)
		except LogApp.DoesNotExist:
			raise Exceptions.LogAppNotExist
		except LogSrc.DoesNotExist:
			raise  Exceptions.LogAppNotExist

	def addlog(self,level,type,content):
			LogItem.create(id=BigIntUniqueID(),src=self.logsrc,level=level,time=datetime.datetime.now(),content=repr(uuid.uuid4()))
