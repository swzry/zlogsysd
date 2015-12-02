from GeneralLoggingHandler import  BaseRedisHandler
import logging,redis

print "Ready"

r = redis.Redis(host='10.7.0.1', port=6379, db=2)
logh = BaseRedisHandler(r,'TestApp','TestSource',prefix='log_')
logger = logging.getLogger('main')
logger.addHandler(logh)

logger.info('hello, world~ This is an error~ Nyan~~~~~~')

print "OK"