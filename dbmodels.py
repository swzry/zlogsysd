# -*- coding: UTF-8 -*-
from dbsettings import ConfigurePeeWee
from peewee import Model
from peewee import CharField, IntegerField, BigIntegerField, TextField, ForeignKeyField, DateTimeField

pwdb = ConfigurePeeWee()

class BaseModel(Model):
	class Meta:
		database = pwdb

class LogApp(BaseModel):
	name = CharField(max_length=128)
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
