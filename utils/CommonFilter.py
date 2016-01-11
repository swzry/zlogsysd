from bottle import template

class CommonFilter():
	def __init__(self,ModelClass):
		self.modelclass = ModelClass
		self.filterlist = {}
	def AddFilter(self,name,fieldname,mode,**kwargs):
		self.filterlist[name] = (fieldname,mode,kwargs)
	def RenderHTML(self):
		return template('CommonFilter.html',{"fl":self.filterlist})
