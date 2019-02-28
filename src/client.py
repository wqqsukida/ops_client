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
# import copy_reg
import types
import hashlib
import time
import datetime
import uuid
import subprocess
import copy
import importlib
import traceback

# def _pickle_method(m):
#     if m.im_self is None:
#         return getattr,(m.im_class,m.im_func.func_name)
#     else:
#         return getattr,(m.im_self,m.im_func.func_name)
#
# copy_reg.pickle(types.MethodType,_pickle_method)



class BaseClient(object):
    def __init__(self):
        self.api = settings.API
        self.task_api = settings.TASK_API
        self.utask_api = settings.UTASK_API
        self.api_token = settings.API_TOKEN
        self.utask_res_path = os.path.join(settings.BASEDIR,'task_handler/res/res.json')
        self.tid_path = os.path.join(settings.BASEDIR,'task_handler/res/tid.json')
        # 获取cert_id
        cert_path = os.path.join(settings.BASEDIR,'conf','cert.txt')
        f = open(cert_path,mode='r')
        cert_id = f.read()
        f.close()
        if not cert_id:
            """第一次运行,生成唯一标示"""
            cert_id = str(uuid.uuid1())
            with open(cert_path,mode='w') as ff:
                ff.write(str(cert_id))
        self.cert_id = cert_id

    def post_info(self,data,api,res_str):
        try:
            response = requests.post(api,data=json.dumps(data),headers={'auth-token':self.auth_header_val})
            # 1. 字典序列化；2. 带请求头 content-type:   application/json
            if res_str == 'Client_Info':data = {'Client_Info':'....'}
            print_info = '[{date_time}]POST[{res_str}]:{data} to server'.format(
                date_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                res_str=res_str,
                data=data
            )
            print(print_info)
            logger.info(print_info)
            # 获得返回结果
            rep = json.loads(response.text)
            return rep
        except requests.ConnectionError as e :
            msg = traceback.format_exc()
            rep = { 'code': 3, 'msg':msg}
            logger.error(msg)
            print (rep)
            return rep
        except ValueError as e :
            msg = traceback.format_exc()
            rep = { 'code': 3, 'msg':msg}
            logger.error(msg)
            print (rep)
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
        '''
        执行上报client硬件信息
        :return:
        '''
        obj = PluginManager()
        server_dict = obj.exec_plugin()
        server_dict['cert_id'] = self.cert_id
        # 将client端信息发送给server
        rep = self.post_info(server_dict,self.api,'Client_Info')

    def check_utask(self):
        '''
        执行上报firmware升级结果
        :return:
        '''
        # 1.检查升级任务结果文件
        with open(self.utask_res_path, 'r') as f:
            res_json = json.load(f)
        utask_res = {"cert_id": self.cert_id, "update_res": {}}
        '''1:新任务 2:执行完成 3:执行失败 4:执行暂停 5:执行中'''
        if res_json.get("status_code") == 2 or res_json.get("status_code") == 3:
            utask_res["update_res"] = res_json
            json.dump({}, open(self.utask_res_path, 'w'))
        # 2.发送升级结果给server
        rep = self.post_info(utask_res,self.utask_api,'Update_Res')
        # 3.查询server端返回结果是否有升级任务要执行
        update_task = rep.get('utask')
        # 4.开启进程执行升级任务
        if update_task:
            from task_handler.update import RunUpdate
            ut_obj = RunUpdate(
                utask_id=update_task['utask_id'],
                node=update_task['node'],
                img_type=update_task['img_type'],
                download_url=update_task['download_url'],
                args_str=update_task['args_str']
            )
            p = Process(target=ut_obj.utask_process)
            p.start()

    def check_task(self):
        '''
        执行上报client任务状态
        :return:
        '''
        # 1.执行返回任务状态脚本
        from task_handler.progress import get_res
        task_res = {'cert_id':self.cert_id,'stask_res':{}}
        try:
            # 查看当前任务运行状态0:IDLE,3:ERROR,5:RUNNING
            if get_res().get('status') == 0 or get_res().get('status') == 3:
                with open(self.tid_path, 'r') as f:
                    tid = json.load(f).get('id')
                if tid:   #如果存在正在执行的任务,则
                    task_res['stask_id'] = tid
                    json.dump({}, open(self.tid_path, 'w'))
            task_res['stask_res'] = get_res()
        except Exception as e:
            task_res['stask_res']['msg'] = 'Run progress.py error!'
            task_res['stask_res']['status'] = 3
            with open(self.tid_path, 'r') as f:
                tid = json.load(f).get('id')
            if tid:  # 如果存在正在执行的任务
                task_res['stask_id'] = tid
                json.dump({}, open(self.tid_path, 'w'))
        # 2.发送任务状态到server
        rep = self.post_info(task_res,self.task_api,"Task_Res")
        # 3.查询server端返回结果是否有任务要执行
        server_task = rep.get('stask')
        # 4.开启进程执行升级任务
        if server_task:
            from task_handler.runtask import RunTask
            t_obj = RunTask(

                stask_id=server_task['stask_id'],
                name=server_task['name'],
                path=server_task['path'],
                args_str=server_task['args_str']
            )
            p = Process(target=t_obj.task_process)
            p.start()

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
