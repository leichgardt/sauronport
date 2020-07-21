import os
import sys
import time
from datetime import timedelta

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../'))

from api.pysnmpcore import PySNMPCore
from api.pysnmp_parameters import *
from api.config import Configer

cfg = Configer().upload(module='PySNMP')
IP_BLACK_LIST = cfg('ip_black_list', [])
del cfg


class PySNMPApi(PySNMPCore):

    """
    Класс с методами для запроса различных данных со свичей. Предназначен для web-приложения SauronPort
    """

    def __init__(self):
        super().__init__()

        self._port_link = ''
        self._port_status = ''

    def get_sysdescr(self, ip):
        return self._snmp_pretty(self.snmp_cmd('get', ip, 'sysDescr', 'SNMPv2-MIB', attrib=0))

    def get_sysname(self, ip):
        return self._snmp_pretty(self.snmp_cmd('get', ip, 'sysName', 'SNMPv2-MIB', attrib=0))

    def get_syslocation(self, ip):
        rez = self._snmp_pretty(self.snmp_cmd('get', ip, 'sysLocation', 'SNMPv2-MIB', attrib=0))
        if rez is '' or rez is -1:
            return 'n/a'
        else:
            return rez.strip()

    def get_sysuptime(self, ip):
        return str(timedelta(seconds=(int(
            self._snmp_pretty(self.snmp_cmd('get', ip, 'sysUpTime', 'SNMPv2-MIB', attrib=0))) / 100))).split('.')[0]

    def get_port_status(self, ip, port):
        """Возвращает статус порта: административно включен/выключен"""
        varBind = self.snmp_cmd('get', ip, 'ifAdminStatus', 'IF-MIB', attrib=port)
        if varBind != -1:
            self._port_status = self._snmp_pretty(varBind)
            if self._port_status == 'up':
                return 1
            elif self._port_status == 'down':
                return 2
            else:
                return self._port_status
        else:
            return 'n/a'

    def get_port_link(self, ip, port):
        """
        Возвращает статус соединения порта:
        Статусы: 1-up, 2-down, 3-testing, 4-unknown, 5-dormant, 6-notPresent, 7-lowerLayerDown.
        """
        varBinds = self.snmp_cmd('get', ip, 'ifOperStatus', 'IF-MIB', attrib=port)

        if varBinds != -1:
            rez = self._snmp_pretty(varBinds)
            if rez is '1':
                self._port_link = 'up'
            elif rez is '2':
                self._port_link = 'down'
            elif rez is '3':
                self._port_link = 'testing'
            elif rez is '4':
                self._port_link = 'unknown'
            elif rez is '5':
                self._port_link = 'dormant'
            elif rez is '6':
                self._port_link = 'notPresent'
            elif rez is '7':
                self._port_link = 'lowerLayerDown'
            elif rez is -1:
                self._port_link = 'noResponse'
            else:
                self._port_link = rez
            return self._port_link
        else:
            return 'n/a'

    def get_port_speed(self, ip, port):
        """Возвращает скорость порта в Mbit/sec или Gbit/sec"""
        if self._port_link is '':
            self.get_port_link(ip, port)
        if self._port_link is 'noResponse':
            return 'n/a'
        else:
            varBind = self.snmp_cmd('get', ip, 'ifSpeed', 'IF-MIB', attrib=port)
            try:
                if varBind != -1:
                    rez = self._snmp_pretty(varBind)
                    if isinstance(rez, str):
                        rez = rez.replace(' ', '')
                    if int(rez) % 1000000000 == 0:
                        return str(int(rez) / 1000000000) + ' Gbit/s'
                    else:
                        return str(int(rez) / 1000000) + ' Mbit/s'
                else:
                    return 'n/a'
            except Exception as e:
                print("get_port_speed error:", e)
                return 'n/a'

    def get_port_mac(self, ip, port):
        """Возвращает таблицу MAC-адресов и их VLAN на порту"""
        varTable = self.snmp_cmd('walk', ip, 'dot1qTpFdbPort', 'Q-BRIDGE-MIB')
        if varTable is not -1:
            macs = []
            vlans = []
            for varBinds in varTable:
                try:
                    if int(varBinds[1]) == int(port):
                        varBind = self._snmp_pretty(varBinds[0], '.', False)
                        vlans.append(int(varBind[1]))
                        macs.append(str(varBind[2][1:-1]))
                except ValueError:
                    continue
            return vlans, macs
        else:
            return ['n/a'], ['n/a']

    def get_errors(self, ip, port):
        """
        Возвращает количество ошибок на порту.
        RX Frames:                  TX Frames:
            1 - CRC Error               1 - Excessive Deferral
            2 - Undersize               2 - Late Collision
            3 - Oversize                3 - Excessive Collision
            4 - Fragment                4 - Single Collision
            5 - Jabber
            6 - Drop Events
            7 - Symbol Error
        """
        rx_frames = {'CRC Error': '',
                     'Undersize': '',
                     'Oversize': '',
                     'Fragments': '',
                     'Jabbers': '',
                     'Drop Events': '',
                     'Symbol Error': ''}
        tx_frames = {'Excessive Deferral': '',
                     'Late Collision': '',
                     'Excessive Collision': '',
                     'Single Collision': ''}
        for error in ERRORS_DICT:
            rez = self._snmp_pretty(self.snmp_cmd('get', ip, error['OID'], error['MIB'], attrib=port))
            if rez in ['timeout', -1]:
                break
            else:
                if error['name'] in rx_frames.keys():
                    rx_frames[error['name']] = rez
                else:
                    tx_frames[error['name']] = rez
        return rx_frames, tx_frames

    def get_update(self, ip, port):
        """Запрос всех данных о порте кроме ошибок"""
        status = self.get_port_status(ip, port)
        link = self.get_port_link(ip, port)
        speed = self.get_port_speed(ip, port)
        vlans, macs = self.get_port_mac(ip, port)
        return status, link, speed, vlans, macs

    def turn_port(self, ip, port, stat):
        """Установить административный статус порту"""
        return self.snmp_cmd('set', ip, 'ifAdminStatus', 'IF-MIB', attrib=port, value=int(stat), private=True)

    def hex_vlan_port_parser(self, port_list):
        """
        Метод парсит принадлежность VLAN-ов к портам. Ответ SNMP выдается в шестнадцатиричном виде. Значения в ответе
        являются побитовым перечислением портов (например, 0xF0F0 - 11110000 11110000 - означает, что порты 1-4 и 9-12
        принадлежат определенному VLAN).
        http://xcme.blogspot.com/2014/10/vlan-snmp.html
        """
        common_list = {}
        for lane in port_list:
            vlan, hex_port_list = self._snmp_pretty(lane, last=False)

            bin_list = ''
            ports = []
            hex_len = len(hex_port_list)
            for i in range(2, hex_len, 2):
                hex_part = hex_port_list[i:i+2]
                bin_list += bin(int(hex_part, 16))[2:].zfill(8)
            for i, b in enumerate(bin_list):
                if b is '1':
                    ports.append(i + 1)
            common_list.update({vlan.split('.')[-1]: ports})
        return common_list

    def vlan_tag_check(self, ip, port):
        """
        Проверка порта - есть ли в нем Tagged VLAN. Две OID: один для получения всех VLAN, второй - все
        Untagged VLANs. Из всех VLANs вычитается Untagged, как результат - список Tagged VLAN остается.
        """
        try:
            vlans = self.snmp_cmd('walk', ip, 'dot1qVlanStaticEgressPorts', 'Q-BRIDGE-MIB')
            untag_vlans = self.snmp_cmd('walk', ip, 'dot1qVlanStaticUntaggedPorts', 'Q-BRIDGE-MIB')

            if vlans is -1 or untag_vlans is -1:
                raise Exception('[vlan_tag_check] error')

            vlans = self.hex_vlan_port_parser(vlans)
            untag_vlans = self.hex_vlan_port_parser(untag_vlans)

            if len(vlans) != len(untag_vlans):
                raise Exception('[vlan_tag_check] length error')
            else:
                tagged_ports = []
                for key, value in vlans.items():
                    value = list(set(value) - set(untag_vlans[key]))
                    for vport in value:
                        if vport not in tagged_ports:
                            tagged_ports.append(vport)
                return True if port in tagged_ports else False
        except Exception as e:
            print('[vlan_tag_check] Error:', e)

    def reload_port(self, ip, port, mode):
        """Метод перезапуска/выключения порта"""
        if self.vlan_tag_check(ip, port) or ip in IP_BLACK_LIST:
            return -1
        else:
            if mode == 1:  # reload
                self.turn_port(ip, port, 2)
                time.sleep(0.5)
                self.turn_port(ip, port, 1)
                print(f'port {port} turned on')
                return 1
            elif mode == 2:  # disable
                self.turn_port(ip, port, 2)
                print(f'port {port} turned off')
                time.sleep(0.5)
                return 1
            else:
                return 0


if __name__ == "__main__":
    ip, port = '192.168.111.60', 3
    snmp = PySNMPApi()
    # [print(line) for line in snmp.get_update(ip, port)]
    # snmp.get_port_mac(ip, port)
    # print(snmp.snmp_cmd('get', '192.168.111.60', '1.3.6.1.2.1.2.2.1.7.' + str(port))[0])
    # snmp.snmp_cmd('set', '192.168.111.60', '1.3.6.1.2.1.2.2.1.7', value=2, private=True)
    # print(snmp.snmp_cmd('get', '192.168.111.60', 'fileIPaddress', 'SNR-SWITCH-MIB', attrib=0, private=True, load=True))
    print(snmp.snmp_cmd('get', '192.168.111.60', 'fileIPaddress', 'SNR-SWITCH_private_2.1.75', attrib=0, private=True, load=True))
    # print(snmp.snmp_cmd('get', '192.168.111.60', 'fileIPaddress', 'SNR-ERD-3s', attrib=0, private=True, load=True))
    # print(snmp.snmp_cmd('get', '192.168.111.60', 'fileIPaddress', 'SNR-ERD-4', attrib=0, private=True, load=True))
