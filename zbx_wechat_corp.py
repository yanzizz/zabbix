#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""调用微信企业号API发送报警信息
 __author__ = "chenqh"
 __date__: "2016/9/8"
 __company__: inno-view
 __version__: "0.1"
 __see__: 如果python版本<2.7.9,使用requests模块请求https资源时会报SSL的错误,
	  请使用urllib版本的get_tocken函数.或者安装requests[security]解决.
"""

import datetime
import json
import logging
import requests
import sys
import urllib2
from urllib2 import URLError

class Logerer(object):
    ''' 类初始化方法 '''
    def __init__(self, logname, logfile):
        self.logname = logname
        self.logfile = logfile

    def getLoger(self):
        self.logger = logging.getLogger(self.logname)
        self.logger.setLevel(logging.INFO)
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(self.logfile)
        fh.setLevel(logging.INFO)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # 定义handler的输出格式
        # fmt = "%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s"
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        #self.logger.addHandler(ch)
        return self.logger

class WeChat(object):
    """ 类初始化函 """
    def __init__(self, corpid, secret):
	self.header = {"Content-Type": "application/json"}
	self.tockenurl = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (corpid, secret)
	self.tocken = self.__get_tocken()
	self.sendurl = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % self.tocken


    """ 类内部函数,获取访问API的tocken (requests版本)"""
    def __get_tocken(self):
	req = requests.get(self.tockenurl)
	tocken = json.loads(req.text)
	if tocken.has_key("errcode"):
	    print "Error occurred:", tocken["errmsg"]
	else:
	    return tocken["access_token"]

    """ 类内部函数,获取访问API的tocken (urllib2版本)"""
    def __get_tocken_urllib(self):
	request = urllib2.Request(self.tockenurl)
	try:
	    result = urllib2.urlopen(request)
	except URLError as e:
	    print e.code
	else:
	    response = json.loads(result.read())
	    result.close()
	    # print "response:",response
	    return response['access_token']


    """ 发送消息 """
    def sendMsg(self, subject, content, user=None):
        data = {
            "msgtype":"text",				                    #消息类型。
            "agentid":1,					                    #企业号中的应用id，
            "text":{"content":subject + "\n" + content},	    #消息内容，最长不超过2048个字节
            "safe":0						                    #是否是保密消息
        }
        if user != None:
            data["touser"] = user			                   	#企业号中的用户帐号，在zabbix用户Media中配置。
        else:
            data["toparty"] = "1"                               #企业号中的部门id

        data_json = json.dumps(data, ensure_ascii=False)
        # print data_json
        res = requests.post(self.sendurl, data=data_json, headers=self.header)
        # print res.text
        result = json.loads(res.text)
        # print result
        if result['errcode'] == 0:
            return "sucessed:" + str(data_json)
        else:
            return "error:" + str(result)

def main():
    # wc = WeChat("wx86exxxxxxxxx1", "7BqHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    # print wc.sendMsg("hadeschan","这是一个测试")

    logfile = "/var/log/zabbix/wechat_" + str(datetime.date.today()) + ".log"
    # print logfile
    loger = Logerer("WeChat", logfile)
    lg = loger.getLoger()

    corpid = "wx86xxxxxxx"							                                  #CorpID是企业号的标识
    corpsecret = "7BqH1lVv6xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"	  #corpsecretSecret是管理组凭证密钥

    wc = WeChat(corpid, corpsecret)
    if len(sys.argv) == 4:
        user = sys.argv[1]					    			      #zabbix传过来的第一个参数
    	subject = sys.argv[2]								      #zabbix传过来的第二个参数
    	content = sys.argv[3]								      #zabbix传过来的第三个参数
        lg.info("\n")
        lg.info("user:" + user)
        lg.info("subject:" + subject)
        lg.info("content:" + content)
    	lg.info(wc.sendMsg(subject, content, user))
    elif len(sys.argv) == 3:
    	subject = sys.argv[1]								      #zabbix传过来的第一个参数
    	content = sys.argv[2]								      #zabbix传过来的第二个参数
        lg.info("\n")
        lg.info("subject:" + subject)
        lg.info("content:" + content)
    	lg.info(wc.sendMsg(subject, content))
    else:
    	print "zbx_wechat.py [user] <subject> <content>"

if __name__ == "__main__":
    main()
