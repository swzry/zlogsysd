# -*- coding: utf-8 -*-
# import dbsettings
# from dbmodels import *
# from DataConvert import BigIntUniqueID
# import uuid,datetime
import sys
sys.path.append("../")

from utils.CommonUtils import MakeSummary

print MakeSummary("哈哈哈哈，哈哈哈，呵呵呵，嘻嘻嘻",10)
print MakeSummary("哈哈哈哈hhh~~~",10)

#from utils.HTTPQueryArgs import HTTPQueryArgs
# class RequestObject():
# 	query = {}
#
# req = RequestObject()
# req.query = {
# 	"a":"aa",
# 	"b":"bb",
# 	"蛤":"蛤铪",
# }
#
# ho = HTTPQueryArgs(req)
# print ho.render()

#DB_Init()

# appkey = uuid.uuid4().bytes.encode('hex')
# secret = uuid.uuid4().bytes.encode('hex')
# app1 = LogApp.create(name="TestApp",desc=u"Test Application",appkey=appkey,secret=secret)
# src1 = LogSrc.create(name="TestSource",app=app1)

# app1 = LogApp.get(name="TestApp")
# src1 = LogSrc.get(name="TestSource",app=app1)
#
# LogItem.create(id=BigIntUniqueID(),src=src1,level="INFO",time=datetime.datetime.now(),content=repr(uuid.uuid4()))

# result = LogItem.select().where(LogItem.time>"2016-01-10 19:40:00")
# for i in result:
# 	print i.content

