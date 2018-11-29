# -*- coding: UTF-8 -*-
from .base import BasePlugin
import re
import os
from lib.config import settings
from lib import convert

class Memory(BasePlugin):
    def linux(self, cmd_func, test):
        if test:
            output = open(os.path.join(settings.BASEDIR, 'files/memory.out'), 'r').read()

        else:
            output = cmd_func("sudo dmidecode  -q -t 17 2>/dev/null")
        return self.parse(output)

    def parse(self, content):
        """
        解析shell命令返回结果
        :param content: shell 命令结果
        :return:解析后的结果
        """
        ram_dict = {}
        key_map = {
            'Size': 'capacity',
            'Locator': 'slot',
            'Type': 'model',
            'Speed': 'speed',
            'Manufacturer': 'manufacturer',
            'Serial Number': 'sn',

        }
        devices = content.split('Memory Device')
        for item in devices:
            item = item.strip()
            if not item:
                continue
            if item.startswith('#'):
                continue
            segment = {}
            lines = item.split('\n\t')
            for line in lines:
                if not line.strip():
                    continue
                if len(line.split(':')):
                    key, value = line.split(':')
                else:
                    key = line.split(':')[0]
                    value = ""
                if key in key_map:
                    if key == 'Size':
                        segment[key_map['Size']] = convert.convert_mb_to_gb(value, 0)
                    else:
                        segment[key_map[key.strip()]] = value.strip()

            ram_dict[segment['slot']] = segment

        return ram_dict
    
    def win(self,cmd_func,test):
        import wmi
        c = wmi.WMI()
        result = {}

        for memory in c.Win32_PhysicalMemory():
            memory_info = {}
            memory_info['capacity'] = float('%.2f'%(float(memory.Capacity)/1024/1024/1024))
            memory_info['slot'] = memory.BankLabel
            memory_info['model'] = '%s'%memory.MemoryType
            memory_info['speed'] = '%s'%memory.Speed
            memory_info['manufacturer'] = memory.Manufacturer
            memory_info['sn'] = memory.SerialNumber
            result[memory.BankLabel] = memory_info
        return result