# -*- coding: UTF-8 -*-
import sys
import importlib
import requests
import traceback
from lib.config import settings
from lib.log import logger
from lib.config import settings
# def func():
#     server_info = {}
#     for k,v in settings.PLUGIN_ITEMS.items():
#         # 找到v字符串：src.plugins.nic.Nic，src.plugins.disk.Disk
#         module_path,cls_name = v.rsplit('.',maxsplit=1)
#         module = importlib.import_module(module_path)
#         cls = getattr(module,cls_name)
#         obj = cls()
#         ret = obj.process()
#         server_info[k] = ret
#
#     requests.post(
#         url=settings.API,
#         data=server_info
#     )

class PluginManager(object):
    def __init__(self,hostname=None):
        self.hostname = hostname
        self.plugin_items = settings.PLUGIN_ITEMS
        self.mode = settings.MODE
        self.test = settings.TEST
        if self.mode == "SSH":
            self.ssh_user = settings.SSH_USER
            self.ssh_port = settings.SSH_PORT
            self.ssh_pwd = settings.SSH_PWD


    def exec_plugin(self):
        server_info = {}
        for k,v in self.plugin_items.items():
            # 找到v字符串：src.plugins.nic.Nic，
            # src.plugins.disk.Disk
            info = {'status':True,'data': {},'msg':None}
            try:
                module_path,cls_name = v.rsplit('.',1)
                module = importlib.import_module(module_path)
                cls = getattr(module,cls_name)

                if hasattr(cls,'initial'):
                    obj = cls.initial()
                else:
                    obj = cls()
                ret = obj.process(self.exec_cmd,self.test)
                info['data'] = ret
            except Exception as e:
                msg = traceback.format_exc()
                info['status'] = False
                info['msg'] = msg
                logger.error(msg)

            server_info[k] = info
        return server_info

    def exec_cmd(self,cmd):
        if self.mode == "AGENT":
            import subprocess,time
            timeout = settings.SHELL_TIME_OUT
            """执行命令cmd，返回命令输出的内容。
            如果超时将会抛出TimeoutError异常。
            cmd - 要执行的命令
            timeout - 最长等待时间，单位：秒
            """
            p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
            t_beginning = time.time()
            seconds_passed = 0
            while True:
                if p.poll() is not None:
                    break
                seconds_passed = time.time() - t_beginning
                if timeout and seconds_passed > timeout:
                    p.terminate()
                    raise TimeoutError(cmd, timeout)
                time.sleep(0.1)
            result =  p.stdout.read().decode('utf-8').strip()

            # # py3
            # if sys.version_info.major == 3 :
            #     import subprocess
            #     result = subprocess.getoutput(cmd)
            # else :
            # # py2
            #     import commands
            #     result = commands.getoutput(cmd)
        elif self.mode == "SSH":
            import paramiko
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.hostname, port=self.ssh_port, username=self.ssh_user, password=self.ssh_pwd)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read()
            ssh.close()
        elif self.mode == "SALT":
            import subprocess
            result = subprocess.getoutput('salt "%s" cmd.run "%s"' %(self.hostname,cmd))
        else:
            raise Exception("模式选择错误：AGENT,SSH,SALT")
        return result