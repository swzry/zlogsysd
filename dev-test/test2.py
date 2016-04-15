from GeneralLoggingHandler import  BaseRedisHandler
import logging,redis

print "Ready"

r = redis.Redis(host='10.7.0.1', port=6379, db=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logh = BaseRedisHandler(r,'zlogsysd','serverlog',prefix='zlogsys')
logc = logging.StreamHandler()
logh.setLevel(logging.DEBUG)
logc.setLevel(logging.DEBUG)
logh.setFormatter(formatter)
logc.setFormatter(formatter)
logger = logging.getLogger('main')
logger.addHandler(logh)
logger.addHandler(logc)
logger.setLevel(logging.DEBUG)

logger.info('hello, world~ This is an Test Log~ Nyan~~~~~~')

print "OK"