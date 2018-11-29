# -*- coding: UTF-8 -*-

import sys
import os
import time
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)
os.environ['AUTO_CLIENT_SETTINGS'] = "conf.settings"
from src import script


if __name__ == '__main__':
    while True:
        script.start()
        time.sleep(60)

