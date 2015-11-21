#coding=utf-8
import re
import urllib
import os

def getHtml(url):
	page=urllib.urlopen(url)
	html=page.read()
	return html

def getImg(html):
	reg=r'src=".+uploads.+[0-9]+x[0-9]+.[jpeg]+"'
	imgre=re.compile(reg)
	imglist=re.findall(imgre,html)
	return imglist

leng=20
for i in range(1,100):
	print "正在爬取第%i个网页" %i
	url="http://www.lifeofpix.com/page/"+str(i)
	print url
	html=getHtml(url)	
	imglist2=getImg(html)
	x=0
	for img in imglist2:		
		newurl=re.split('"',img)[1]
		basedir='outcome\\%s'%str(i)
		if not os.path.exists(basedir):
			os.makedirs(basedir)
		if newurl.find("jpg")==-1:			 
			name=basedir+'\\%s.jpeg' %str(x)
		else:
			name=basedir+'\\%s.jpg' %str(x)
		print name
		urllib.urlretrieve(newurl,name)
		x+=1