# /usr/bin/env python
# -*- coding:utf-8 -*-
# Author  : wuyifei
# Data    : 10/15/18 4:55 PM
# FileName: base.py
import platform
from abc import ABCMeta,abstractmethod

class BasePlugin(object):
    __metaclass__ = ABCMeta
    '''
    插件类的基类:必须实现win和linux方法
    '''
    def get_os(self,cmd_func):
        # return cmd_func('查看系统的命令')
        return platform.system()

    def process(self,cmd_func,test):
        os = self.get_os(cmd_func)
        if os == 'Windows':
            return self.win(cmd_func,test)
        elif os == 'Linux':
            return self.linux(cmd_func,test)
    
    @abstractmethod
    def win(self,cmd_func,test):
        pass
        # raise NotImplementedError('win must be implemented ')
    
    @abstractmethod
    def linux(self,cmd_func,test):
        pass
        # raise NotImplementedError('linux must be implemented ')
    

if __name__ == "__main__" :
    class B(BasePlugin):
        pass

    b = B()
