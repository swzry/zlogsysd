# -*- coding: UTF-8 -*-
from dbsettings import ConfigurePeeWee
from peewee import Model
from peewee import CharField, IntegerField, BigIntegerField, TextField, ForeignKeyField, DateTimeField
from DataConvert import BigIntUniqueID
import datetime

pwdb = ConfigurePeeWee()

class BaseModel(Model):
	class Meta:
		database = pwdb

class LogApp(BaseModel):
	name = CharField(max_length=128,unique=True,index=True)
	desc = TextField(null = True)
	appkey = CharField(max_length=128,null = True,index=True)
	secret = CharField(max_length=128,null = True)

class LogSrc(BaseModel):
	name = CharField(max_length=128,index=True)
	app = ForeignKeyField(LogApp)

class LogItem(BaseModel):
	id = BigIntegerField(primary_key=True)
	src = ForeignKeyField(LogSrc)
	level = IntegerField()
	time = DateTimeField(index=True)
	type = CharField(max_length=32,index=True)
	content = TextField()

def DB_Init():
	pwdb.connect()
	LogApp.create_table(fail_silently=True)
	LogSrc.create_table(fail_silently=True)
	LogItem.create_table(fail_silently=True)
	thisapp,created = LogApp.get_or_create(name="zlogsys",defaults={"desc":"This Log Server.","appkey":"","secret":""})
	LogSrc.get_or_create(name="serverlog",defaults={"app":thisapp.id})
	LogSrc.get_or_create(name="failure",defaults={"app":thisapp.id})

class Exceptions:
	class LogAppNotExist(Exception):
		pass
	class LogSrcNotExist(Exception):
		pass

class LoggerModel():
	def __init__(self,logappname,logsrcname):
		try:
			logapp = LogApp.get(name=logappname)
			self.logsrc = LogSrc.get(app=logapp, name=logsrcname)
		except LogApp.DoesNotExist:
			raise Exceptions.LogAppNotExist
		except LogSrc.DoesNotExist:
			raise  Exceptions.LogSrcNotExist

	def addlog(self,level,ctype,content):
		if isinstance(content,str):
			cte = content
		else:
			cte = repr(content)
		LogItem.create(id=BigIntUniqueID(),src=self.logsrc,level=level,type=ctype,time=datetime.datetime.now(),content=cte)
