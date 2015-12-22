import logging,time,random

def BigIntUniqueID():
	ts = long(time.time()*100000000)
	hs = hash(str(time.time())+str(random.random())) & 0x00ffffff
	return ts+hs

class BaseRedisHandler(logging.Handler):
	def __init__(self,redisdb,appname,srcname,prefix=""):
		logging.Handler.__init__(self)
		self.redis = redisdb
		self.appname = appname
		self.srcname = srcname
		self.prefix = prefix

	def emit(self, record):
		try:
			lkey = "%s$[%s](%s)"%(self.prefix,self.appname,self.srcname)
			key = "%s[%s]%d"%(self.prefix,self.appname,BigIntUniqueID())
			pipe =self.redis.pipeline()
			pipe.hset(key,'app',self.appname)
			pipe.hset(key,'src',self.srcname)
			pipe.hset(key,'type','text/plain')
			pipe.hset(key,'level',str(record.levelno))
			pipe.hset(key,'content',record.getMessage())
			pipe.lpush(lkey,key)
			pipe.execute()
		except Exception,e:
			print "Err: %s"%repr(e)
