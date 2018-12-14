# /usr/bin/env python
# -*- coding:utf-8 -*-
# Author  : wuyifei
# Data    : 12/12/18 5:49 PM
# FileName: setup.py
import sys
import os

CLIENT_DIR = '/opt/dera_ops_client'


def setup():
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    # os.rename(base_dir,CLIENT_DIR)
    if os.getuid() == 0:
        pass
    else:
        print('\033[1;31;40m 请切换root用户执行!\033[0m')
        sys.exit(1)

    step1 = os.system('pip install requests')
    if step1 == 32512:
        print('\033[1;31;40m 找不到pip命令,请先安装pip!\033[0m')
        sys.exit(1)

    step2 = os.system("grep 'sh /opt/dera_ops_client/run_client.sh start' /etc/rc.d/rc.local")
    if step2 != 0:
        step3 = os.system("sed -i '$a\sh /opt/dera_ops_client/run_client.sh start' /etc/rc.d/rc.local & chmod +x /etc/rc.d/rc.local")
        if step3 != 0:
            print('\033[1;31;40m 设置开机启动失败,请手动将启动脚本添加到rc.local下!\033[0m')

    print('\033[1;32;40m 安装完成!\033[0m')

if __name__ == "__main__":
    setup()