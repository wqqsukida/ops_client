# -*- coding: UTF-8 -*-
from .base import BasePlugin
import os
import re
from lib.config import settings

class Nic(BasePlugin):
    def linux(self, cmd_func, test):
        if test:
            output = open(os.path.join(settings.BASEDIR, 'files/nic.out'), 'r').read()
            interfaces_info = self._interfaces_ip(output)
        else:
            interfaces_info = self.linux_interfaces(cmd_func)

        self.standard(interfaces_info)

        return interfaces_info

    def linux_interfaces(self, command_func):
        '''
        Obtain interface information for *NIX/BSD variants
        '''
        ifaces = dict()
        ip_path = 'ip'
        if ip_path:
            cmd1 = command_func('sudo {0} link show'.format(ip_path))
            cmd2 = command_func('sudo {0} addr show'.format(ip_path))
            ifaces = self._interfaces_ip(cmd1 + '\n' + cmd2)
        return ifaces

    def which(self, exe):
        def _is_executable_file_or_link(exe):
            # check for os.X_OK doesn't suffice because directory may executable
            return (os.access(exe, os.X_OK) and
                    (os.path.isfile(exe) or os.path.islink(exe)))

        if exe:
            if _is_executable_file_or_link(exe):
                # executable in cwd or fullpath
                return exe

            # default path based on busybox's default
            default_path = '/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin'
            search_path = os.environ.get('PATH', default_path)
            path_ext = os.environ.get('PATHEXT', '.EXE')
            ext_list = path_ext.split(';')

            search_path = search_path.split(os.pathsep)
            if True:
                # Add any dirs in the default_path which are not in search_path. If
                # there was no PATH variable found in os.environ, then this will be
                # a no-op. This ensures that all dirs in the default_path are
                # searched, which lets salt.utils.which() work well when invoked by
                # salt-call running from cron (which, depending on platform, may
                # have a severely limited PATH).
                search_path.extend(
                    [
                        x for x in default_path.split(os.pathsep)
                        if x not in search_path
                    ]
                )
            for path in search_path:
                full_path = os.path.join(path, exe)
                if _is_executable_file_or_link(full_path):
                    return full_path

        return None

    def _number_of_set_bits_to_ipv4_netmask(self, set_bits):  # pylint: disable=C0103
        '''
        Returns an IPv4 netmask from the integer representation of that mask.

        Ex. 0xffffff00 -> '255.255.255.0'
        '''
        return self.cidr_to_ipv4_netmask(self._number_of_set_bits(set_bits))

    def cidr_to_ipv4_netmask(self, cidr_bits):
        '''
        Returns an IPv4 netmask
        '''
        try:
            cidr_bits = int(cidr_bits)
            if not 1 <= cidr_bits <= 32:
                return ''
        except ValueError:
            return ''

        netmask = ''
        for idx in range(4):
            if idx:
                netmask += '.'
            if cidr_bits >= 8:
                netmask += '255'
                cidr_bits -= 8
            else:
                netmask += '{0:d}'.format(256 - (2 ** (8 - cidr_bits)))
                cidr_bits = 0
        return netmask

    def _number_of_set_bits(self, x):
        '''
        Returns the number of bits that are set in a 32bit int
        '''
        # Taken from http://stackoverflow.com/a/4912729. Many thanks!
        x -= (x >> 1) & 0x55555555
        x = ((x >> 2) & 0x33333333) + (x & 0x33333333)
        x = ((x >> 4) + x) & 0x0f0f0f0f
        x += x >> 8
        x += x >> 16
        return x & 0x0000003f

    def _interfaces_ip(self, out):
        '''
        Uses ip to return a dictionary of interfaces with various information about
        each (up/down state, ip address, netmask, and hwaddr)
        '''
        ret = dict()
        right_keys = ['name', 'hwaddr', 'up', 'netmask', 'ipaddrs']

        def parse_network(value, cols):
            '''
            Return a tuple of ip, netmask, broadcast
            based on the current set of cols
            '''
            brd = None
            if '/' in value:  # we have a CIDR in this address
                ip, cidr = value.split('/')  # pylint: disable=C0103
            else:
                ip = value  # pylint: disable=C0103
                cidr = 32

            if type_ == 'inet':
                mask = self.cidr_to_ipv4_netmask(int(cidr))
                if 'brd' in cols:
                    brd = cols[cols.index('brd') + 1]
            return (ip, mask, brd)

        groups = re.compile('\r?\n\\d').split(out)
        for group in groups:
            iface = None
            data = dict()

            for line in group.splitlines():
                if ' ' not in line:
                    continue
                match = re.match(r'^\d*:\s+([\w.\-]+)(?:@)?([\w.\-]+)?:\s+<(.+)>', line)
                if match:
                    iface, parent, attrs = match.groups()
                    if 'UP' in attrs.split(','):
                        data['up'] = True
                    else:
                        data['up'] = False
                    if parent and parent in right_keys:
                        data[parent] = parent
                    continue

                cols = line.split()
                if len(cols) >= 2:
                    type_, value = tuple(cols[0:2])

                    iflabel = cols[-1:][0]
                    if type_ in ('inet',):
                        if 'secondary' not in cols:
                            ipaddr, netmask, broadcast = parse_network(value, cols)
                            if type_ == 'inet':
                                if 'inet' not in data:
                                    data['inet'] = list()
                                addr_obj = dict()
                                addr_obj['address'] = ipaddr
                                addr_obj['netmask'] = netmask
                                addr_obj['broadcast'] = broadcast
                                data['inet'].append(addr_obj)
                        else:
                            if 'secondary' not in data:
                                data['secondary'] = list()
                            ip_, mask, brd = parse_network(value, cols)
                            data['secondary'].append({
                                'type': type_,
                                'address': ip_,
                                'netmask': mask,
                                'broadcast': brd,
                            })
                            del ip_, mask, brd
                    elif type_.startswith('link'):
                        data['hwaddr'] = value
            if iface:
                if iface.startswith('pan') or iface.startswith('lo') or iface.startswith('v'):
                    del iface, data
                else:
                    ret[iface] = data
                    del iface, data
        return ret

    def standard(self, interfaces_info):

        for key, value in interfaces_info.items():
            ipaddrs = set()
            netmask = set()
            if not 'inet' in value:
                value['ipaddrs'] = ''
                value['netmask'] = ''
            else:
                for item in value['inet']:
                    ipaddrs.add(item['address'])
                    netmask.add(item['netmask'])
                value['ipaddrs'] = '/'.join(ipaddrs)
                value['netmask'] = '/'.join(netmask)
                del value['inet']
                
    def win(self,cmd_func,test):
        import wmi
        info_dic = {}
        c = wmi.WMI()
        # 获取MAC和IP地址
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=1):
            interface_info = {}
            interface_info['hwaddr'] = interface.MACAddress
            interface_info['netmask'] = interface.IPSubnet[0]
            interface_info['ipaddrs'] = interface.IPAddress[0]
            interface_info['up'] = True
            info_dic[interface.Description] = interface_info

        return info_dic
'''
{'_associated_classes': None,
 'methods': {
     u'EnableIPSec': None,
     u'SetDNSServerSearchOrder': None,
     u'SetWINSServer': None,
     u'SetIPUseZeroBroadcast': None,
     u'SetNumForwardPackets': None,
     u'SetIGMPLevel': None,
     u'SetKeepAliveTime': None,
     u'SetArpAlwaysSourceRoute': None,
     u'SetTcpMaxConnectRetransmissions': None,
     u'SetTcpNumConnections': None,
     u'SetDefaultTOS': None,
     u'SetArpUseEtherSNAP': None,
     u'SetPMTUBHDetect': None,
     u'SetTcpWindowSize': None,
     u'EnableStatic': None,
     u'SetDNSDomain': None,
     u'RenewDHCPLeaseAll': None,
     u'SetIPConnectionMetric': None,
     u'ReleaseDHCPLeaseAll': None,
     u'SetPMTUDiscovery': None,
     u'SetTcpipNetbios': None,
     u'SetTcpUseRFC1122UrgentPointer': None,
     u'SetGateways': None,
     u'RenewDHCPLease': None,
     u'DisableIPSec': None,
     u'SetIPXVirtualNetworkNumber': None,
     u'SetDNSSuffixSearchOrder': None,
     u'SetDeadGWDetect': None,
     u'SetDefaultTTL': None,
     u'EnableWINS': None,
     u'SetTcpMaxDataRetransmissions': None,
     u'SetDatabasePath': None,
     u'SetIPXFrameTypeNetworkPairs': None,
     u'ReleaseDHCPLease': None,
     u'SetKeepAliveInterval': None,
     u'SetMTU': None,
     u'EnableDHCP': None,
     u'SetForwardBufferMemory': None,
     u'EnableIPFilterSec': None,
     u'EnableDNS': None,
     u'SetDynamicDNSRegistration': None},
 'property_map': {},
 'properties': {
     u'DHCPLeaseObtained': None,
     u'Index': None,
     u'NumForwardPackets': None,
     u'TcpMaxDataRetransmissions': None,
     u'DomainDNSRegistrationEnabled': None,
     u'DatabasePath': None,
     u'IPSecPermitUDPPorts': None,
     u'WINSHostLookupFile': None,
     u'IPXEnabled': None,
     u'TcpWindowSize': None,
     u'InterfaceIndex': None,
     u'IPUseZeroBroadcast': None,
     u'GatewayCostMetric': None,
     u'DHCPLeaseExpires': None,
     u'TcpipNetbiosOptions': None,
     u'DNSServerSearchOrder': None,
     u'Description': None,
     u'TcpNumConnections': None,
     u'WINSEnableLMHostsLookup': None,
     u'IPFilterSecurityEnabled': None,
     u'WINSScopeID': None,
     u'DeadGWDetectEnabled': None,
     u'IPXFrameType': None,
     u'TcpMaxConnectRetransmissions': None,
     u'ArpAlwaysSourceRoute': None,
     u'IPSecPermitTCPPorts': None,
     u'IPAddress': None,
     u'DHCPEnabled': None,
     u'PMTUBHDetectEnabled': None,
     u'DNSDomain': None,
     u'IPXMediaType': None,
     u'KeepAliveInterval': None,
     u'PMTUDiscoveryEnabled': None,
     u'DefaultIPGateway': None,
     u'MTU': None,
     u'Caption': None,
     u'SettingID': None,
     u'ServiceName': None,
     u'ForwardBufferMemory': None,
     u'FullDNSRegistrationEnabled': None,
     u'IPSubnet': None,
     u'TcpUseRFC1122UrgentPointer': None,
     u'MACAddress': None,
     u'ArpUseEtherSNAP': None,
     u'DNSEnabledForWINSResolution': None,
     u'IPConnectionMetric': None,
     u'IPXAddress': None,
     u'IGMPLevel': None,
     u'IPSecPermitIPProtocols': None,
     u'KeepAliveTime': None,
     u'DNSHostName': None,
     u'IPXVirtualNetNumber': None,
     u'DNSDomainSuffixSearchOrder': None,
     u'WINSSecondaryServer': None,
     u'DefaultTOS': None,
     u'IPXNetworkNumber': None,
     u'IPEnabled': None,
     u'IPPortSecurityEnabled': None,
     u'DefaultTTL': None,
     u'WINSPrimaryServer': None,
     u'DHCPServer': None},
 '_keys': None,
 }'''