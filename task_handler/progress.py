# /usr/bin/env python
# -*- coding:utf-8 -*-
# Author  : wuyifei
# Data    : 12/3/18 9:43 AM
# FileName: progress.py
import time
'''
res = {

    "name": "test.py",

    "path": "/tmp/test.py",

    "args": "-t 10 -d 4",

    "status": 0,

    "msg": "some desc",

    "elapsed": 40

}
'''

def get_res():
    f = open('/home/wuyifei/ops_pro/ops_client/task_handler/res','r')
    status = f.read()
    f.close()
    res = {
        "name": "test.py",
        "path": "/tmp/test.py",
        "args": "-t 10 -d 4",
        "status": status,
        "msg": "some desc",
        "elapsed": 40
               }

    return res