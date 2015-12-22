# -*- coding: UTF-8 -*-
from daemonlib import Daemon
from bottle import Bottle,route,run,get,post,request,HTTPError,static_file,request,error,template
import os,sys,time,traceback,datetime,threading,json,logging
import dbsettings
from dbmodels import  *
now = lambda: time.strftime("[%Y-%b-%d %H:%M:%S]")
maxdate=datetime.datetime.fromtimestamp(2140000000)
##============Global Variable============
basedir,pidfile,currname,shost = "","","",""
webport,syslogport = 9564,9514
CGI = None
proccessMonitorOn = False
redis,redis_conf = dbsettings.ConfigureRedis()
SelfLoggerModel,SelfFailureLoggerModel = None,None
##============================
def RouteTable(app):
	cgiapp=CGI_APP()
	errpages=ERR_PAGES()
##============URL Route List============
	routeDict = {
		'/': cgiapp.index,
		'/about/': cgiapp.about,
	}
	getDict = {
	}
	postDict = {
	}
##=======================================
	for url in routeDict:
		app.route(url)(routeDict[url])
	for url in getDict:
		app.get(url)(getDict[url])
	for url in postDict:
		app.post(url)(postDict[url])
	app.error(403)(errpages.ERR403)
	app.error(500)(errpages.ERR500)
	app.error(500)(errpages.ERR500)
class CGI_APP:
##============CGI APP Class============
	def index(self):
		return 'Constructing...'
	def about(self):
		return currname+" (Now Building...)"


##============Error Pages Class============
class ERR_PAGES:
	def ERR404(self,err):
		return template('404')
	def ERR403(self,err):
		return template('403')
	def ERR500(self,err):
		return template('500')

def str2int(strs):
	strr=filter(lambda x:(x.isdigit or x=='-'),str(strs))
	if strr==None:
		return 0
	elif strr=='':
		return 0
	else:
		return int(strr)

def DoRedisQuene():
	SelfLoggerModel.addlog(logging.DEBUG,'text/plain','DoRedisQuene')
	lst = redis.lrange(redis_conf['prefix']+'#sys_srclist',0,-1)
	SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',"<DEBUG>%s"%repr(lst))
	for i in lst:
		try:
			srcobjn = i.split("@",2)
			if not len(srcobjn) == 2:
				raise Exception("Invalid SrcInfo in 'srclist'")
			lkeyname = "%s$[%s](%s)" % (redis_conf['prefix'],srcobjn[0],srcobjn[1])
			iLoggerModel = LoggerModel(srcobjn[0],srcobjn[1])
			while 1:
				kd = redis.lpop(lkeyname)
				if not kd:
					break
				try:
					dType    = redis.hget(kd,'type')
					dLevel   = str2int(redis.hget(kd,'level'))
					dContent = redis.hget(kd,'content')
					iLoggerModel.addlog(dLevel,dType,dContent)
				except Exceptions,e:
					SelfFailureLoggerModel.addlog(logging.WARNING,'text/plain',"[%s]<FailedWriteDB>%s"%(i,repr(e)))
		except Exceptions,e:
			SelfFailureLoggerModel.addlog(logging.WARNING,'text/plain',"[%s]<FailedDumpRedis>%s"%(i,repr(e)))




##============Start Server Threading============
class RunCGIServer(threading.Thread):
	def run(self):
		CGI = Bottle()
		RouteTable(CGI)
		CGI.run(host=webhost,port=webport,server='cherrypy')

class RunWorker(threading.Thread):
	def run(self):
		while 1:
			try:
				DoRedisQuene()
				time.sleep(20)
			except Exception,e:
				s = traceback.format_exc()
				sys.stderr.write("\n"+now()+"Application was shutdown by a fatal error.\n%s\n"%s)
				sys.stderr.flush()

##============Init============
def dmInit():
	global SelfLoggerModel,SelfFailureLoggerModel
	reload(sys)
	sys.setdefaultencoding('utf-8')
	try:
		os.chdir(basedir)
		SelfLoggerModel = LoggerModel("zlogsys","serverlog")
		SelfFailureLoggerModel = LoggerModel("zlogsys","failure")
		serv = RunCGIServer()
		worker = RunWorker()
		serv.start()
		worker.start()
		SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain','Zlogsys FailureLog Test')
		SelfLoggerModel.addlog(logging.INFO,'text/plain','Zlogsys Server Start')
	except Exception,e:
		time.sleep(5)
		s = traceback.format_exc()
		sys.stderr.write("\n"+now()+"Application was shutdown by a fatal error.\n%s\n"%s)
		sys.stderr.flush()

def syncdb():
	DB_Init()

##============Daemon System============
class MyDaemon(Daemon):
	def _run(self):
		if proccessMonitorOn:
			while True:
				dmInit()
		else:
			dmInit()
			

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf-8')
	basedir = os.environ.get('basedir','[Err]')
	if basedir == "[Err]":
		print "Loading Env...                                        [\033[1;31;40mFAILURE\033[0m]"
		print "Environment Variable '$basedir' Not Found. Did you use 'zlogsysd' daemon script to launch this?"
		sys.exit(2)
	pidfile = os.environ.get('pidfile','[Err]')
	if pidfile == "[Err]":
		print "Loading Env...                                        [\033[1;31;40mFAILURE\033[0m]"
		print "Environment Variable '$pidfile' Not Found. Did you use 'zlogsysd' daemon script to launch this?"
		sys.exit(2)
	prcL = os.environ.get('proccessMonitorOn','0.0.0.0')
	proccessMonitorOn = (prcL == "True")
	webhost = os.environ.get('webhost','0.0.0.0')
	sysloghost = os.environ.get('sysloghost','0.0.0.0')
	swport = os.environ.get('webport','9564')
	webport = str2int(swport)
	if webport == 0:
		print "Loading Env...                                        [\033[1;31;40mFAILURE\033[0m]"
		print "Invalid Value of '$webport'"
		sys.exit(2)
	slport = os.environ.get('syslogport','9514')
	syslogport = str2int(slport)
	if syslogport == 0:
		print "Loading Env...                                        [\033[1;31;40mFAILURE\033[0m]"
		print "Invalid Value of '$syslogport'"
		sys.exit(2)
	currname='zlogsysd'
	daemon = MyDaemon(pidfile,'/dev/null',basedir+currname+'.out.log',basedir+currname+'.err.log')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			print "Starting...                                            [\033[1;32;40mOK\033[0m]"
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
			print "Stopping...                                            [\033[1;32;40mOK\033[0m]"
		elif 'restart' == sys.argv[1]:
			print "Stopping...                                            [\033[1;32;40mOK\033[0m]"
			print "Starting...                                            [\033[1;32;40mOK\033[0m]"
			daemon.restart()
		elif 'syncdb' == sys.argv[1]:
			syncdb()
			print "Database Sync....                                      [\033[1;32;40mOK\033[0m]"
		else:
			print "Unknown Command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "Command Format: %s start|stop|restart" % currname
		sys.exit(2)
