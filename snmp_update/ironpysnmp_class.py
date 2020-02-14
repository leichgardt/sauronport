from pysnmp.hlapi import *
from datetime import timedelta


class IronSNMP:
    """docstring"""

    def __init__(self, community='public', version='v2c'):
        self.__versions = {'v1': 0,
                           'v2c': 1}

        self.COMMUNITY = community
        self.__ENGINE = SnmpEngine()
        self.__COMMUNITY_DATA = CommunityData(self.COMMUNITY, mpModel=self.__versions[version])
        self.__CONTEXT_DATA = ContextData()

    def _snmp_get_next(self, ip, oid, mib=''):
        ObjId = ObjectIdentity(oid) if mib is '' else ObjectIdentity(mib, oid)
        try:
            (errInd,
             errStat,
             errId,
             varBinds) = next(getCmd(self.__ENGINE,
                                     self.__COMMUNITY_DATA,
                                     UdpTransportTarget((ip, 161), timeout=2.0, retries=0),
                                     self.__CONTEXT_DATA,
                                     ObjectType(ObjId)))
            if errInd or errStat:
                print('ERROR! Ind:{0} Stat:{1} ID:{2} from getCmd into snmp_get_next\n'.format(errInd, errStat, errId))
                return 0
            else:
                return varBinds
        except Exception as e:
            print("snmp_get_next: GetCmd exception:\n{0}\n".format(e))
            return 0

    def _snmp_get_bulk(self, ip, oid, mib=''):
        ObjId = ObjectIdentity(oid) if mib is '' else ObjectIdentity(mib, oid)
        rez = []
        try:
            for (errInd,
                 errStat,
                 errId,
                 varT) in bulkCmd(self.__ENGINE,
                                  self.__COMMUNITY_DATA,
                                  UdpTransportTarget((ip, 161), timeout=10.0, retries=5),
                                  self.__CONTEXT_DATA,
                                  0, 25,
                                  ObjectType(ObjId),
                                  lexicographicMode=False):
                if errInd or errStat:
                    print('ERROR! Ind:{0} Stat:{1} ID:{2} from getCmd into snmp_get_next\n'.format(errInd, errStat,
                                                                                                   errId))
                    return 0
                else:
                    for varL in varT:
                        rez.append(varL)
            return rez
        except Exception as e:
            print("snmp_get_bulk: BulkCmd exception:\n{0}\n".format(e))
            return 0

    def _snmp_pretty(self, obj, split_by=' = ', last=True):
        return obj[0].prettyPrint().split(split_by)[-1] if last else obj.prettyPrint().split(split_by)

    def get_port_status(self, ip, port):
        varBinds = self._snmp_get_next(ip, '1.3.6.1.2.1.2.2.1.8.' + str(port))
        if varBinds is not 0:
            rez = self._snmp_pretty(varBinds)
            if '1' in rez:
                return 'up'
            elif '2' in rez:
                return 'down'
            elif '3' in rez:
                return 'testing'
            elif '4' in rez:
                return 'unknown'
            elif '5' in rez:
                return 'dormant'
            elif '6' in rez:
                return 'notPresent'
            elif '7' in rez:
                return 'lowerLayerDown'
            else:
                return rez
        else:
            print('GET_PORT_STATUS: snmp_get_next error: the answer is empty.')
            return 0

    def get_port_speed(self, ip, port):
        varBind = self._snmp_get_next(ip, '1.3.6.1.2.1.2.2.1.5.' + str(port))
        if varBind is not 0:
            rez = self._snmp_pretty(varBind).replace(' ', '')
            return str(int(rez) / 1000000) + ' Mbit/s'
        else:
            print('GET_PORT_SPEED: snmp_get_next error: the answer is empty.')
            return 0

    def get_port_mac(self, ip, port):
        macs = []
        vlans = []
        varTable = self._snmp_get_bulk(ip, 'dot1qTpFdbPort', 'Q-BRIDGE-MIB')
        if varTable is not 0:
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
            print('GET_PORT_MAC: snmp_get_bulk error: the answer is empty.')
            return 0, 0

    def get_sysdescr(self, ip):
        return self._snmp_pretty(self._snmp_get_bulk(ip, 'sysDescr', 'SNMPv2-MIB'))

    def get_sysname(self, ip):
        return self._snmp_pretty(self._snmp_get_bulk(ip, 'sysName', 'SNMPv2-MIB'))

    def get_location(self, ip):
        return self._snmp_pretty(self._snmp_get_bulk(ip, 'sysLocation', 'SNMPv2-MIB'))

    def get_errors(self, ip, port):
        rx_frames = {'CRC Error': -1,
                     'Undersize': -1,
                     'Oversize': -1,
                     'Fragments': -1,
                     'Jabbers': -1,
                     'Drop Events': -1,
                     'Symbol Error': -1}
        tx_frames = {'Excessive Deferral': -1,
                     'CRC Error': -1,
                     'Late Collision': -1,
                     'Excessive Collision': -1,
                     'Single Collision': -1,
                     'Collision': -1}
        varTable1 = self._snmp_get_bulk(ip, 'etherStatsEntry', 'RMON-MIB')
        varTable2 = self._snmp_get_bulk(ip, 'dot3StatsEntry', 'EtherLike-MIB')
        if varTable1 is not 0 and varTable2 is not 0:
            for varBinds in varTable1:
                varBind = self._snmp_pretty(varBinds, last=False)
                if '.' + str(port) in varBind[0][-4:]:
                    if 'etherStatsCRCAlignErrors' in varBind[0]:
                        rx_frames['CRC Error'] = varBind[1]
                    elif 'Undersize' in varBind[0]:
                        rx_frames['Undersize'] = varBind[1]
                    elif 'Oversize' in varBind[0]:
                        rx_frames['Oversize'] = varBind[1]
                    elif 'Fragments' in varBind[0]:
                        rx_frames['Fragments'] = varBind[1]
                    elif 'Jabbers' in varBind[0]:
                        rx_frames['Jabbers'] = varBind[1]
                    elif 'Drop' in varBind[0]:
                        rx_frames['Drop Events'] = varBind[1]
                    elif 'Collisions' in varBind[0]:
                        tx_frames['Collision'] = varBind[1]
            for varBinds in varTable2:
                varBind = self._snmp_pretty(varBinds, last=False)
                if '.' + str(port) in varBind[0][-4:]:
                    if 'Single' in varBind[0]:
                        tx_frames['Single Collision'] = varBind[1]
                    elif 'Deferred' in varBind[0]:
                        tx_frames['Excessive Deferral'] = varBind[1]
                    elif 'Late' in varBind[0]:
                        tx_frames['Late Collision'] = varBind[1]
                    elif 'Excessive' in varBind[0]:
                        tx_frames['Excessive Collision'] = varBind[1]
                    elif 'Symbol' in varBind[0]:
                        rx_frames['Symbol Error'] = varBind[1]
            return rx_frames, tx_frames

    def get_sysuptime(self, ip):
        return str(
            timedelta(seconds=(int(self._snmp_pretty(self._snmp_get_bulk(ip, 'sysUpTime', 'SNMPv2-MIB'))) / 100)))

    def get_all_data(self, ip, port):
        sysname = self.get_sysname(ip)
        sysloc = self.get_location(ip)
        sysuptime = self.get_sysuptime(ip)
        status = self.get_port_status(ip, port)
        speed = self.get_port_speed(ip, port)
        rx, tx = self.get_errors(ip, port)
        vlans, macs = self.get_port_mac(ip, port)
        return sysname, sysloc, sysuptime, status, speed, rx, tx, vlans, macs

    def get_update(self, ip, port):
        status = self.get_port_status(ip, port)
        speed = self.get_port_speed(ip, port)
        vlans, macs = self.get_port_mac(ip, port)
        return status, speed, vlans, macs


if __name__ == '__main__':
    from datetime import datetime, timedelta
    from snmp_update.ironpysnmp import *

    ip, port = '192.168.111.29', 3

    snmp = IronSNMP()
    print(timedelta(seconds=(int(snmp._snmp_pretty(snmp._snmp_get_bulk(ip, 'sysUpTime', 'SNMPv2-MIB'))) / 100)))
    # uptime = int(snmp._snmp_pretty(snmp._snmp_get_bulk(ip, 'sysUpTime', 'SNMPv2-MIB'))) / 100
    # uptime = str(timedelta(seconds=uptime))
    print(snmp.get_sysuptime(ip))  # 2112307 988146500
