# -*- coding: UTF-8 -*-

import datetime
import requests
from src.plugins import PluginManager
from lib.config import settings
# from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process,Pool
from lib.log import logger
import json
import os
import copy_reg
import types
import hashlib
import time
import datetime
import uuid
import subprocess
import copy
import importlib
import traceback

def _pickle_method(m):
    if m.im_self is None:
        return getattr,(m.im_class,m.im_func.func_name)
    else:
        return getattr,(m.im_self,m.im_func.func_name)
    
copy_reg.pickle(types.MethodType,_pickle_method)



class BaseClient(object):
    def __init__(self):
        self.api = settings.API
        self.task_api = settings.TASK_API
        self.api_token = settings.API_TOKEN
        self.task_res_path = os.path.join(settings.BASEDIR,'task_handler/res/res.json')
        # 获取主机名
        cert_path = os.path.join(settings.BASEDIR, 'conf', 'cert.txt')
        f = open(cert_path, mode='r')
        hostname = f.read()
        f.close()
        self.hostname = hostname

    def post_server_info(self,server_dict):
        # requests.post(self.api,data=server_dict) # 1. k=v&k=v,   2.  content-type:   application/x-www-form-urlencoded
        try:
            response = requests.post(self.api,json=server_dict,headers={'auth-token':self.auth_header_val})
            # 1. 字典序列化；2. 带请求头 content-type:   application/json
            rep = json.loads(response.text)
            return rep
        except requests.ConnectionError,e :
            msg = traceback.format_exc()
            rep = { 'code': 3, 'msg':msg}
            logger.error(msg)
            print rep
            return rep
        except ValueError,e :
            msg = traceback.format_exc()
            rep = { 'code': 3, 'msg':msg}
            logger.error(msg)
            print rep
            return rep

    @property
    def auth_header_val(self):
        ctime = str(time.time())
        new_key = "%s|%s" % (self.api_token, ctime,)  # asdfuasodijfoausfnasdf|时间戳
        hs = hashlib.md5()
        hs.update(new_key.encode('utf-8'))
        md5_str = hs.hexdigest()

        # 6f800b6a11d3f9c08c77ef8f77b2d460，  # asdfuasodijfoausfnasdf|时间戳
        auth_header_val = "%s|%s" % (md5_str, ctime,)  # 6f800b6a11d3f9c08c77ef8f77b2d460|时间戳

        return auth_header_val

    def exe(self):
        raise NotImplementedError('必须实现exec方法')

class AgentClient(BaseClient):

    def exe(self):
        obj = PluginManager()
        server_dict = obj.exec_plugin()
        new_hostname = server_dict['basic']['data']['hostname']
        cert_path = os.path.join(settings.BASEDIR,'conf','cert.txt')

        f = open(cert_path,mode='r')
        cert_id = f.read()
        f.close()

        if not cert_id:
            """第一次运行,生成唯一标示"""
            cert_id = str(uuid.uuid1())
            with open(cert_path,mode='w') as ff:
                ff.write(str(cert_id))
        server_dict['cert'] = cert_id
        print_info = '[%s]POST %s to server'%(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'[ client info ]')
        print(print_info)
        logger.info(print_info)
        # 将client端信息发送给server
        rep = self.post_server_info(server_dict)

    def check_task(self):
        pass


class SaltSshClient(BaseClient):
    pass
    # def task(self,host):
    #     obj = PluginManager(host)
    #     server_dict = obj.exec_plugin()
    #     self.post_server_info(server_dict)
    # 
    # def get_host_list(self):
    #     response = requests.get(self.api)
    #     # print(response.text) # [{"hostname": "c1.com"}]
    #     return json.loads(response.text)
    # 
    # def exec(self):
    #     pool = ThreadPoolExecutor(10)
    # 
    #     host_list = self.get_host_list()
    #     for host in host_list:
    #         pool.submit(self.task,host['hostname'])
