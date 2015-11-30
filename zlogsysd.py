# -*- coding: utf-8 -*-
from daemonlib import Daemon
from bottle import Bottle,route,run,get,post,request,HTTPError,static_file,request,error,template
import MySQLdb
import os.path
import os,sys,time,traceback,datetime,threading,json
now = lambda: time.strftime("[%Y-%b-%d %H:%M:%S]")
sqlf = lambda sql: MySQLdb.escape_string(sql)
maxdate=datetime.datetime.fromtimestamp(2140000000)

##============Global Variable============
basedir,pidfile,currname,shost = "","","",""
webport,syslogport = 9564,9514
CGI = None
proccessMonitorOn = False
##============================
def RouteTable(app):
	cgiapp=CGI_APP()
	errpages=ERR_PAGES()
##============URL Route List============
	routeDict = {
		'/': cgiapp.index,
		'/about.zrycgi': cgiapp.about,
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
	app.route('/EasterEgg/500')(errpages.EERR500)
	app.route('/EasterEgg/403')(errpages.EERR403)
	app.route('/EasterEgg/404')(errpages.EERR404)
	app.error(403)(errpages.ERR403)
	app.error(500)(errpages.ERR500)
	app.error(500)(errpages.ERR500)
##============CGI APP Class============
class CGI_APP:
	def index(self):
		return template('BuildingPage')
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
	def EERR404(self):
		return template('404')
	def EERR403(self):
		return template('403')
	def EERR500(self):
		return template('500')

##============Logging Out Functions============
def elog(msg):
	sys.stderr.write("%s %s\n" %(now(), msg))
	sys.stderr.flush()

def olog(msg):
	sys.stdout.write("%s %s\n" %(now(), msg))
	sys.stdout.flush()

##============MySQL Model Functions============
def MySQLExec(sqlc):
	mysql=MySQLdb.connect(host=jsf['host'], user=jsf['user'],passwd=jsf['passwd'],db="")
	cursor=mysql.cursor()
	rdc=cursor.execute(sqlc)
	return (cursor,rdc,mysql)

def MySQLExecWithPar(sqlc,par):
	mysql=MySQLdb.connect(host=jsf['host'], user=jsf['user'],passwd=jsf['passwd'],db="")
	cursor=mysql.cursor()
	rdc=cursor.execute(sqlc,par)
	return (cursor,rdc,mysql)

def str2int(strs):
	strr=filter(lambda x:(x.isdigit or x=='-'),str(strs))
	if strr==None:
		return 0
	elif strr=='':
		return 0
	else:
		return int(strr)

##============Start Server Threading============
class RunCGIServer(threading.Thread):
	def run(self):
		CGI.run(host=webhost,port=webport,server='cherrypy')

##============Init============
def mainfunc():
	CGI = Bottle()
	RouteTable(CGI)
	#fsqlp=open("/var/prv/mysql.json","r")
	#jsf=json.loads(fsqlp.read())
	#mysql=MySQLdb.connect(host=jsf['host'], user=jsf['user'],passwd=jsf['passwd'],db="")
	serv = RunCGIServer()
	serv.start()

def dmInit():
	reload(sys)
	sys.setdefaultencoding('utf-8')
	try:
		os.chdir(basedir)
		mainfunc()
	except Exception,e:
		time.sleep(5)
		s = traceback.format_exc()
		sys.stderr.write("\n"+now()+"Application was shutdown by a fatal error.\n%s\n"%s)
		sys.stderr.flush()

##============Daemon System============
class MyDaemon(Daemon):
	def _run(self):
		if ProcessMonitorOn:
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
		print "Invalid Value of '$webport'" % sys.argv[0]
		sys.exit(2)
	slport = os.environ.get('syslogport','9514')
	syslogport = str2int(slport)
	if syslogport == 0:
		print "Loading Env...                                        [\033[1;31;40mFAILURE\033[0m]"
		print "Invalid Value of '$syslogport'" % sys.argv[0]
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
		else:
			print "Unknown Command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "Command Format: %s start|stop|restart" % currname
		sys.exit(2)
