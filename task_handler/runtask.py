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
    def __init__(self, stask_id, name, path, args_str):
        super(RunTask, self).__init__()
        self.stask_id = stask_id
        self.name = name
        self.path = path
        self.args_str = args_str

    def task_process(self):
        tid = {'id':self.stask_id}
        res = subprocess.Popen(
            'sudo {path} {args_str} 2>&1'.
                format(
                path=self.path,
                args_str=self.args_str,
            ),
            shell=True,
            stdout=subprocess.PIPE
        )


        json.dump(tid, open(self.tid_path, 'w'))
