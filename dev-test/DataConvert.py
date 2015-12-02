# -*- coding: UTF-8 -*-
import decimal,math,time,datetime,random
from django.utils.html import strip_tags as html_strip_tags

def str2int(strs):
	strr=filter(lambda x:(x.isdigit or x=='-'),str(strs))
	if strr==None:
		return 0
	elif strr=='':
		return 0
	else:
		return int(strr)

def str2long(strs):
	strr=filter(lambda x:(x.isdigit or x=='-'),str(strs))
	if strr==None:
		return 0
	elif strr=='':
		return 0
	else:
		return long(strr)

def parseDecimal(strs,totalLen,apart):
	apt=strs.split(".",1)
	if len(apt) == 1:
		return decimal.Decimal(str(str2int(strs)))
	else:
		ipart=str(str2int(apt[0]))
		fpart=str(str2int(apt[1].replace('.','')))
	if(len(fpart)>apart):
		fptx=fpart[:apart]
		fpi=int(fptx)
		if(int(fpart[apart])>4):
			fpi=fpi+1
	else:
		fpi=int(fpart)
	if(len(ipart)>totalLen-apart):
		iptx='9'*(totalLen-apart)
		ipi=int(iptx)
	else:
		ipi=int(ipart)
	return decimal.Decimal(str(ipi)+'.'+str(fpi))

def CheckPOST(needlist,postkeys):
	for i in needlist:
		if i not in postkeys:
			return i
	return ""

def MakeSummary(text,length,escape=True):
	# if len(text.decode('utf8','ignore'))>length:
	# 	text=text.decode('utf8','ignore')[:length].encode("utf8")+u"..."
	# return text
	if len(text)>length:
		text=text[:length]+u"..."
	if escape:
		text = html_strip_tags(text)
	return text


def convertBytes(bytes,lst=['字节', 'KB', 'MB', 'GB', 'TB', 'PB']):
	i = int(math.floor(
			 math.log(bytes, 1024)
			))

	if i >= len(lst):
		i = len(lst) - 1
	return ('%.2f' + " " + lst[i]) % (bytes/math.pow(1024, i))

def Str2Date(strdate):
	t = time.strptime(strdate,"%Y-%m-%d")
	return datetime.date(t.tm_year,t.tm_mon,t.tm_mday)

def Str2DateTime(StrDateTime):
	t = time.strptime(StrDateTime,"%Y-%m-%d %H:%M:%S")
	return t

def BigIntUniqueID():
	ts = long(time.time()*100000000)
	hs = hash(str(time.time())+str(random.random())) & 0x00ffffff
	return ts+hs