# -*- coding: UTF-8 -*-

import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLUGIN_ITEMS = {
    "nic": "src.plugins.nic.Nic",
    "disk": "src.plugins.disk.Disk",
    "memory": "src.plugins.memory.Memory",
    # "cpuinfo": "src.plugins.cpuinfo.Cpuinfo",
    "nvme_ssd": "src.plugins.nvme_ssd.Nvme_ssd",
}

API_TOKEN = "7d6766a6s5f76safas657889hj78kf90"
API = "http://10.0.4.186/api/server/"
TASK_API = "http://10.0.4.186/api/task/"
# STASK_API = "http://10.0.2.20/api/stask/"
# FILE_API = "http://10.0.2.20/api/file/"

TEST = False

MODE = "AGENT" # AGENT/SSH/SALT

NVME_TOOL_PATH = os.path.join(BASEDIR,'nvme_tool')
#
# SSH_USER = "root"
# SSH_PORT = 22
# SSH_PWD = "sdf"

CLIENT_VERSION = "v1.0.5"

LOG_FILE_PATH = os.path.join(BASEDIR,'log','cmdb.log')