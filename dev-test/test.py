import dbsettings
from dbmodels import *
from DataConvert import BigIntUniqueID
import uuid,datetime

#DB_Init()

# appkey = uuid.uuid4().bytes.encode('hex')
# secret = uuid.uuid4().bytes.encode('hex')
# app1 = LogApp.create(name="TestApp",desc=u"Test Application",appkey=appkey,secret=secret)
# src1 = LogSrc.create(name="TestSource",app=app1)

# app1 = LogApp.get(name="TestApp")
# src1 = LogSrc.get(name="TestSource",app=app1)
#
# LogItem.create(id=BigIntUniqueID(),src=src1,level="INFO",time=datetime.datetime.now(),content=repr(uuid.uuid4()))

result = LogItem.select().where(LogItem.type=="text/plain").where(LogItem.level==20)
for i in result:
	print i.content