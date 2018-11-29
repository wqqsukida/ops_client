# -*- coding: UTF-8 -*-
from .base import BasePlugin
import re
import os
from lib.config import settings

class Disk(BasePlugin):

    def linux(self,cmd_func,test):
        if test:
            output = open(os.path.join(settings.BASEDIR, 'files/disk.out'), 'r').read()
        else:
            output = cmd_func("sudo MegaCli  -PDList -aALL")

        return self.parse(output)

    def parse(self, content):
        """
        解析shell命令返回结果
        :param content: shell 命令结果
        :return:解析后的结果
        """
        response = {}
        result = []
        for row_line in content.split("\n\n\n\n"):
            result.append(row_line)
        for item in result:
            temp_dict = {}
            for row in item.split('\n'):
                if not row.strip():
                    continue
                if len(row.split(':')) != 2:
                    continue
                key, value = row.split(':')
                name = self.mega_patter_match(key)
                if name:
                    if key == 'Raw Size':
                        raw_size = re.search('(\d+\.\d+)', value.strip())
                        if raw_size:

                            temp_dict[name] = float(raw_size.group())
                        else:
                            raw_size = '0'
                    else:
                        temp_dict[name] = value.strip()
            if temp_dict:
                response[temp_dict['slot']] = temp_dict
        return response

    @staticmethod
    def mega_patter_match(needle):
        grep_pattern = {'Slot': 'slot', 'Raw Size': 'capacity', 'Inquiry': 'model', 'PD Type': 'pd_type'}
        for key, value in grep_pattern.items():
            if needle.startswith(key):
                return value
        return False
    
    def win(self,cmd_func,test):
        result = {}
        import wmi
        c = wmi.WMI()


        for disk in c.Win32_DiskDrive():
            disk_info = {}
            disk_info['slot'] = '%s'%disk.SCSIBus
            disk_info['capacity'] = float('%.2f'%(float(disk.Size)/1024/1024/1024))
            disk_info['model'] = disk.Model
            disk_info['pd_type'] = disk.InterfaceType
            result[disk.SCSIBus] = disk_info
            # space = 100.0 * long(drive.FreeSpace) / long(drive.Size)
            # print "%s has %0.2f%% free" % (drive.Name, space)

        return result
'''
{'_associated_classes': None,
 'methods': {u'Reset': None, u'SetPowerState': None},
 'property_map': {},
 'properties': {
                   u'Index': None,
                   u'TracksPerCylinder': None,
                   u'PowerManagementSupported': None,
                   u'MaxMediaSize': None,
                   u'NumberOfMediaSupported': None,
                   u'Capabilities': None,
                   u'SCSIPort': None,
                   u'MinBlockSize': None,
                   u'SystemName': None,
                   u'PowerManagementCapabilities': None,
                   u'Status': None,
                   u'PNPDeviceID': None,
                   u'Description': None,
                   u'TotalCylinders': None,
                   u'BytesPerSector': None,
                   u'ConfigManagerUserConfig': None,
                   u'ErrorCleared': None,
                   u'InterfaceType': None,
                   u'CompressionMethod': None,
                   u'SCSITargetId': None,
                   u'Manufacturer': None,
                   u'SerialNumber': None,
                   u'Name': None,
                   u'InstallDate': None,
                   u'MediaType': '<wmi_property: MediaType>',
                   u'DefaultBlockSize': None,
                   u'Signature': None,
                   u'Size': '<wmi_property: Size>',
                   u'FirmwareRevision': None,
                   u'CapabilityDescriptions': None,
                   u'ConfigManagerErrorCode': None,
                   u'ErrorMethodology': None,
                   u'MediaLoaded': None,
                   u'SectorsPerTrack': None,
                   u'Model': None,
                   u'TotalHeads': None,
                   u'SCSILogicalUnit': None,
                   u'SCSIBus': None,
                   u'Caption': '<wmi_property: Caption>',
                   u'ErrorDescription': None,
                   u'NeedsCleaning': None,
                 u'StatusInfo': None,
                 u'TotalTracks': None,
                 u'MaxBlockSize': None,
                 u'TotalSectors': None,
                 u'LastErrorCode': None,
                 u'CreationClassName': None,
                 u'Partitions': None,
                 u'Availability': None,
                 u'SystemCreationClassName': None,
                 u'DeviceID': None
 }}
'''
