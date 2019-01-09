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

class RunUpdate(client.BaseClient):
    def __init__(self, utask_id, sn, img_type, download_url, args_str):
        super(RunUpdate, self).__init__()
        self.utask_id = utask_id
        self.sn = sn
        self.img_type = img_type
        self.download_url = download_url
        self.args_str = args_str
        self.cmd_file = os.path.join(settings.NVME_TOOL_PATH,'nvme_update.sh')
        self.img_file = self.get_img()

    def utask_process(self):
        utask_res = {"utask_id": self.utask_id, "status_code": 5,
                     "run_time": "", "message": "",}
        start_time = datetime.datetime.now()
        try:
            res = subprocess.Popen(
                'sudo sh {update_cmd} -t {sn} -f {img_file}'.format(update_cmd=self.cmd_file,sn=self.sn, img_file=self.img_file),
                shell=True,
                stdout=subprocess.PIPE
            )
            res.wait()
            end_time = datetime.datetime.now()
            run_time = end_time - start_time
            utask_res["run_time"] = str(run_time)
            utask_res["status_code"] = 2
            utask_res["message"] = res.stdout.read().decode('utf-8')
        except Exception as e:
            end_time = datetime.datetime.now()
            run_time = end_time - start_time
            utask_res["run_time"] = str(run_time)
            utask_res["status_code"] = 3
            msg = traceback.format_exc()
            utask_res["message"] = msg
            logger.error(msg)
        json.dump(utask_res, open(self.task_res_path, 'w'))


    def get_img(self):
        try:
            file_obj = requests.get(self.download_url)
            md5_str = self.download_url.split('fid=')[1]
            file_name = file_obj.headers['Content-Disposition'].split('filename=')[1]
            file_path = os.path.join(settings.BASEDIR, 'image_file',self.img_type)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            img_path = os.path.join(file_path,file_name)
            with open(img_path, "wb") as f:
                f.write(file_obj.content)
            f.close()
            img_md5_str = self.match(img_path)
            if img_md5_str != md5_str:
                self.get_img()
        except Exception as e:
            msg = traceback.format_exc()
            logger.error(msg)
            img_path = ''

        return img_path

    def match(self,file_path, Bytes=1024):
        md5_1 = hashlib.md5()  # 创建一个md5算法对象
        with open(file_path, 'rb') as f:  # 打开一个文件，必须是'rb'模式打开
            while 1:
                data = f.read(Bytes)  # 由于是一个文件，每次只读取固定字节
                if data:  # 当读取内容不为空时对读取内容进行update
                    md5_1.update(data)
                else:  # 当整个文件读完之后停止update
                    break
        ret = md5_1.hexdigest()  # 获取这个文件的MD5值
        return ret

    def res_callback(self):
        pass