#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""调用IVOPS平台发送告警
 __author__ = "chenqh"
 __date__: "2017/2/4"
 __company__: inno-view
 __version__: "0.1"
 __see__: 如果python版本<2.7.9,使用requests模块请求https资源时会报SSL的错误,
	  请使用urllib版本的get_tocken函数.或者安装requests[security]解决.
"""

import sys
import json
import logging
import urllib2
import datetime
import requests
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

class Message(object):
    """ 类初始化函 """
    def __init__(self):
	self.header = {"Content-Type": "application/json"}
	self.sendurl = "http://api.wingconn.net/controller/v1/alarm"


    """ 发送消息 """
    def sendMsg(self, subject, content, user=None):
        # data = {
        #     "msgtype":"text",				                    #消息类型。
        #     "agentid":1,					                    #企业号中的应用id，
        #     "text":{"content":subject + "\n" + content},	    #消息内容，最长不超过2048个字节
        #     "safe":0						                    #是否是保密消息
        # }

        alertinfo = content.split(";")[0]
        alerthost = content.split(";")[1]
        alerthostip = content.split(";")[2]
        alertlevel = content.split(";")[3]
        alerttime = content.split(";")[4]
        data = {
            "touser":"",
            "data":{
                "first": {
                "value":subject,
			    "color":"#FF0000"
		        },
		        "keyword1":{
			    "value":alertinfo,
			    "color":"#173177"
		        },
		        "keyword2": {
			    "value":alerthost,
			    "color":"#173177"
		         },
		        "keyword3": {
			    "value":alerthostip,
			    "color":"#173177"
		        },
		        "keyword4": {
			    "value":alertlevel,
			    "color":"#173177"
		        },
		        "keyword5": {
			    "value":alerttime,
			    "color":"#173177"
		        },
		        "remark":{
			    "value":"请后台人员相互转告，谢谢！",
			    "color":"#0000CD"
		       }
            }
        }

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
    # wc = WeChat("wx86e9521bba68be11", "7BqH1lVv65-b8ZjtmNaEqgOQbdJozpcxD31WG1c9POGOufxHr_Vq_8w7O-v7JsGl")
    # print wc.sendMsg("hadeschan","这是一个测试")

    logfile = "/var/log/zabbix/ivops_" + str(datetime.date.today()) + ".log"
    # print logfile
    loger = Logerer("IVOPS", logfile)
    lg = loger.getLoger()

    msg = Message()
    if len(sys.argv) == 4:
        user = sys.argv[1]					    			      #zabbix传过来的第一个参数
    	subject = sys.argv[2]								      #zabbix传过来的第二个参数
    	content = sys.argv[3]								      #zabbix传过来的第三个参数
        lg.info("\n")
        lg.info("user:" + user)
        lg.info("subject:" + subject)
        lg.info("content:" + content)
    	lg.info(msg.sendMsg(subject, content, user))
    elif len(sys.argv) == 3:
    	subject = sys.argv[1]								      #zabbix传过来的第一个参数
    	content = sys.argv[2]								      #zabbix传过来的第二个参数
        lg.info("\n")
        lg.info("subject:" + subject)
        lg.info("content:" + content)
    	lg.info(msg.sendMsg(subject, content))
    else:
    	print "zbx_wechat.py [user] <subject> <content>"

if __name__ == "__main__":
    main()
