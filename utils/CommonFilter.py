from bottle import template
import copy

def NoneFunction(*args,**kwargs):
	pass

class CommonFilter():
	def __init__(self,ModelClass,logger=NoneFunction):
		self.modelclass = ModelClass
		self.logger=logger
		self.filterlist = []
		self.filterdict = {}
	def AddFilter(self,name,fieldname,mode,**kwargs):
		self.filterdict[name] = (fieldname,mode,kwargs)
		self.filterlist.append((name,(fieldname,mode,kwargs)))
	def RenderHTML(self,request):
		ql = dict(request.query)
		fl = copy.deepcopy(self.filterlist)
		for i in fl:
			if i[0] in ql.keys():
				i[1][2]['default'] = ql[i[0]]
		kwargs = {"fl":fl,"logger":self.logger}
		return template('CommonFilter.html',kwargs)
	def Filter(self,request,dbo):
		ql = dict(request.query)
		dbobj = dbo
		for k,v in ql.items():
			if k in self.filterdict.keys():
				d = self.filterdict[k]
				if d[1] == "eq":
					dbobj = dbobj.where(getattr(self.modelclass,d[0])==v)
				if d[1] == "lt":
					dbobj = dbobj.where(getattr(self.modelclass,d[0])<v)
				if d[1] == "gt":
					dbobj = dbobj.where(getattr(self.modelclass,d[0])>v)
				if d[1] == "lte":
					dbobj = dbobj.where(getattr(self.modelclass,d[0])<=v)
				if d[1] == "gte":
					dbobj = dbobj.where(getattr(self.modelclass,d[0])>=v)
				if d[1] == "ct":
					dbobj = dbobj.where(getattr(self.modelclass,d[0]).contains(v))
				if d[1] == "sw":
					dbobj = dbobj.where(getattr(self.modelclass,d[0]).startwith(v))
				if d[1] == "ew":
					dbobj = dbobj.where(getattr(self.modelclass,d[0]).endwith(v))
				if d[1] == "sc":
					dbobj = dbobj.where(getattr(self.modelclass,d[0])==v)
				if d[1] == "mc":
					vlst = v.split(',')
					dbobj = dbobj.where(getattr(self.modelclass,d[0])<<vlst)
		return dbobj