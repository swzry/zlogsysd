from urllib import urlencode

class HTTPQueryArgs():
	def __init__(self,request):
		self.request = request
		self.args = dict(request.query)
	def addQuery(self,key,value):
		self.args[key] = value
	def render(self):
		return urlencode(self.args)
	def render_with_tempargs(self,tempagrs):
		tpdict = self.args
		tpdict.update(tempagrs)
		return urlencode(tempagrs)