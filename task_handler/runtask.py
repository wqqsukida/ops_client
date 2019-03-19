# /usr/bin/env python
# -*- coding:utf-8 -*-
# Author  : wuyifei
# Data    : 1/8/19 4:05 PM
# FileName: update.py
from src import client
from lib.config import settings
from lib.log import logger
from multiprocessing import Pool,Process
import json
import copy
import requests
import datetime
import os
import subprocess
import traceback
import hashlib

class RunTask(client.BaseClient):
    def __init__(self, stask_id, name, path, args_str, download_url):
        super(RunTask, self).__init__()
        self.stask_id = stask_id
        self.name = name
        self.path = path
        self.args_str = args_str
        self.download_url = download_url

    def task_process(self):
        tid = {'id': self.stask_id}
        try:
            self.get_script()
            res = subprocess.Popen(
                'sudo python {path} {args_str} 2>&1'.
                    format(
                    path=self.path,
                    args_str=self.args_str,
                ),
                shell=True,
                stdout=subprocess.PIPE
            )
        except Exception as e:
            msg = traceback.format_exc()
            logger.error(msg)

        from task_handler.progress import get_res
        try:
            #如果是windows系統則找不到host_task.results會報錯
            if not get_res().get('status') == '5':  #如果脚本没有生成host_task.results文件
                with open('/tmp/host_task.results', 'w') as f:
                    f.write('args                  : %s\n' % self.args_str)
                    f.write('elapsed               : %s\n' % '0')
                    f.write('msg                   : %s\n' % 'this script doesn`t generate a host_task.results file!')
                    f.write('name                  : %s\n' % self.name)
                    f.write('path                  : %s\n' % self.path)
                    f.write('status                : %d\n' % 3)
        except Exception as e:
            msg = traceback.format_exc()
            logger.error(msg)

        json.dump(tid, open(self.tid_path, 'w'))

    def get_script(self):

        file_obj = requests.get(self.download_url)
        # md5_str = self.download_url.split('fid=')[1]
        file_name = file_obj.headers['Content-Disposition'].split('filename=')[1]
        file_path = self.path.strip(file_name)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(self.path, "wb") as f:
            f.write(file_obj.content)
        f.close()
        # img_md5_str = self.match(img_path)
        # if img_md5_str != md5_str:
        #     self.get_img()
        #
        # return img_path