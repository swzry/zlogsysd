# -*- coding: UTF-8 -*-
from daemonlib import Daemon
from bottle import Bottle,route,run,get,post,response,HTTPError,static_file,request,error,template,redirect,HTTPResponse
import os,sys,time,traceback,datetime,threading,json,logging,rsa,hmac,hashlib,uuid
from utils.CommonFilter import CommonFilter
from utils.HTTPQueryArgs import HTTPQueryArgs
from utils.CommonUtils import PageCounter,MakeSummary,IDNameCheck
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
RSAKEY = {}
##============================
def RouteTable(app):
	cgiapp=CGI_APP()
	errpages=ERR_PAGES()
##============URL Route List============
	routeDict = {
		'/static/<filename:path>':cgiapp.static,
		'/': cgiapp.index,
		'/login/': cgiapp.login,
		'/logout/': cgiapp.logout,
		'/about/': cgiapp.about,
		'/app/list/':cgiapp.AppList,
		'/app/new/':cgiapp.NewAppForm,
		'/app/del/':cgiapp.DelApp,
		'/src/list/':cgiapp.SrcList,
		'/src/del/':cgiapp.DelSrc,
		'/log/list/':cgiapp.LogList,
		'/log/view/<logid>/':cgiapp.LogView,
	}
	getDict = {
	}
	postDict = {
		'/login/': cgiapp.login_backend,
		'/app/new/':cgiapp.NewApp_backend,
		'/src/new/':cgiapp.NewSrc_backend,
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

class AuthObj(object):
	username = None
	uhmac = None
	msg = []

class AuthStatus():
	class NotLoggedIn(Exception):
		pass

def CheckLogin(func):
	def wrapper(*args,**kwargs):
		try:
			try:
				uhmac = request.cookies.get('uhmac')
				token = request.cookies.get('token')
				uname = request.cookies.get('uname')
				hm = hmac.new(str(RSAKEY['passwd_store']),"UNHMAC_"+uname, hashlib.sha1)
				uhmac2 = hm.digest().encode('base64').strip()
				if not uhmac == uhmac2:
					raise AuthStatus.NotLoggedIn
				kn = redis_conf['prefix']+'#uSession'
				kn2 = redis_conf['prefix']+"#uMsg:"+uhmac
				rtk = redis.hget(kn,uhmac)
				if rtk == None or rtk == "":
					raise AuthStatus.NotLoggedIn
				if not rtk == token:
					raise AuthStatus.NotLoggedIn
			except:
				SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',"<DEBUG>[LoginError]\n%s"%traceback.format_exc())
				raise AuthStatus.NotLoggedIn
			msgl = []
			try:
				while 1:
					msg = redis.lpop(kn2)
					if msg:
						if msg[0] == "s":
							mtype = "success"
							content = msg[1:]
						elif msg[0] == "i":
							mtype = "info"
							content = msg[1:]
						elif msg[0] == "w":
							mtype = "warning"
							content = msg[1:]
						elif msg[0] == "d":
							mtype = "danger"
							content = msg[1:]
						else:
							mtype = "info"
							content = msg
						msgl.append((mtype,content))
					else:
						break
			except:
				SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',"<DEBUG>[MsgSysError]\n%s"%traceback.format_exc())
			authobj = AuthObj()
			authobj.username = uname
			authobj.uhmac = uhmac
			authobj.msg = msgl
			kwargs ["auth"] = authobj
			try:
				result = func(*args,**kwargs)
				return result
			except HTTPResponse,e:
				raise e
			except:
				SelfFailureLoggerModel.addlog(logging.ERROR,'text/plain',traceback.format_exc())
				return error(500)
		except AuthStatus.NotLoggedIn:
			SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',"<DEBUG>[LoginFailure]%s"%traceback.format_exc())
			return redirect("/login/",code=302)
	return wrapper

def ThrowMsg(authobj,mtype,content):
	if mtype == "s":
		mpf = "s"
	elif mtype == "i":
		mpf = "i"
	elif mtype == "w":
		mpf = "w"
	elif mtype == "d":
		mpf = "d"
	else:
		mpf = "i"
	ku = authobj.uhmac
	kn = redis_conf['prefix']+"#uMsg:"+ku
	redis.lpush(kn,mpf+content)

class CGI_APP:
##============CGI APP Class============
	def static(self,filename):
		return static_file(filename, root='static')
	def login(self):
		ref = request.headers.get("REFERER")
		if ref == None or ref == "":
			ref = "/"
		errcode = request.query.get("errcode")
		kwvars = {
			"PageTitle":"管理登陆",
			"ref":ref,
			"keyn":hex(RSAKEY['login_pub']['n'])[2:][:-1],
			"keye":hex(RSAKEY['login_pub']['e'])[2:],
			"errcode":errcode,
		}
		return template("login.html",**kwvars)

	@CheckLogin
	def logout(self,auth=None):
		kn = redis_conf['prefix']+'#uSession'
		redis.hdel(kn,auth.uhmac)
		return redirect("/login/",code=302)

	def login_backend(self):
		user_c = request.forms.get("username")
		pswd_c = request.forms.get("password")
		try:
			username = rsa.decrypt(user_c.decode('base64'),RSAKEY['login_prv'])
		except:
			return redirect("/login/?errcode=400",302)
		if username in RSAKEY['ulist'].keys():
			try:
				password = rsa.decrypt(pswd_c.decode('base64'),RSAKEY['login_prv'])
			except:
				return redirect("/login/?errcode=400",302)
			hm = hmac.new(str(RSAKEY['passwd_store']),password, hashlib.sha1)
			sg = hm.digest()
			pshs = sg.encode('base64').strip()
			upd = RSAKEY['ulist'].get(username)
			if pshs == upd:
				suuid = uuid.uuid4().bytes.encode('base64').strip()
				hm = hmac.new(str(RSAKEY['passwd_store']),"UNHMAC_"+username, hashlib.sha1)
				uname = hm.digest().encode('base64').strip()
				kn = redis_conf['prefix']+'#uSession'
				kn2 = redis_conf['prefix']+"#uMsg:"+uname
				redis.hset(kn,uname,suuid)
				redis.lpush(kn2,"s登陆成功")
				response.set_cookie("uname",username,path="/")
				response.set_cookie("uhmac",uname,path="/")
				response.set_cookie("token",suuid,path="/")
				return redirect("/",302)
			else:
				return redirect("/login/?errcode=530",302)
		else:
			return redirect("/login/?errcode=530",302)

	@CheckLogin
	def index(self,auth=None):
		kwvars = {
			"PageTitle":"日志系统管理",
			"auth":auth,
		}
		return template('home.html',**kwvars)

	@CheckLogin
	def AppList(self,auth=None):
		ao = LogApp.select()
		try:
			pgid = int(request.query.get('page','1'))
		except:
			pgid = 0
		pco = PageCounter(ao,20)
		pco.setCurrentPage(pgid)
		lpg = ao.order_by(LogApp.id).paginate(pgid,20)
		hqo = HTTPQueryArgs(request)
		SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',hqo.args)
		kwvars = {
			"pco": pco,
			"hqo": hqo,
			"lPage": lpg,
			"PageTitle":"应用管理",
			"auth":auth,
		}
		return template('app.list.html',**kwvars)

	@CheckLogin
	def NewAppForm(self,auth=None):
		kwvars = {
			"PageTitle":"新建应用",
			"auth":auth,
		}
		return template('form.newapp.html',**kwvars)

	@CheckLogin
	def NewApp_backend(self,auth=None):
		appname = request.forms.get("name")
		desc = request.forms.get("desp")
		if not IDNameCheck(appname):
			ThrowMsg(auth,"d","应用名称无效（只能包含大小写字母、数字和下划线_）")
			return redirect("/app/new/",code=302)
		co,ic = LogApp.get_or_create(name=appname,defaults={"desc":desc,"appkey":"","secret":""})
		if ic:
			ThrowMsg(auth,"s","应用创建成功")
		else:
			ThrowMsg(auth,"w","应用名称与现有应用重复，新应用未被创建")
		return redirect("/app/list/",code=302)

	@CheckLogin
	def DelApp(self,auth=None):
		appid = request.query.get("aid")
		vcode = request.query.get("hash")
		try:
			ao = LogApp.get(LogApp.id == appid)
		except LogApp.DoesNotExist:
			ThrowMsg(auth,"d","应用不存在")
			return redirect("/app/list/",code=302)
		if ao.name == "zlogsys":
			ThrowMsg(auth,"d","系统应用'zlogsys'不能删除")
			return redirect("/app/list/",code=302)
		#SelfLoggerModel.addlog(logging.DEBUG,"text/plain","HashInfo: queryHash={0},objectHash={1}".format(repr(vcode),repr(ao.gethash())))
		if not ao.gethash() == vcode:
			ThrowMsg(auth,"d","安全校验失败，服务器拒绝操作")
			return redirect("/app/list/",code=302)
		ao.delete_instance()
		ThrowMsg(auth,"s","删除成功")
		return redirect("/app/list/",code=302)


	@CheckLogin
	def SrcList(self,auth=None):
		so = LogSrc.select()
		fco = CommonFilter(LogSrc,logger=SelfFailureLoggerModel.addlog)
		fco.AddFilter("an","app.name","eq",title="应用名")
		fco.AddFilter("ai","app.id","eq",title="应用ID")
		fco.AddFilter("n","name","eq",title="日志源名")
		fco.AddFilter("id","id","eq",title="日志源ID")
		so = fco.Filter(request,so)
		try:
			pgid = int(request.query.get('page','1'))
		except:
			pgid = 0
		pco = PageCounter(so,20)
		pco.setCurrentPage(pgid)
		lpg = so.order_by(LogSrc.id).paginate(pgid,20)
		hqo = HTTPQueryArgs(request)
		SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',hqo.args)
		kwvars = {
			"fthtml":fco.RenderHTML(request),
			#"fthtml":"",
			"pco": pco,
			"hqo": hqo,
			"lPage": lpg,
			"PageTitle":"应用管理",
			"auth":auth,
		}
		return template('src.list.html',**kwvars)

	# @CheckLogin
	# def NewSrcForm(self,auth=None):
	# 	kwvars = {
	# 		"PageTitle":"新建日志源",
	# 		"auth":auth,
	# 	}
	# 	return template('form.newsrc.html',**kwvars)

	@CheckLogin
	def NewSrc_backend(self,auth=None):
		srcname = request.forms.get("name")
		appid = request.forms.get("aid")
		try:
			appobj = LogApp.get(LogApp.id == appid)
		except LogApp.DoesNotExist:
			ThrowMsg(auth,"d","应用不存在")
			return redirect("/app/list/",code=302)
		if appobj.name == "zlogsys":
			ThrowMsg(auth,"d","不能在系统应用'zlogsys'下创建新日志源")
			return redirect("/app/list/",code=302)
		if not IDNameCheck(srcname):
			ThrowMsg(auth,"d","日志源名称无效（只能包含大小写字母、数字和下划线_）")
			return redirect("/app/list/",code=302)
		co,ic = LogSrc.get_or_create(name=srcname,app=appobj)
		if ic:
			ThrowMsg(auth,"s","日志源创建成功")
			return redirect("/src/list/?ai="+appid,code=302)
		else:
			ThrowMsg(auth,"w","日志源名称与在同一个应用下的现有日志源重复，新日志源未被创建")
			return redirect("/app/list/",code=302)


	@CheckLogin
	def DelSrc(self,auth=None):
		srcid = request.query.get("sid")
		vcode = request.query.get("hash")
		try:
			so = LogSrc.get(LogSrc.id == srcid)
		except LogSrc.DoesNotExist:
			ThrowMsg(auth,"d","日志源不存在")
			return redirect("/src/list/",code=302)
		if so.app.name == "zlogsys":
			ThrowMsg(auth,"d","系统应用'zlogsys'下的日志源不能删除")
			return redirect("/src/list/",code=302)
		#SelfLoggerModel.addlog(logging.DEBUG,"text/plain","HashInfo: queryHash={0},objectHash={1}".format(repr(vcode),repr(ao.gethash())))
		if not so.gethash() == vcode:
			ThrowMsg(auth,"d","安全校验失败，服务器拒绝操作")
			return redirect("/src/list/",code=302)
		so.delete_instance()
		ThrowMsg(auth,"s","删除成功")
		return redirect("/src/list/",code=302)

	@CheckLogin
	def LogList(self,auth=None):
		lo = LogItem.select()
		fco = CommonFilter(LogItem,logger=SelfFailureLoggerModel.addlog)
		tpch = {
			"text/plain":"纯文本",
			"text/html":"HTML",
			"text/markdown":"Markdown",
		}
		lvch = {
			logging.CRITICAL:"CRITICAL",
			logging.ERROR:"ERROR",
			logging.WARNING:"WARNING",
			logging.INFO:"INFO",
			logging.DEBUG:"DEBUG",
		}
		fco.AddFilter("lv","level","gte",title="级别",choices=lvch)
		fco.AddFilter("st","time","gte",title="起始时间",datecontrol=True)
		fco.AddFilter("et","time","lte",title="结束时间",datecontrol=True)
		fco.AddFilter("tp","type","sc",title="数据类型",choices=tpch,editable=True)
		lo = fco.Filter(request,lo)
		try:
			pgid = int(request.query.get('page','1'))
		except:
			pgid = 0
		pco = PageCounter(lo,20)
		pco.setCurrentPage(pgid)
		lpg = lo.order_by(-LogItem.time).paginate(pgid,20)
		hqo = HTTPQueryArgs(request)
		#SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',hqo.render_with_tempargs({"page":2}))
		kwvars = {
			"fthtml":fco.RenderHTML(request),
			"pco": pco,
			"hqo": hqo,
			"lPage": lpg,
			"PageTitle":"日志列表",
			"auth":auth,
			"MakeSummary":MakeSummary,
		}
		return template('log.list.html',**kwvars)

	@CheckLogin
	def LogView(self,logid,auth=None):
		try:
			lo = LogItem.get(LogItem.id == str2int(logid))
		except LogItem.DoesNotExist:
			ThrowMsg(auth,"d","该日志条目不存在！")
			return redirect("/log/list/",code=302)
		kwvars = {
			"PageTitle":"查看日志条目内容",
			"auth":auth,
			"lo":lo,
		}
		return template('log.view.html',**kwvars)

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
	global SelfLoggerModel,SelfFailureLoggerModel
	#SelfLoggerModel.addlog(logging.DEBUG,'text/plain','DoRedisQuene')
	lst = redis.lrange(redis_conf['prefix']+'#sys_srclist',0,-1)
	#SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',"<DEBUG>%s"%repr(lst))
	for i in lst:
		try:
			srcobjn = i.split("@",2)
			if not len(srcobjn) == 2:
				raise Exception("Invalid SrcInfo in 'srclist'")
			lkeyname = "%s$[%s](%s)" % (redis_conf['prefix'],srcobjn[0],srcobjn[1])
			#SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',"<DEBUG>---:%s"%repr(lkeyname))
			iLoggerModel = LoggerModel(srcobjn[0],srcobjn[1])
			while 1:
				kd = redis.lpop(lkeyname)
				#SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain',"<DEBUG>---:%s"%repr(kd))
				if not kd:
					break
				try:
					dType    = redis.hget(kd,'type')
					dLevel   = str2int(redis.hget(kd,'level'))
					dContent = redis.hget(kd,'content')
					redis.delete(kd)
					iLoggerModel.addlog(dLevel,dType,dContent)
				except Exceptions,e:
					SelfFailureLoggerModel.addlog(logging.WARNING,'text/plain',"[%s]<FailedWriteDB>%s"%(i,repr(e)))
		except Exceptions,e:
			SelfFailureLoggerModel.addlog(logging.WARNING,'text/plain',"[%s]<FailedDumpRedis>%s"%(i,repr(e)))

def RefreshConfig():
	lsrckey = redis_conf['prefix']+'#sys_srclist'
	redis.delete(lsrckey)
	for i in LogSrc.select():
		redis.lpush(lsrckey,i.app.name+"@"+i.name)

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
			except Exception,e:
				s = traceback.format_exc()
				sys.stderr.write("\n"+now()+"Application was shutdown by a fatal error.\n%s\n"%s)
				sys.stderr.flush()
			finally:
				time.sleep(20)

##============Init============

def LoadRSAKeys():
	global RSAKEY
	with open('passwd/loginkey_pub.pem') as fpub:
		RSAKEY['login_pub'] = rsa.PublicKey.load_pkcs1(fpub.read(),'PEM')
	with open('passwd/loginkey_prv.pem') as fpub:
		RSAKEY['login_prv'] = rsa.PrivateKey.load_pkcs1(fpub.read(),'PEM')
	with open('passwd/passwd.json') as jsf:
		passwd = json.load(jsf)
		RSAKEY['passwd_store'] = passwd['password_store_key']
		RSAKEY['ulist'] = passwd['user_list']

def RebuildKeys():
	(pub,prv) = rsa.newkeys(2048)
	dfpub = pub.save_pkcs1(format="PEM")
	dfprv = prv.save_pkcs1(format="PEM")
	if os.path.exists('passwd/loginkey_pub.pem'):
		os.remove('passwd/loginkey_pub.pem')
	if os.path.exists('passwd/loginkey_prv.pem'):
		os.remove('passwd/loginkey_prv.pem')
	with open('passwd/loginkey_pub.pem','w') as fpub:
		fpub.write(dfpub)
	with open('passwd/loginkey_prv.pem','w') as fprv:
		fprv.write(dfprv)

def dmInit():
	global SelfLoggerModel,SelfFailureLoggerModel
	reload(sys)
	sys.setdefaultencoding('utf-8')
	try:
		os.chdir(basedir)
		SelfLoggerModel = LoggerModel("zlogsys","serverlog")
		SelfFailureLoggerModel = LoggerModel("zlogsys","failure")
		RefreshConfig()
		serv = RunCGIServer()
		worker = RunWorker()
		serv.start()
		worker.start()
		SelfFailureLoggerModel.addlog(logging.DEBUG,'text/plain','Zlogsys FailureLog Test')
		SelfLoggerModel.addlog(logging.INFO,'text/plain','Zlogsys Server Start')
		try:
			LoadRSAKeys()
			SelfLoggerModel.addlog(logging.INFO,'text/plain','RSA Key Loaded.')
		except Exception,e:
			SelfLoggerModel.addlog(logging.WARNING,'text/plain','Invalid RSA Key: %s'%repr(e))
			SelfLoggerModel.addlog(logging.INFO,'text/plain','Rebuilding Key...')
			RebuildKeys()
			SelfLoggerModel.addlog(logging.INFO,'text/plain','RSA Key Rebuild.')
			LoadRSAKeys()
			SelfLoggerModel.addlog(logging.INFO,'text/plain','RSA Key Loaded.')
	except Exception,e:
		time.sleep(5)
		s = traceback.format_exc()
		sys.stderr.write("\n"+now()+"Application was shutdown by a fatal error.\n%s\n"%s)
		sys.stderr.flush()

def syncdb():
	DB_Init()

def InstallTestData():
	testapp,created = LogApp.get_or_create(name="TestApp",defaults={"desc":"App For Test.","appkey":"","secret":""})
	LogSrc.get_or_create(name="TestSource",defaults={"app":testapp.id})
	RefreshConfig()

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
	elif len(sys.argv) == 3:
		if 'syncdb' == sys.argv[1]:
			if '--with-testdata' == sys.argv[2]:
				syncdb()
				print "Database Sync....                                      [\033[1;32;40mOK\033[0m]"
				InstallTestData()
				print "Install Test Data....                                  [\033[1;32;40mOK\033[0m]"
		sys.exit(0)
	else:
		print "Command Format: %s start|stop|restart" % currname
		sys.exit(2)
