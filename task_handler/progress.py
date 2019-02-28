# /usr/bin/env python
# -*- coding:utf-8 -*-
# Author  : wuyifei
# Data    : 12/3/18 9:43 AM
# FileName: progress.py
import re
res = {}
def get_res():

    with open('/tmp/host_task.results', 'r') as f:
        for line in f.readlines():
            m = re.search('(\w+)\s+:\s+(\S+.*)', line)
            if m:
                name = str(m.group(1))
                value = m.group(2)
                res[name] = value
    return res