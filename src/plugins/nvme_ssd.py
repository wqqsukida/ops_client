# -*- coding: UTF-8 -*-
from .base import BasePlugin
import time
import os,re
import sys
from lib.config import settings

class Nvme_ssd(BasePlugin):
    def linux(self, cmd_func, test):
        if test:
            output = open(os.path.join(settings.BASEDIR, 'files/nvme_ssd.out'), 'r').read()

        else:
            nvme_path = os.path.join(settings.NVME_TOOL_PATH,'nvme')
            output = cmd_func("sudo {0} dera info".format(nvme_path))

        return self.parse(output,cmd_func)

    def parse(self,content,cmd_func):
        """
        解析shell命令返回结果
        :param content: shell 命令结果
        :return:解析后的结果
        """
        response = {}

        name_list = ['node','sn','model','namespace','capacity','format','fw_rev']
        for row_line in content.split("\n")[2:]:
            node_val = re.search('/\w+/\w+',row_line)
            # usage_val = re.search('(\d+\.\d+\s*[GT]B\s*/\s*\d+\.\d+\s*[GT]B)', row_line)
            # format_val = re.search('\d+\s*\w*B\s*\+\s*\d+\s*\w*B', row_line)
            val_list =re.split('\s{2,}',row_line)#[0:4]
            sn_val = val_list[1]
            # if usage_val and format_val:
            #     val_list.append(usage_val.group())
            #     val_list.append(format_val.group())
            #     val_list.append(row_line.split(" ")[-1])

            response[sn_val] = dict(zip(name_list,val_list))
            # get device smart_log ##################################
            smart_log = self.smart_log(cmd_func,node_val)
            response[sn_val]['smart_log'] = smart_log
            #########################################################
        return response

    def smart_log(self,cmd_func,device,task_id=None):
        '''
        cmd : nvme smart-log device
        :param device:
        :return:
        '''
        response = {}
        nvme_path = os.path.join(settings.NVME_TOOL_PATH, 'nvme')
        output = cmd_func("sudo {0} smart-log {1}".format(nvme_path,device))
        # if sys.version_info.major == 2 :
        # # py2
        #     import commands
        #     output = commands.getoutput("sudo {0} smart-log {1}".format(nvme_path,device))
        # # py3
        # else:
        #     import subprocess
        #     output = subprocess.getoutput("sudo {0} smart-log {1}".format(nvme_path,device))
        for row_line in output.split('\n')[1:]:
            k = row_line.split(":")[0].strip() # .replace(' ','_').lower()
            response[k] = row_line.split(":")[1].strip()

        if task_id:
            return {'task_id':task_id,'task_res':response}
        else:
            return response

    def error_log(self,device,task_id=None):
        response = {'res':'%s error_log'%device}

        time.sleep(20)

        if task_id:
            return {'task_id':task_id,'task_res':response}
        else:
            return response

    def format(self,device,task_id=None):
        response = {'res':'%s format success'%device}

        time.sleep(120)

        if task_id:
            return {'task_id':task_id,'task_res':response}
        else:
            return response

    def win(self,cmd_func,test):
        result = {}
        return result