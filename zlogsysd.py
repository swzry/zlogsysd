# -*- coding: utf-8 -*-
from daemonlib import Daemon
from bottle import Bottle,route,run,get,post,request,HTTPError,static_file,request,error,template
import MySQLdb
import os.path
import os,sys,time,traceback,datetime,threading,json
now = lambda: time.strftime("[%Y-%b-%d %H:%M:%S]")
sqlf = lambda sql: MySQLdb.escape_string(sql)
maxdate=datetime.datetime.fromtimestamp(2140000000)
##============Init============
def mainfunc():
    global CGI
    CGI=Bottle()
    RouteTable(CGI)
    fsqlp=open("/var/prv/mysql.json","r")
    jsf=json.loads(fsqlp.read())
    #mysql=MySQLdb.connect(host=jsf['host'], user=jsf['user'],passwd=jsf['passwd'],db="")
    serv=RunCGIServer()
    serv.start()

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

##============Start Server Threading============
class RunCGIServer(threading.Thread):
    def run(self):
        CGI.run(host='0.0.0.0',port=9564,server='cherrypy')

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

##============Daemon System============
class MyDaemon(Daemon):
    def _run(self):
        #while True:
            reload(sys)
            sys.setdefaultencoding('utf-8')
            try:
                os.chdir(currdir)
                mainfunc()
            except Exception,e:
                time.sleep(1)
                s=traceback.format_exc()
                sys.stderr.write("\n"+now()+"Application was shutdown by a fatal error.\n%s\n"%s)
                sys.stderr.flush()

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    global currdir,currname
    currdir='/home/wwwcgi/zlogsysd/'
    currname='zlogsysd'
    daemon = MyDaemon('/dev/shm/zlogsysd.pid',currdir+currname+'.in',currdir+currname+'.out',currdir+currname+'.err')
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
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
