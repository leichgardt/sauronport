from pysnmp.hlapi import *
from datetime import timedelta, datetime
from api.iron_pysnmp_parameters import *
import time


class IronSNMP:

    """docstring"""

    def __init__(self, community='public', version='v2c'):
        """

        --version - Using v2c at mpModel=1. "mpMpdel=0" is a v1.
        Community is access level of request.
        """
        self.__versions = {'v1': 0,
                           'v2c': 1}
        self.COMMUNITY = community
        self.__ENGINE = SnmpEngine()
        self.__CONTEXT_DATA = ContextData()
        self.__VERSION = version
        self.__COMMUNITY_DATA = CommunityData(self.COMMUNITY,
                                              mpModel=self.__versions[self.__VERSION])
        self._port_link = ''
        self._port_status = ''

    def private_community(func):
        def warper(self, *args):
            self.__COMMUNITY_DATA = CommunityData('private',
                                                  mpModel=self.__versions[self.__VERSION])
            answer = func(self, *args)
            self.__COMMUNITY_DATA = CommunityData('public',
                                                  mpModel=self.__versions[self.__VERSION])
            return answer
        return warper

    def _snmp_cmd(self, cmd, ip, oid, mib='', attrib=-1, arg=None, load=False):
        """
        SNMP request method.

        cmd:    get
                walk
                set
        oid:    can be indicated as OID or as Nom but with MIB
        attrib: attribute for OID that indicate parameter
        arg:    argument for 'snmp_set' command
        """

        if mib is '':
            ObjId = ObjectIdentity(oid)
        elif mib is not '' and attrib is -1:
            ObjId = ObjectIdentity(mib, oid)
        else:
            ObjId = ObjectIdentity(mib, oid, attrib)

        if arg is None:
            ObjType = ObjectType(ObjId)
        else:
            ObjType = ObjectType(ObjId, arg)

        if load:
            ObjId.addAsn1MibSource('http://mibs.snmplabs.com/asn1/@mib@')

        """
        ports: 161 - UDP port
               162 - Traps port
        """
        if cmd is 'get':
            snmp_cmd = getCmd(self.__ENGINE,
                              self.__COMMUNITY_DATA,
                              UdpTransportTarget((ip, 161), timeout=1.0, retries=1),
                              self.__CONTEXT_DATA,
                              ObjType)
        elif cmd is 'walk':
            snmp_cmd = bulkCmd(self.__ENGINE,
                               self.__COMMUNITY_DATA,
                               UdpTransportTarget((ip, 161), timeout=1.0, retries=1),
                               self.__CONTEXT_DATA,
                               0, 25,  # nonRepeaters / maxRepetitions - MIB num are requesting
                               ObjType,
                               lexicographicMode=False)
        elif cmd is 'set':
            snmp_cmd = setCmd(self.__ENGINE,
                              self.__COMMUNITY_DATA,
                              UdpTransportTarget((ip, 161), timeout=1.0, retries=1),
                              self.__CONTEXT_DATA,
                              ObjType)

        try:
            if cmd is 'walk':
                rez = []
                for (errInd, errStat, errId, varBinds) in snmp_cmd:
                    if errInd or errStat or errId:
                        print(f'[snmp_{cmd}]: ',
                              errInd if errInd else '',
                              errStat if errStat else '',
                              errId if errId else '')
                        return -1
                    else:
                        for varBind in varBinds:
                            rez.append(varBind)
            else:
                (errInd, errStat, errId, varBinds) = next(snmp_cmd)
                if errInd or errStat or errId:
                    print(f'[snmp_{cmd}]: ',
                          errInd if errInd else '',
                          errStat if errStat else '',
                          errId if errId else '')
                    return -1
                else:
                    rez = varBinds
            if self._snmp_correct_oid(rez):
                return rez
            else:
                return -1
        except Exception as e:
            print(f"[snmp_{cmd}]: Exception:\n{e}\n")
            return -1

    def _snmp_correct_oid(self, obj):
        try:
            if 'No Such Instance' in self._snmp_pretty(obj) or 'No Such Object' in self._snmp_pretty(obj):
                return False
            else:
                return True
        except TypeError:
            return True

    def _snmp_pretty(self, obj, split_by=' = ', last=True):
        if isinstance(obj, str):
            return obj
        elif obj is -1:
            return -1
        else:
            if last:
                rez = obj[0].prettyPrint().split(split_by)[-1]
                if 'No Such Instance' in rez or 'No Such Object' in rez:
                    return -1
                else:
                    return rez
            else:
                return obj.prettyPrint().split(split_by)

    def get_sysdescr(self, ip):
        return self._snmp_pretty(self._snmp_cmd('walk', ip, 'sysDescr', 'SNMPv2-MIB'))

    def get_sysname(self, ip):
        return self._snmp_pretty(self._snmp_cmd('walk', ip, 'sysName', 'SNMPv2-MIB'))

    def get_syslocation(self, ip):
        rez = self._snmp_pretty(self._snmp_cmd('walk', ip, 'sysLocation', 'SNMPv2-MIB'))
        if rez is '' or rez is -1:
            return 'n/a'
        else:
            return rez.strip()

    def get_sysuptime(self, ip):
        return str(timedelta(seconds=(int(
            self._snmp_pretty(self._snmp_cmd('walk', ip, 'sysUpTime', 'SNMPv2-MIB'))) / 100))).split('.')[0]

    def get_port_status(self, ip, port):
        varBind = self._snmp_cmd('get', ip, 'ifAdminStatus', 'IF-MIB', port)
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
        Getting a port status at router port x
        Status: 1-up, 2-down, 3-testing, 4-unknown, 5-dormant, 6-notPresent, 7-lowerLayerDown.
        Using a function snmp_get_next::getCmd for pulling out a one parameter.
        """
        varBinds = self._snmp_cmd('get', ip, 'ifOperStatus', 'IF-MIB', port)

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
        """
        Getting a port speed at router port x
        Answer shown as a bit/sec bandwidth, that's why output must be need to translated to Mbit/sec to readability.
        Using a function snmp_get_next::getCmd for pulling out a one parameter.
        """
        if self._port_link is '':
            self.get_port_link(ip, port)
        if self._port_link is 'noResponse':
            return 'n/a'
        else:
            varBind = self._snmp_cmd('get', ip, 'ifSpeed', 'IF-MIB', port)
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
        """
        Getting a table with MACs and their ports with VLAN.
        ObjName: "dot1qTpFdbPort", MID: "Q-BRIDGE-MIB".
        Using a function snmp_get_next::getBulk for pulling out many parameters.
        """
        varTable = self._snmp_cmd('walk', ip, 'dot1qTpFdbPort', 'Q-BRIDGE-MIB')
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
        RX Frames:                  TX Frames:
            1 - CRC Error               1 - Excessive Deferral
            2 - Undersize               2 - Late Collision
            3 - Oversize                3 - Excessive Collision
            4 - Fragment                4 - Single Collision
            5 - Jabber                  5 - Collision
            6 - Drop Pkts
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
        for error in errors_dict:
            rez = self._snmp_pretty(self._snmp_cmd('get', ip, error['OID'], error['MIB'], port))
            if rez is 'timeout' or rez is -1:
                break
            else:
                if error['name'] in rx_frames.keys():
                    rx_frames[error['name']] = rez
                else:
                    tx_frames[error['name']] = rez

        return rx_frames, tx_frames

    def get_update(self, ip, port):
        status = self.get_port_status(ip, port)
        link = self.get_port_link(ip, port)
        speed = self.get_port_speed(ip, port)
        vlans, macs = self.get_port_mac(ip, port)
        return status, link, speed, vlans, macs

    @private_community
    def turn_port(self, ip, port, stat):
        try:
            self._snmp_cmd('set', ip, 'ifAdminStatus', 'IF-MIB', port, Integer(stat))
        except Exception as e:
            print('[turn_port] Error:', e)

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
        Метод для проверки порта - есть ли в нем Tagged VLAN. Две OID: один для получения всех VLAN, второй - все
        Untagged VLANs. Из всех VLANs вычитается Untagged, как результат - список Tagged VLAN.
        """
        try:
            vlans = self._snmp_cmd('walk', ip, 'dot1qVlanStaticEgressPorts', 'Q-BRIDGE-MIB')
            untag_vlans = self._snmp_cmd('walk', ip, 'dot1qVlanStaticUntaggedPorts', 'Q-BRIDGE-MIB')

            if vlans is -1 or untag_vlans is -1:
                raise Exception('[snmp_walk] -> [vlan_tag_check] error')

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
        if self.vlan_tag_check(ip, port) or ip in IP_BLACK_LIST:
            return -1
        else:
            if mode == 1:  # reload
                self.turn_port(ip, port, 2)
                self.turn_port(ip, port, 1)
                print(f'port {port} turned on')
                time.sleep(1)
                return 1
            elif mode == 2:  # disable
                self.turn_port(ip, port, 2)
                print(f'port {port} turned off')
                time.sleep(1)
                return 1
            return 0


if __name__ == '__main__':
    ip, port = '192.168.110.87', 3
    # 139, 4
    snmp = IronSNMP()
    snmp.vlan_tag_check(ip, port)
