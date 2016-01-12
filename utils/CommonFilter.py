from bottle import template

def NoneFunction(*args,**kwargs):
	pass

class CommonFilter():
	def __init__(self,ModelClass,logger=NoneFunction):
		self.modelclass = ModelClass
		self.logger=logger
		self.filterlist = {}
	def AddFilter(self,name,fieldname,mode,**kwargs):
		self.filterlist[name] = (fieldname,mode,kwargs)
	def RenderHTML(self):
		return template('CommonFilter.html',{"fl":self.filterlist,"logger":self.logger})
