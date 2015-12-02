import logging

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
		lkey = "%s#[%s](%s)"%(self.prefix,self.appname,self.srcname)
		key = "%s[%s]%d"%(self.prefix,self.appname,BigIntUniqueID())
		self.redis.hset(key,'app',self.appname)
		self.redis.hset(key,'src',self.srcname)
		self.redis.hset(key,'type','basic')
		self.redis.hset(key,'level',str(record.levelno))
		self.redis.lpush(lkey,key)
