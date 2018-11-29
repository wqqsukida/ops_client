# /usr/bin/env python
# -*- coding:utf-8 -*-
# Author  : wuyifei
# Data    : 10/23/18 11:39 AM
# FileName: log.py
import logging
import os
from lib.config import settings

class Logger(object):
    def __init__(self):
        self.log_file_path = settings.LOG_FILE_PATH
        if not self.log_file_path:
            # os.makedirs()
            f = open(self.log_file_path,'w')
            f.close()
        file_handler = logging.FileHandler(self.log_file_path, 'a', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s:  %(message)s"))

        self.logger = logging.Logger('cmdb', level=logging.INFO)
        self.logger.addHandler(file_handler)

    def info(self,msg):
        self.logger.info(msg)
    def error(self,msg):
        self.logger.error(msg)


logger = Logger()