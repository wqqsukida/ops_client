# -*- coding: UTF-8 -*-

import os,platform
from lib.config import settings

class Cpuinfo(object):
    def linux(self, cmd_func, test):
        if test:
            output = open(os.path.join(settings.BASEDIR, 'files/cpuinfo.out'), 'r').read()

        else:
            # output = cmd_func("sudo cat /proc/cpuinfo")
            cpu_physical_count = cmd_func("sudo cat /proc/cpuinfo | grep 'physical id' | sort | uniq | wc -l")
            cpu_count = cmd_func("sudo cat /proc/cpuinfo | grep 'processor' | wc -l")
            cpu_model = cmd_func("sudo cat /proc/cpuinfo | grep name | cut -f2 -d:| uniq -c")
        return self.parse(cpu_physical_count,cpu_count,cpu_model)
    
    def parse(self,cpu_physical_count,cpu_count,cpu_model):
        response = {
            'cpu_physical_count':cpu_physical_count,
            'cpu_count':cpu_count,
            'cpu_model':cpu_model
        }
        # response = {}
        # p = 0
        # for core in content.split("processor")[1:]:
        #     key_map = {}
        #     for row_line in core.strip().split('\n'):
        #         key,val = row_line.split(':')
        #         if not key :
        #             key_map['processor'] = val.strip()
        #         if key.startswith('model name'):
        #             key_map['model name'] = val.strip()
        #         if key.startswith('cpu cores'):
        #             key_map['cpu cores'] = val.strip()
        #     response['processor%s' % p] = key_map
        #     p+=1
        return response

    def win(selfcmd_func,test):
        pass